"""Portable preview renderer for the Forge2D architecture animation.

This renderer mirrors the Manim scene with Pillow and streams frames to ffmpeg.
It exists so the included preview can be rebuilt on systems without Cairo/Pango.
The canonical editable animation remains ``forge2d_architecture.py``.
"""

from __future__ import annotations

import math
import subprocess
from functools import cache
from pathlib import Path
from typing import Callable, Sequence

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1280
HEIGHT = 720
FPS = 24
DURATION = 31.0

BG = (7, 17, 31)
PANEL = (16, 36, 58)
INK = (237, 247, 255)
MUTED = (142, 169, 190)
CYAN = (55, 212, 255)
GREEN = (91, 231, 169)
GOLD = (255, 200, 87)
RED = (255, 107, 122)
GRID = (26, 50, 72)

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "forge2d_architecture.mp4"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


@cache
def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def ease(value: float) -> float:
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def phase(t: float, start: float, duration: float) -> float:
    return ease((t - start) / duration)


def fade_window(t: float, start: float, end: float, edge: float = 0.45) -> float:
    return min(phase(t, start, edge), 1.0 - phase(t, end - edge, edge))


def rgba(color: tuple[int, int, int], alpha: float) -> tuple[int, int, int, int]:
    """Preblend a color against the fixed background for fast fading."""
    alpha = clamp(alpha)
    blended = tuple(round(BG[index] + (color[index] - BG[index]) * alpha) for index in range(3))
    return (*blended, 255)


def draw_grid(image: Image.Image) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x in range(0, WIDTH, 48):
        draw.line((x, 0, x, HEIGHT), fill=(*GRID, 60), width=1)
    for y in range(0, HEIGHT, 48):
        draw.line((0, y, WIDTH, y), fill=(*GRID, 60), width=1)
    image.alpha_composite(overlay)


def centered_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    size: int,
    color: tuple[int, int, int],
    *,
    alpha: float = 1.0,
    bold: bool = False,
) -> None:
    if alpha <= 0.001:
        return
    active_font = font(size, bold)
    box = draw.multiline_textbbox((0, 0), text, font=active_font, align="center", spacing=4)
    width = box[2] - box[0]
    height = box[3] - box[1]
    draw.multiline_text(
        (xy[0] - width / 2, xy[1] - height / 2 - box[1]),
        text,
        font=active_font,
        fill=rgba(color, alpha),
        anchor=None,
        align="center",
        spacing=4,
    )


def node(
    image: Image.Image,
    xy: tuple[float, float],
    title: str,
    subtitle: str,
    accent: tuple[int, int, int],
    *,
    alpha: float = 1.0,
    width: int = 210,
    height: int = 82,
    scale: float = 1.0,
) -> tuple[float, float, float, float]:
    width *= scale
    height *= scale
    x1, y1 = xy[0] - width / 2, xy[1] - height / 2
    x2, y2 = xy[0] + width / 2, xy[1] + height / 2
    if alpha <= 0.001:
        return x1, y1, x2, y2
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (x1 - 4, y1 - 4, x2 + 4, y2 + 4),
        radius=17,
        outline=rgba(accent, alpha * 0.3),
        width=4,
    )
    draw.rounded_rectangle(
        (x1, y1, x2, y2),
        radius=14,
        fill=rgba(PANEL, alpha * 0.97),
        outline=rgba(accent, alpha),
        width=2,
    )
    centered_text(draw, (xy[0], xy[1] - (9 if subtitle else 0)), title, round(21 * scale), INK, alpha=alpha, bold=True)
    if subtitle:
        centered_text(draw, (xy[0], xy[1] + 20 * scale), subtitle, round(13 * scale), MUTED, alpha=alpha)
    return x1, y1, x2, y2


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    color: tuple[int, int, int],
    *,
    alpha: float = 1.0,
    progress: float = 1.0,
    width: int = 3,
    dashed: bool = False,
) -> None:
    if alpha <= 0.001:
        return
    progress = clamp(progress)
    ex = start[0] + (end[0] - start[0]) * progress
    ey = start[1] + (end[1] - start[1]) * progress
    if dashed:
        distance = math.dist(start, (ex, ey))
        steps = max(1, int(distance / 18))
        for index in range(steps):
            a = index / steps
            b = min(1.0, a + 0.55 / steps)
            draw.line(
                (
                    start[0] + (ex - start[0]) * a,
                    start[1] + (ey - start[1]) * a,
                    start[0] + (ex - start[0]) * b,
                    start[1] + (ey - start[1]) * b,
                ),
                fill=rgba(color, alpha),
                width=width,
            )
    else:
        draw.line((*start, ex, ey), fill=rgba(color, alpha), width=width)
    if progress < 0.96:
        return
    angle = math.atan2(ey - start[1], ex - start[0])
    tip = 12
    wing = 0.5
    points = [
        (ex, ey),
        (ex - tip * math.cos(angle - wing), ey - tip * math.sin(angle - wing)),
        (ex - tip * math.cos(angle + wing), ey - tip * math.sin(angle + wing)),
    ]
    draw.polygon(points, fill=rgba(color, alpha))


