import time
from scapy.all import sniff
from .visualizer import display_packet

# flag for breaking event loop
stop_sniffing = False


def stop_filter(_):
    global stop_sniffing
    return stop_sniffing


def main():
    global stop_sniffing

    print("Starting packet sniffing... Ctrl+C to stop")

    try:
        while not stop_sniffing:
            # Capture a small batch
            packets = sniff(count=5, timeout=3, stop_filter=stop_filter)

            if packets:
                for pkt in packets:
                    # Extract minimal info manually
                    proto = pkt.sprintf("%IP.proto%") if pkt.haslayer("IP") else "Unknown"
                    src = getattr(pkt, "src", None)
                    dst = getattr(pkt, "dst", None)
                    size = len(pkt)

                    pkt_info = {
                        "src": src,
                        "dst": dst,
                        "protocol": proto,
                        "size": size,
                    }

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
