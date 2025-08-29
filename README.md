
# 🌊 BeachSniffer

A retro ANSI-art visualization of home network traffic, running on a Raspberry Pi.

BeachSniffer listens to local WiFi packets and transforms them into a **colorful, animated beach scene**:

* 🌞 Sun pulsing with network load
* 🕊️ Seagulls flying with new TCP connections
* 🌊 Waves rolling with DNS lookups and bursts
* 🏖️ Sand shimmering with ARP/DHCP background chatter

The result is a **living ASCII painting** of my apartment’s network life.

---

## 🎯 Project Goals

* Create a **long-running visualization** that can sit on a Raspberry Pi in your living room.
* Use **only the console (tty1)** — no X server required.
* Combine **packet sniffing** with **retro ANSI art + animation**.
* Provide both **artistic aesthetics** and **insight into local network behavior**.

---

## 🛠️ Tech Stack

* **Python 3** → the main language.
* **Scapy** → for packet sniffing (ARP, DNS, TCP, UDP, etc.).
* **Rich** → for colorful retro-style CLI graphics and animations.
* **systemd service** → to run on Raspberry Pi boot and display on HDMI without X server.

---

## 📡 Local Traffic in a Home Network

When you sniff WiFi in a typical apartment, you’ll see a mix of protocols:

* **ARP**:
  “Who has 192.168.1.5? Tell 192.168.1.1”
  Constant chatter as devices map IPs to MACs.

* **DNS**:
  Lookups every time someone visits a website.
  Lots of small bursts.

* **DHCP**:
  When devices join / renew IP leases.
  Occasional messages.

* **HTTP/HTTPS (TCP)**:
  Streaming, browsing, apps.
  Mostly encrypted TLS, but visible as packet sizes + bursts.

* **TCP handshakes (SYN, SYN-ACK, ACK)**:
  Every new connection (especially many when loading web pages).

* **UDP**:
  Used in gaming, streaming, DNS.
  Short bursts.

**In short:**

* Background noise: **ARP + DHCP**
* Frequent bursts: **DNS + TCP handshakes**
* Heavy flow: **HTTPS traffic**

---

## 🎨 Protocol → Scene Mapping

BeachSniffer translates protocols into elements of the scene:

* **ARP + DHCP** → 🏖️ **Sand shimmer** (the constant, subtle background noise).
* **DNS lookups** → 🌊 **Wave splashes** (short bursts across the water).
* **TCP handshakes** → 🕊️ **Seagulls fly across the sky** (new connections appearing).
* **HTTPS / heavy flows** → 🌞 **Sun pulses brighter** (more load = stronger glow).
* **UDP bursts** → ✨ **Sparkles on the water** (quick, scattered highlights).

This mapping makes the art **responsive to real activity** in your home network.

---

## 🚀 Running on Raspberry Pi

1. Clone the repo and install dependencies:

   ```bash
   pip install scapy rich
   ```
2. Enable WiFi monitor mode on your Pi (required for sniffing):

   ```bash
   sudo iwconfig wlan0 mode monitor
   ```
3. Run BeachSniffer:

   ```bash
   python beachsniffer.py
   ```
4. (Optional) Install as a `systemd` service to start at boot and display on HDMI automatically.

---

## 🌟 Future Ideas

* Different “themes” (forest, space, matrix) for different moods.
* Per-device visualization (your phone = one gull, your laptop = another).
* Sound effects tied to packets (waves crash louder when traffic is high).