def chapter(draw: ImageDraw.ImageDraw, number: str, title: str, alpha: float) -> None:
    if alpha <= 0.001:
        return
    draw.rounded_rectangle((48, 42, 102, 78), radius=9, fill=rgba(CYAN, alpha))
    centered_text(draw, (75, 60), number, 17, BG, alpha=alpha, bold=True)
    draw.text((120, 59), title, font=font(27, True), fill=rgba(INK, alpha), anchor="lm")


def title_scene(image: Image.Image, t: float) -> None:
    draw = ImageDraw.Draw(image)
    alpha = fade_window(t, 0.0, 3.4, 0.7)
    if alpha <= 0.001:
        return
    offset = (1.0 - phase(t, 0.1, 0.8)) * 18
    centered_text(draw, (WIDTH / 2, 250 - offset), "GODOT 2D · TEMPLATE BASELINE", 20, CYAN, alpha=alpha)
    centered_text(draw, (WIDTH / 2, 325 - offset), "Forge2D Laufzeitarchitektur", 43, INK, alpha=alpha, bold=True)
    centered_text(draw, (WIDTH / 2, 385), "Kleiner Kern · klare Besitzer · austauschbare Features", 23, MUTED, alpha=alpha)


def topology_scene(image: Image.Image, t: float) -> None:
    local = t - 3.2
    alpha = fade_window(t, 3.2, 12.0, 0.55)
    if alpha <= 0.001:
        return
    draw = ImageDraw.Draw(image)
    chapter(draw, "01", "Stabiler Start und klare Besitzer", alpha)
    points = [(128, 230), (390, 230), (660, 230), (1005, 230)]
    details = [
        ("Bootstrap", "stabile Main Scene", GOLD, 205),
        ("ApplicationRoot", "Kompositionsbesitzer", CYAN, 230),
        ("RouteHost", "genau eine Route", GREEN, 205),
        ("template_home", "aktive Route", GREEN, 210),
    ]
    starts = [0.3, 1.2, 2.2, 3.2]
    for index, ((title, subtitle, accent, node_width), point) in enumerate(zip(details, points)):
        visible = alpha * phase(local, starts[index], 0.45)
        node(image, point, title, subtitle, accent, alpha=visible, width=node_width)
        if index:
            link_progress = phase(local, starts[index] - 0.45, 0.55)
            arrow(draw, (points[index - 1][0] + details[index - 1][3] / 2 + 6, 230), (point[0] - node_width / 2 - 8, 230), MUTED, alpha=alpha, progress=link_progress)

    branch_alpha = alpha * phase(local, 4.0, 0.55)
    node(image, (525, 410), "PersistentUI", "CanvasLayer", CYAN, alpha=branch_alpha, width=200, height=70)
    node(image, (820, 410), "TransitionLayer", "CanvasLayer", CYAN, alpha=branch_alpha, width=220, height=70)
    arrow(draw, (420, 270), (495, 373), MUTED, alpha=branch_alpha, progress=phase(local, 3.8, 0.5))
    arrow(draw, (430, 270), (780, 373), MUTED, alpha=branch_alpha, progress=phase(local, 3.9, 0.6))

    infra_alpha = alpha * phase(local, 5.2, 0.5)
    node(image, (235, 560), "RouteTable", "Resource", GOLD, alpha=infra_alpha, width=190, height=70)
    node(image, (500, 560), "SceneRouter", "einziger Autoload", CYAN, alpha=infra_alpha, width=220, height=70)
    arrow(draw, (335, 560), (380, 560), GOLD, alpha=infra_alpha, progress=phase(local, 5.4, 0.45))
    arrow(draw, (540, 523), (640, 273), CYAN, alpha=infra_alpha, progress=phase(local, 5.8, 0.7))

    pulse = phase(local, 6.8, 0.6) * (1.0 - phase(local, 7.5, 0.6))
    if pulse > 0:
        draw.rounded_rectangle((552 - 6 * pulse, 183 - 6 * pulse, 768 + 6 * pulse, 277 + 6 * pulse), radius=16, outline=rgba(GREEN, alpha * pulse), width=4)


