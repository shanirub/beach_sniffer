import os
import random

def clear_screen():
    """Clear screen without extra packages."""
    os.system("clear")

def display_packet(packet_info: dict):
    """
    Show packet info (dict from sniffer) in a random screen position.
    """
    clear_screen()

    src = packet_info.get("src", "N/A")
    dst = packet_info.get("dst", "N/A")
    proto = packet_info.get("protocol", "Unknown")
    size = packet_info.get("size", 0)

    # Random positioning (basic terminal assumptions)
    rows, cols = 24, 80
    row = random.randint(0, rows - 6)
    col = random.randint(0, cols - 30)

    # ANSI colors
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

    # Move cursor and print
    print(f"\033[{row};{col}H{color}Beach Sniffer")
    print(f"\033[{row+1};{col}H{color}Src: {src}")
    print(f"\033[{row+2};{col}HDst: {dst}")
    print(f"\033[{row+3};{col}HProto: {proto}")
    print(f"\033[{row+4};{col}HSize: {size} bytes{reset}")
