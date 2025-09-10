# main.py

import time
from .visualizer import display_packet
from .sniffer import packet_generator

# flag for breaking event loop
stop_sniffing = False


def main():
    global stop_sniffing

    iface = "wlan0"  # change this to your interface
    print(f"Starting packet sniffing on {iface}... Ctrl+C to stop")

    try:
        gen = packet_generator(iface)

        while not stop_sniffing:
            batch = []

            # collect a small batch of 5 packets or timeout after ~3 seconds
            start = time.time()
            while len(batch) < 5 and time.time() - start < 3:
                try:
                    pkt_info = next(gen)
                    if pkt_info:
                        batch.append(pkt_info)
                except StopIteration:
                    break

            if batch:
                for pkt_info in batch:
                    display_packet(pkt_info)
                    time.sleep(1)  # pause so you can see each one
            else:
                print("No packets captured in this cycle.")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected, stopping...")
        stop_sniffing = True

    print("Exiting gracefully.")


if __name__ == "__main__":
    main()