def route_scene(image: Image.Image, t: float) -> None:
    local = t - 11.7
    alpha = fade_window(t, 11.7, 20.2, 0.55)
    if alpha <= 0.001:
        return
    draw = ImageDraw.Draw(image)
    chapter(draw, "02", "Sicherer Route-Wechsel", alpha)
    node(image, (200, 330), "SceneRouter", "navigate(route_id)", CYAN, alpha=alpha, width=230)
    node(image, (510, 330), "RouteHost", "aktiver Slot", GREEN, alpha=alpha, width=210)
    old_alpha = alpha * (1.0 - phase(local, 6.2, 0.8))
    old_y = 245 - 25 * phase(local, 5.8, 0.8)
    node(image, (940, old_y), "Route A", "bleibt zunächst aktiv", GOLD, alpha=old_alpha, width=230)
    arrow(draw, (315, 330), (400, 330), CYAN, alpha=alpha, progress=phase(local, 0.5, 0.55))
    arrow(draw, (615, 315), (820, 260), GOLD, alpha=old_alpha, progress=phase(local, 0.8, 0.6))

    next_visible = phase(local, 2.0, 0.55)
    next_move = phase(local, 5.7, 1.0)
    next_y = 430 + (245 - 430) * next_move
    next_accent = GREEN if next_move > 0.65 else CYAN
    node(image, (940, next_y), "Route B", "aktiv nach READY" if next_move > 0.65 else "wird vorbereitet", next_accent, alpha=alpha * next_visible, width=230)
    if next_move < 0.78:
        arrow(draw, (615, 345), (820, 415), CYAN, alpha=alpha * next_visible, progress=phase(local, 2.2, 0.65))
    else:
        arrow(draw, (615, 315), (820, 260), GREEN, alpha=alpha, progress=phase(local, 6.3, 0.55))

    safe_alpha = alpha * phase(local, 3.0, 0.45) * (1.0 - phase(local, 6.0, 0.45))
    centered_text(draw, (640, 610), "Fehler? Route A bleibt erhalten.", 21, MUTED, alpha=safe_alpha)
    ready_alpha = alpha * phase(local, 4.7, 0.35) * (1.0 - phase(local, 6.3, 0.4))
    centered_text(draw, (940, 492), "READY", 17, GREEN, alpha=ready_alpha, bold=True)
    completed_alpha = alpha * phase(local, 6.4, 0.4)
    centered_text(draw, (715, 370), "transition_completed", 18, GREEN, alpha=completed_alpha)


