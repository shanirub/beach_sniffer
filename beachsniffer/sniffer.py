# sniffer.py
from scapy.all import sniff, IP, ARP, DNS, DNSQR, DNSRR, UDP, TCP, ICMP


def packet_callback(pkt):
    protocol = "OTHER"
    info = {}

    # --- ARP ---
    if ARP in pkt:
        protocol = "ARP"
        info["op"] = pkt[ARP].op  # 1=request, 2=reply
        info["hwsrc"] = pkt[ARP].hwsrc  # sender MAC

    # --- DNS ---
    elif DNS in pkt:
        protocol = "DNS"
        info["qr"] = pkt[DNS].qr  # 0=query, 1=response
        if pkt[DNS].qd and isinstance(pkt[DNS].qd, DNSQR):
            info["qname"] = pkt[DNS].qd.qname.decode(errors="ignore").strip(".")
        if pkt[DNS].an and isinstance(pkt[DNS].an, DNSRR):
            info["ans"] = pkt[DNS].an.rdata if hasattr(pkt[DNS].an, "rdata") else None

    # --- TCP ---
    elif TCP in pkt:
        protocol = "TCP"
        info["flags"] = pkt[TCP].flags.flagrepr()  # e.g. 'S', 'SA', 'A', 'F'

    # --- UDP ---
    elif UDP in pkt:
        protocol = "UDP"

    # --- ICMP ---
    elif ICMP in pkt:
        protocol = "ICMP"
        info["type"] = pkt[ICMP].type

    # --- IP fallback ---
    elif IP in pkt:
        protocol = "IP"

    # --- Source / Destination ---
    src = None
    dst = None
    if IP in pkt:
        src = pkt[IP].src
        dst = pkt[IP].dst
    elif ARP in pkt:
        src = pkt[ARP].psrc
        dst = pkt[ARP].pdst

    size = len(pkt)

    return {
        "src": src,
        "dst": dst,
        "size": size,
        "protocol": protocol,
        **info,  # merge protocol-specific fields
    }


def packet_generator(iface):
    """Yield parsed packet information continuously."""
    for pkt in sniff(iface=iface, store=False):
        info = packet_callback(pkt)
        if info:
            yield info
