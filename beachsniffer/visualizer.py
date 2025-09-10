# visualizer.py
# Fun terminal packet visualizer with categories & ASCII flair

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"

COLORS = {
    "yellow": "\033[33m",
    "green": "\033[32m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "red": "\033[31m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "gray": "\033[90m",
}


def colorize(text, color="white", bold=False):
    return f"{BOLD if bold else ''}{COLORS.get(color, COLORS['white'])}{text}{RESET}"


def display_packet(packet):
    proto = packet.get("protocol", "").upper()
    src = packet.get("src", "N/A")
    dst = packet.get("dst", "N/A")
    info = ""

    # --- ARP ---
    if proto == "ARP":
        if packet.get("op") == 1:
            info = colorize(f"Who has {dst}? Asking for a friend :-)", "yellow")
        elif packet.get("op") == 2:
            info = colorize(f"{dst} lives at {packet.get('hwsrc', '??:??:??:??:??:??')} — mystery solved! \\o/", "green")
        else:
            info = colorize("Mysterious ARP business... (._.)", "gray")

    # --- DNS ---
    elif proto == "DNS":
        qname = packet.get("qname", "example.com")
        if packet.get("qr") == 0:
            info = colorize(f"Looking up {qname}... hope it’s not shady ;-)", "blue")
        elif packet.get("qr") == 1:
            ans = packet.get("ans", "???")
            info = colorize(f"{qname}? Yeah, that’s {ans} — don’t get lost! :-]", "magenta")
        else:
            info = colorize("DNS chatter... names and numbers doing a dance (._.)", "blue")

    # --- TCP ---
    elif proto == "TCP":
        flags = packet.get("flags", "")
        if "S" in flags and "A" not in flags:
            info = colorize(f"Do you want to be my friend? (SYN) :-)\n  {src} → {dst}", "red", bold=True)
        elif "S" in flags and "A" in flags:
            info = colorize(f"Yes, let’s be friends! (SYN-ACK)\n  {src} → {dst}", "yellow")
        elif flags == "A":
            info = colorize(f"Handshake complete, friendship secured! (ACK)\n  {src} ↔ {dst}", "white")
        elif "F" in flags:
            info = colorize(f"All good things come to an end (FIN)\n  {src} → {dst}", "gray")
        elif "R" in flags:
            info = colorize(f"Forget it, I’m out. (RST)\n  {src} → {dst}", "red")
        else:
            info = colorize(f"TCP doing TCP things — probably data streaming...\n  {src} ↔ {dst}", "white")

    # --- UDP ---
    elif proto == "UDP":
        info = colorize(f"Fast and loose: UDP at your service! ;-)\n  {src} → {dst}", "cyan")

    # --- ICMP ---
    elif proto == "ICMP":
        icmp_type = packet.get("type")
        if icmp_type == 8:
            info = colorize(f"Ping? Anybody there? (o_o)?\n  {src} → {dst}", "green")
        elif icmp_type == 0:
            info = colorize(f"Yes, I’m here! Pong! (^_^)v\n  {dst} ← {src}", "yellow")
        elif icmp_type == 3:
            info = colorize(f"Sorry, can’t reach {dst} — try again later. :-/", "red")
        else:
            info = colorize(f"ICMP noise — network gossip at its finest ;-)\n  {src} → {dst}", "magenta")

    # --- Generic IP ---
    elif proto == "IP":
        info = colorize(f"Plain old IP packet, nothing fancy to see here... (¬_¬)\n  {src} → {dst}", "white")

    # --- Unknown ---
    else:
        info = colorize(f"¯\\_(ツ)_/¯ A mystery packet wanders the wires...\n  {src} → {dst}", "gray")

    print(info)