def dependency_scene(image: Image.Image, t: float) -> None:
    local = t - 19.9
    alpha = fade_window(t, 19.9, 27.2, 0.55)
    if alpha <= 0.001:
        return
    draw = ImageDraw.Draw(image)
    chapter(draw, "03", "Abhängigkeiten fließen nur nach innen", alpha)
    node(image, (640, 165), "Komposition", "verdrahtet", GOLD, alpha=alpha, width=210)
    feature_alpha = alpha * phase(local, 0.7, 0.55)
    node(image, (260, 345), "Feature A", "eigene Dateien", CYAN, alpha=feature_alpha, width=205)
    node(image, (640, 345), "Service API", "enger Vertrag", GREEN, alpha=feature_alpha, width=205)
    node(image, (1020, 345), "Feature B", "eigene Dateien", CYAN, alpha=feature_alpha, width=205)
    for target_x in (260, 640, 1020):
        arrow(draw, (640, 207), (target_x, 302), MUTED, alpha=feature_alpha, progress=phase(local, 1.15, 0.65))
    shared_alpha = alpha * phase(local, 2.4, 0.45)
    node(image, (640, 575), "Shared", "Engine + Definitionen", MUTED, alpha=shared_alpha, width=245)
    for source_x in (260, 640, 1020):
        arrow(draw, (source_x, 387), (640, 532), MUTED, alpha=shared_alpha, progress=phase(local, 2.75, 0.65))
    forbidden_alpha = alpha * phase(local, 4.1, 0.45)
    arrow(draw, (365, 442), (915, 442), RED, alpha=forbidden_alpha, dashed=True)
    if forbidden_alpha > 0.001:
        draw.line((625, 427, 655, 457), fill=rgba(RED, forbidden_alpha), width=5)
        draw.line((625, 457, 655, 427), fill=rgba(RED, forbidden_alpha), width=5)
    centered_text(draw, (640, 480), "kein Feature-zu-Feature-Import", 18, RED, alpha=forbidden_alpha)


def finale_scene(image: Image.Image, t: float) -> None:
    alpha = fade_window(t, 26.9, DURATION, 0.7)
    if alpha <= 0.001:
        return
    local = t - 26.9
    draw = ImageDraw.Draw(image)
    centered_text(draw, (640, 145), "Eine Architektur · viele 2D-Spieltypen", 37, INK, alpha=alpha, bold=True)
    scale = 0.92 + 0.08 * phase(local, 0.6, 0.6)
    node(image, (640, 330), "Aktive Route", "Root-Typ bleibt frei", GREEN, alpha=alpha, width=270, height=95, scale=scale)
    centered_text(draw, (640, 430), "Kleiner Kern. Klare Grenzen. Freie Spiellogik.", 23, MUTED, alpha=alpha * phase(local, 1.3, 0.5))
    labels = [
        (230, "Node2D-Welt", CYAN),
        (505, "Control-UI", GOLD),
        (775, "gemischte Szene", GREEN),
        (1050, "Tool-Ansicht", INK),
    ]
    for index, (x, text, color) in enumerate(labels):
        centered_text(draw, (x, 575), text, 20, color, alpha=alpha * phase(local, 2.0 + index * 0.18, 0.45))


SCENES: Sequence[Callable[[Image.Image, float], None]] = (
    title_scene,
    topology_scene,
    route_scene,
    dependency_scene,
    finale_scene,
)


def render_frame(t: float) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (*BG, 255))
    draw_grid(image)
    for scene in SCENES:
        scene(image, t)
    return image.convert("RGB")


def main() -> None:
    command = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{WIDTH}x{HEIGHT}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(OUTPUT),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    for frame_index in range(round(DURATION * FPS)):
        frame = render_frame(frame_index / FPS)
        process.stdin.write(frame.tobytes())
    process.stdin.close()
    return_code = process.wait()
    if return_code:
        raise SystemExit(return_code)
    print(OUTPUT)


if __name__ == "__main__":
    main()
