"""Packet sniffer producing high-level events for the visualizer.

- Uses scapy to sniff on a given interface (defaults to wlan0).
- Emits coarse protocol events via a thread-safe Queue.
- Keeps the parser intentionally lightweight so Python on a Pi 3B+ can cope.

Notes:
- WiFi sniffing of *all* traffic typically requires monitor mode.
  You can also run in normal mode to observe traffic to/from the Pi itself.
- Run with capabilities or sudo (CAP_NET_RAW / CAP_NET_ADMIN) if needed.
"""
from __future__ import annotations

import threading
import time
from queue import Queue
from typing import Optional

try:
    # scapy imports are a little heavy; import lazily in start()
    from scapy.all import sniff, ARP, BOOTP, DHCP, DNS, TCP, UDP
except Exception:  # pragma: no cover – scapy may not be available during static checks
    sniff = None  # type: ignore
    ARP = BOOTP = DHCP = DNS = TCP = UDP = object  # type: ignore

from . import events as E


class Sniffer:
    def __init__(self, event_queue: Queue, iface: str = "wlan0", bpf_filter: Optional[str] = None):
        self.q = event_queue
        self.iface = iface
        # A lean BPF filter to reduce Python work. Tunable.
        self.filter = bpf_filter or "arp or udp port 53 or tcp or udp"
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()

    def start(self):
        if sniff is None:
            raise RuntimeError("Scapy is not available. Install scapy: pip install scapy")
        self._thread = threading.Thread(target=self._run, name="BeachSniffer", daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 2.0):
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout)

    # --- internals ---
    def _run(self):
        # scapy sniff loop. We keep prn callback very small and do minimal attribute access.
        def on_pkt(pkt):
            # Fast path dispatch based on layers present
            try:
                now = time.time()
                if ARP in pkt:
                    self.q.put((E.ARP, now))
                    return
                if (BOOTP in pkt) or (DHCP in pkt):
                    self.q.put((E.DHCP, now))
                    return
                if DNS in pkt:
                    self.q.put((E.DNS, now))
                    return
                if UDP in pkt:
                    # DNS already caught above; treat remaining UDP as generic UDP
                    self.q.put((E.UDP, now))
                    return
                if TCP in pkt:
                    tcp = pkt[TCP]
                    flags = int(tcp.flags)
                    # Flag bits: 0x02 SYN, 0x10 ACK, 0x12 SYN-ACK
                    if flags & 0x02 and not (flags & 0x10):
                        self.q.put((E.TCP_SYN, now))
                    elif (flags & 0x12) == 0x12:
                        self.q.put((E.TCP_SYNACK, now))
                    elif (flags & 0x10) and not (flags & 0x02):
                        self.q.put((E.TCP_ACK, now))
                    # Heuristic: any packet to/from 443 increments TLS “load”
                    if getattr(tcp, "dport", None) == 443 or getattr(tcp, "sport", None) == 443:
                        self.q.put((E.TLS, now))
                    return
                # Fallback
                self.q.put((E.OTHER, now))
            except Exception:
                # We never want the callback to explode; drop on floor if needed
                pass

        # Use store=0 to avoid keeping packets in memory; count=0 for infinite; stop_filter checks flag
        sniff(
            iface=self.iface,
            filter=self.filter,
            prn=on_pkt,
            store=0,
            stop_filter=lambda _: self._stop.is_set(),
        )
