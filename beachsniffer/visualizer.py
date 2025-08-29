from rich.console import Console, Group
from rich.live import Live
from rich.text import Text
from rich.style import Style
import time
import math
import threading

class BeachVisualizer:
    def __init__(self, fps=15):
        self.console = Console()
        self.fps = fps
        self._stop = threading.Event()
        self.width = self.console.size.width
        self.height = self.console.size.height
        self.pulse = 0.0

    def stop(self):
        self._stop.set()

    def _make_sky_line(self, y: int) -> Text:
        """Return a single line of sky with sun pulse."""
        line = []
        # Simple pulsating sun effect at top-left corner
        sun_color = 255 if y < 3 else 200
        line.append(Text(" " * self.width, style=f"on rgb({sun_color}, {180 + int(self.pulse * 50)}, 255)"))
        return Text("").join(line)

    def _make_sand_line(self, y: int) -> Text:
        """Return a single line of sand at the bottom."""
        line = []
        sand_color = 194 + int(self.pulse * 20)
        line.append(Text(" " * self.width, style=f"on rgb({sand_color}, {178}, 128)"))
        return Text("").join(line)

    def _make_wave_line(self, y: int) -> Text:
        """Return a line representing waves in front of sand."""
        line = []
        wave_color = 0, 105, 148
        # simple sine wave pattern
        wave_chars = ["~", "≈", "^", "~"]
        chars = [wave_chars[(i + int(self.pulse * 5)) % len(wave_chars)] for i in range(self.width)]
        line.append(Text("".join(chars), style=f"rgb{wave_color}"))
        return Text("").join(line)

    def _make_seagull_line(self, y: int) -> Text:
        """Return a line with seagulls in sky (ASCII)."""
        line = [" "] * self.width
        for i in range(0, self.width, 20):
            # simple flying pattern
            bird = "v" if int(self.pulse * 5) % 2 == 0 else "^"
            if i + int(self.pulse * 3) < self.width:
                line[i + int(self.pulse * 3)] = bird
        return Text("".join(line), style="white")

    def _compose(self) -> Group:
        lines = []
        for y in range(self.height):
            if y < int(self.height * 0.3):
                lines.append(self._make_sky_line(y))
                lines.append(self._make_seagull_line(y))
            elif y < int(self.height * 0.6):
                lines.append(self._make_wave_line(y))
            else:
                lines.append(self._make_sand_line(y))
        return Group(*lines)

    def run(self):
        """Main loop to render beach scene continuously."""
        with Live(self._compose(), console=self.console, refresh_per_second=self.fps, screen=True):
            while not self._stop.is_set():
                self.pulse += 0.1
                if self.pulse > 2 * math.pi:
                    self.pulse -= 2 * math.pi
                time.sleep(1 / self.fps)
