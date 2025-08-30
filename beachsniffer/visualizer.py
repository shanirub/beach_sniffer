from __future__ import annotations

import os
import sys
import time
from queue import Queue, Empty

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text


class BeachVisualizer:
    """
    Renders a retro beach scene to the terminal, animated based on network traffic.
    """

    def __init__(self, fps: int = 15, q: Queue | None = None):
        self.console = Console()
        self.fps = fps
        self.q: Queue | None = q  # Queue with packets from Sniffer
        self.frame = 0
        self.last_packet_time = 0.0
        self.packet_count = 0
        self.max_packets_seen = 1  # prevent divide-by-zero

    def render_scene(self) -> Panel:
        """
        Render a single frame of the beach animation.
        The scene changes based on how much traffic is seen.
        """
        wave_chars = ["~", "-", "="]
        sun_chars = ["☼", "☀", "🌞"]

        # Activity level: higher when more packets
        now = time.time()
        if now - self.last_packet_time < 1.0:
            activity = min(1.0, self.packet_count / self.max_packets_seen)
        else:
            activity = 0.0

        # Pick a wave character based on activity
        wave = wave_chars[int(activity * (len(wave_chars) - 1))]
        sun = sun_chars[self.frame % len(sun_chars)]

        beach = []
        beach.append(" " * 10 + sun)
        beach.append(" " * 5 + wave * 20)
        beach.append(" " * 3 + "/" + " " * 18 + "\\")
        beach.append(" " * 2 + "/" + " " * 20 + "\\")
        beach.append("~" * 30)

        text = Text("\n".join(beach), justify="center")
        return Panel(text, title="🏖️ BeachSniffer", border_style="cyan")

    def process_packets(self) -> None:
        """
        Drain the packet queue and update traffic metrics.
        """
        if self.q is None:
            return
        drained = 0
        while True:
            try:
                _pkt = self.q.get_nowait()
                drained += 1
            except Empty:
                break
        if drained:
            self.packet_count = drained
            self.last_packet_time = time.time()
            if drained > self.max_packets_seen:
                self.max_packets_seen = drained

    def run(self) -> None:
        """
        Run the visualization loop until interrupted.
        """
        refresh_delay = 1.0 / self.fps
        with Live(self.render_scene(), refresh_per_second=self.fps, console=self.console) as live:
            while True:
                self.process_packets()
                live.update(self.render_scene())
                self.frame += 1
                time.sleep(refresh_delay)


# from rich.console import Console, Group
# from rich.live import Live
# from rich.text import Text
# from rich.style import Style
# import time
# import math
# import threading
#
# class BeachVisualizer:
#     def __init__(self, fps=15):
#         self.console = Console()
#         self.fps = fps
#         self._stop = threading.Event()
#         self.width = self.console.size.width
#         self.height = self.console.size.height
#         self.pulse = 0.0
#
#     def stop(self):
#         self._stop.set()
#
#     def _make_sky_line(self, y: int) -> Text:
#         """Return a single line of sky with sun pulse."""
#         line = []
#         # Simple pulsating sun effect at top-left corner
#         sun_color = 255 if y < 3 else 200
#         line.append(Text(" " * self.width, style=f"on rgb({sun_color}, {180 + int(self.pulse * 50)}, 255)"))
#         return Text("").join(line)
#
#     def _make_sand_line(self, y: int) -> Text:
#         """Return a single line of sand at the bottom."""
#         line = []
#         sand_color = 194 + int(self.pulse * 20)
#         line.append(Text(" " * self.width, style=f"on rgb({sand_color}, {178}, 128)"))
#         return Text("").join(line)
#
#     def _make_wave_line(self, y: int) -> Text:
#         """Return a line representing waves in front of sand."""
#         line = []
#         wave_color = 0, 105, 148
#         # simple sine wave pattern
#         wave_chars = ["~", "≈", "^", "~"]
#         chars = [wave_chars[(i + int(self.pulse * 5)) % len(wave_chars)] for i in range(self.width)]
#         line.append(Text("".join(chars), style=f"rgb{wave_color}"))
#         return Text("").join(line)
#
#     def _make_seagull_line(self, y: int) -> Text:
#         """Return a line with seagulls in sky (ASCII)."""
#         line = [" "] * self.width
#         for i in range(0, self.width, 20):
#             # simple flying pattern
#             bird = "v" if int(self.pulse * 5) % 2 == 0 else "^"
#             if i + int(self.pulse * 3) < self.width:
#                 line[i + int(self.pulse * 3)] = bird
#         return Text("".join(line), style="white")
#
#     def _compose(self) -> Group:
#         lines = []
#         for y in range(self.height):
#             if y < int(self.height * 0.3):
#                 lines.append(self._make_sky_line(y))
#                 lines.append(self._make_seagull_line(y))
#             elif y < int(self.height * 0.6):
#                 lines.append(self._make_wave_line(y))
#             else:
#                 lines.append(self._make_sand_line(y))
#         return Group(*lines)
#
#     def run(self):
#         """Main loop to render beach scene continuously."""
#         with Live(self._compose(), console=self.console, refresh_per_second=self.fps, screen=True):
#             while not self._stop.is_set():
#                 self.pulse += 0.1
#                 if self.pulse > 2 * math.pi:
#                     self.pulse -= 2 * math.pi
#                 time.sleep(1 / self.fps)
