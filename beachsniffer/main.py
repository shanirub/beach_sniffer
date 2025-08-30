"""Entrypoint for BeachSniffer.

Examples:
    python -m beachsniffer.main --iface wlan0 --fps 15

When run under systemd on a Pi without X, the output should go to tty1.
"""
from __future__ import annotations

import argparse
import signal
import sys
from queue import Queue

from rich.console import Console

from .sniffer import Sniffer
from .visualizer import BeachVisualizer


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="beachsniffer", description="Retro ANSI beach scene driven by network traffic")
    p.add_argument("--iface", default="wlan0", help="Network interface to sniff (default: wlan0)")
    p.add_argument("--fps", type=int, default=15, help="Frames per second for animation (default: 15)")
    p.add_argument("--filter", default=None, help="Optional BPF filter override")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    console = Console()
    q: Queue = Queue(maxsize=10000)

    # Start sniffer in background
    sniffer = Sniffer(q, iface=args.iface, bpf_filter=args.filter)
    try:
        sniffer.start()
    except Exception as e:
        console.print(f"[red]Failed to start sniffer:[/red] {e}")
        return 2

    # vis = BeachVisualizer(fps=args.fps)
    vis = BeachVisualizer(q=q, fps=args.fps)

    # Graceful shutdown on SIGTERM/SIGINT
    def handle_sig(_sig, _frm):
        sniffer.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    try:
        vis.run()
    except KeyboardInterrupt:
        pass
    finally:
        sniffer.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
