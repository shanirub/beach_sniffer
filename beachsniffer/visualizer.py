"""Retro ANSI art renderer using Rich.

We render a beach scene in a text terminal (tty1) without X:
- Sky with a sun that pulses based on TLS/HTTPS load.
- Seagulls that spawn on TCP handshakes and glide across the sky.
- Waves animated horizontally; DNS bursts add splashes/energy.
- Sand shimmering gently from ARP/DHCP "background noise".
- Occasional sparkles on the water for UDP bursts.

Design goals:
- Keep per-frame work minimal (good for a Pi 3B+).
- Use Rich Live() for smooth updates; target ~15 FPS by default.
"""
from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from queue import Queue, Empty
from typing import List, Tuple

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from . import events as E


@dataclass
class Seagull:
    x: float
    y: int
    vx: float
    sprite_phase: int = 0

    def step(self):
        self.x += self.vx
        self.sprite_phase = (self.sprite_phase + 1) % 4

    def sprite(self) -> str:
        # Cycle through a tiny wing-flap animation
        frames = [r"\\   /",
                  r" \\_ /",
                  r" / _/",
                  r"/   \\",
        ]
        return frames[self.sprite_phase]


@dataclass
class SceneState:
    width: int
    height: int
    gulls: List[Seagull] = field(default_factory=list)
    wave_phase: float = 0.0
    dns_energy: float = 0.0
    sand_shimmer: float = 0.0
    sun_energy: float = 0.0  # from TLS / heavy flows
    sparkle_timer: float = 0.0

    def decay(self):
        # Exponential-ish decay to keep the scene lively
        self.dns_energy *= 0.90
        self.sand_shimmer *= 0.95
        self.sun_energy *= 0.92
        self.sparkle_timer = max(0.0, self.sparkle_timer - 0.05)


class Visualizer:
    def __init__(self, event_queue: Queue, fps: int = 15, console: Console | None = None):
        self.q = event_queue
        self.console = console or Console()
        self.fps = max(5, min(60, fps))
        self.state = SceneState(width=80, height=24)

    # --- Event handling ---
    def _drain_events(self):
        # Drain without blocking, update state
        now = time.time()
        while True:
            try:
                evt, ts = self.q.get_nowait()
            except Empty:
                break
            if evt == E.ARP or evt == E.DHCP:
                self.state.sand_shimmer += 0.2
            elif evt == E.DNS:
                self.state.dns_energy += 0.7
            elif evt in (E.TCP_SYN, E.TCP_SYNACK):
                # spawn a seagull at left edge flying right
                y = random.randint(1, max(1, self.state.height // 4))
                self.state.gulls.append(Seagull(x=-5.0, y=y, vx=0.8 + random.random()))
            elif evt == E.UDP:
                self.state.sparkle_timer = 0.5
            elif evt == E.TLS:
                self.state.sun_energy += 0.3
            # ACK / OTHER ignored for visuals (keeps CPU low)

        # Cull off-screen gulls
        self.state.gulls = [g for g in self.state.gulls if g.x < self.state.width + 5]

    # --- Rendering helpers ---
    def _make_sky_line(self, y: int) -> Text:
        # Base sky color; brighten slightly with sun energy
        base = 180
        brightness = min(255, int(base + self.state.sun_energy * 40))
        sky = Text(" " * self.state.width, style=f"on rgb(0, {brightness}, {brightness})")

        # Sun: a soft circle at upper-right
        cx = int(self.state.width * 0.78)
        cy = int(self.state.height * 0.22)
        r = 4
        # Pulsing border based on sun energy
        pulse = 0.5 + 0.5 * math.sin(time.time() * 2.0)
        sun_color = 200 + int(min(55, self.state.sun_energy * 30 + pulse * 30))
        if abs(y - cy) <= r:
            span = int(math.sqrt(max(0, r * r - (y - cy) ** 2)))
            left = max(0, cx - span)
            right = min(self.state.width - 1, cx + span)
            for x in range(left, right):
                sky._spans.append(Text(" ", style=f"on rgb({sun_color}, {180 + pulse * 50:.0f}, 0)")._spans[0])
        return sky

    def _render_gulls(self, lines: List[Text]):
        for g in self.state.gulls:
            g.step()
            s = g.sprite()
            x = int(g.x)
            y = max(0, min(self.state.height // 3, g.y))
            if 0 <= y < len(lines):
                # overlay sprite onto the line
                line = lines[y]
                # Replace characters starting at x with the seagull sprite
                for i, ch in enumerate(s):
                    xi = x + i
                    if 0 <= xi < self.state.width:
                        line._text = line._text[:xi] + ch + line._text[xi + 1:]
                        # white gull on sky
                        # (Using Text.stylize would be cleaner but more expensive per char)

    def _make_wave_line(self, row: int) -> Text:
        # Animated wave using sine; DNS energy adds turbulence
        phase = self.state.wave_phase + row * 0.4
        ch = "≈" if ((row + int(self.state.wave_phase)) % 2 == 0) else "~"
        line = ""
        for x in range(self.state.width):
            y = math.sin((x * 0.25) + phase)
            if y > 0.4 - self.state.dns_energy * 0.05:
                line += ch
            else:
                line += " "
        style = "bold rgb(200,220,255) on rgb(0,40,80)"
        # UDP sparkles
        if self.state.sparkle_timer > 0:
            line = list(line)
            for _ in range(10):
                xi = random.randrange(0, self.state.width)
                line[xi] = "*"
            line = "".join(line)
        return Text(line, style=style)

    def _make_sand_line(self) -> Text:
        # Sand with subtle shimmering noise
        density = 0.06 + min(0.25, self.state.sand_shimmer * 0.02)
        chars = []
        for _ in range(self.state.width):
            chars.append("░" if random.random() < density else " ")
        return Text("".join(chars), style="rgb(230,200,120) on rgb(60,40,0)")

    def _compose(self) -> Panel:
        w, h = self.state.width, self.state.height
        sky_rows = max(3, h // 3)
        water_rows = max(5, h // 3)
        sand_rows = h - sky_rows - water_rows

        lines: List[Text] = []
        # Sky
        for y in range(sky_rows):
            lines.append(self._make_sky_line(y))
        self._render_gulls(lines)
        # Water
        for i in range(water_rows):
            lines.append(self._make_wave_line(i))
        # Sand
        for _ in range(sand_rows):
            lines.append(self._make_sand_line())

        # Footer legend (very light)
        legend = Text("  🕊 TCP handshakes  ✨ UDP  🌊 DNS  🌞 HTTPS load  🏖 ARP/DHCP ", style="dim")
        if len(lines) >= 1:
            last = lines[-1]
            pad = max(0, self.state.width - legend.cell_len)
            lines[-1] = Text(last.plain[:pad]) + legend

        # Advance global phases
        self.state.wave_phase += 0.25 + self.state.dns_energy * 0.02
        self.state.decay()

        body = Text.newlines().join(lines)
        return Panel(body, title="BeachSniffer", border_style="cyan")

    # --- Public API ---
    def run(self):
        # Size detection from terminal
        w, h = self.console.size
        self.state.width = max(60, w)
        self.state.height = max(20, h - 2)

        frame_time = 1.0 / float(self.fps)
        with Live(self._compose(), console=self.console, refresh_per_second=self.fps, screen=True):
            while True:
                self._drain_events()
                time.sleep(frame_time)
