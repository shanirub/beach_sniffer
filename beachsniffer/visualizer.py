# visualizer.py

import random
import sys

def display_packet(packet_info: dict):
    """
    Show packet info (dict from sniffer) as sequential lines.
    """
    src = packet_info.get("src", "N/A")
    dst = packet_info.get("dst", "N/A")
    proto = packet_info.get("protocol", "Unknown")
    size = packet_info.get("size", 0)

    # ANSI colors for fun
    colors = [
        "\033[91m",  # red
        "\033[92m",  # green
        "\033[93m",  # yellow
        "\033[94m",  # blue
        "\033[95m",  # magenta
        "\033[96m",  # cyan
    ]
    reset = "\033[0m"
    color = random.choice(colors)

    # Print line by line, scrolling naturally
    print(f"{color}Beach Sniffer | Src: {src} | Dst: {dst} | Proto: {proto} | Size: {size} bytes{reset}")

    # Ensure immediate flush (so lines show up in real time)
    sys.stdout.flush()
