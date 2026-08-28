"""Animated overview of the Forge2D Template runtime architecture.

Render with:
    manim -pqh forge2d_architecture.py Forge2DArchitecture
"""

from __future__ import annotations

from manim import (
    AnimationGroup,
    Arrow,
    BLUE,
    BLUE_E,
    Circumscribe,
    Create,
    DashedLine,
    DOWN,
    FadeIn,
    FadeOut,
    GOLD,
    GREEN,
    GREY_B,
    GREY_D,
    GrowArrow,
    Indicate,
    LEFT,
    Line,
    ORIGIN,
    RED,
    RIGHT,
    RoundedRectangle,
    Scene,
    Succession,
    Text,
    Transform,
    UP,
    VGroup,
    WHITE,
    config,
    rate_functions,
)


config.background_color = "#07111F"

BG = "#07111F"
PANEL = "#10243A"
PANEL_ALT = "#15314D"
INK = "#EDF7FF"
MUTED = "#8EA9BE"
CYAN = "#37D4FF"
GREEN_ACCENT = "#5BE7A9"
GOLD_ACCENT = "#FFC857"
RED_ACCENT = "#FF6B7A"


class ArchitectureNode(VGroup):
    """Small labelled architecture node used throughout the animation."""

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        *,
        width: float = 2.45,
        height: float = 1.0,
        color: str = CYAN,
    ) -> None:
        super().__init__()
        box = RoundedRectangle(
            corner_radius=0.15,
            width=width,
            height=height,
            stroke_color=color,
            stroke_width=2.2,
            fill_color=PANEL,
            fill_opacity=0.96,
        )
        title_text = Text(title, font_size=25, color=INK, weight="SEMIBOLD")
        if subtitle:
            subtitle_text = Text(subtitle, font_size=15, color=MUTED)
            labels = VGroup(title_text, subtitle_text).arrange(DOWN, buff=0.08)
        else:
            labels = VGroup(title_text)
        labels.move_to(box)
        self.add(box, labels)
        self.box = box
        self.labels = labels


def chapter_label(number: str, title: str) -> VGroup:
    badge = RoundedRectangle(
        corner_radius=0.11,
        width=0.6,
        height=0.38,
        stroke_width=0,
        fill_color=CYAN,
        fill_opacity=1,
    )
    badge_text = Text(number, font_size=18, color=BG, weight="BOLD").move_to(badge)
    heading = Text(title, font_size=29, color=INK, weight="SEMIBOLD")
    return VGroup(VGroup(badge, badge_text), heading).arrange(RIGHT, buff=0.22)


def link(source: VGroup, target: VGroup, *, color: str = MUTED) -> Arrow:
    return Arrow(
        source.get_right(),
        target.get_left(),
        buff=0.12,
        stroke_width=2.4,
        color=color,
        max_tip_length_to_length_ratio=0.12,
    )


class Forge2DArchitecture(Scene):
    """Four-chapter animated technical overview."""

    def construct(self) -> None:
        self.show_title()
        self.show_topology()
        self.show_route_replacement()
        self.show_dependencies()
        self.show_finale()

    def show_title(self) -> None:
        kicker = Text("GODOT 2D · TEMPLATE BASELINE", font_size=23, color=CYAN)
        title = Text("Forge2D Laufzeitarchitektur", font_size=51, color=INK, weight="BOLD")
        subtitle = Text(
            "Kleiner Kern · klare Besitzer · austauschbare Features",
            font_size=25,
            color=MUTED,
        )
        group = VGroup(kicker, title, subtitle).arrange(DOWN, buff=0.24)
        self.play(FadeIn(kicker, shift=UP * 0.15), run_time=0.6)
        self.play(FadeIn(title, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(subtitle), run_time=0.6)
        self.wait(0.9)
        self.play(FadeOut(group, shift=UP * 0.2), run_time=0.7)

    def show_topology(self) -> None:
        heading = chapter_label("01", "Stabiler Start und klare Besitzer")
        heading.to_edge(UP, buff=0.45).to_edge(LEFT, buff=0.55)

        boot = ArchitectureNode("Bootstrap", "stabile Main Scene", color=GOLD_ACCENT)
        app = ArchitectureNode("ApplicationRoot", "Kompositionsbesitzer", width=2.8)
        host = ArchitectureNode("RouteHost", "genau eine Route", color=GREEN_ACCENT)
        route = ArchitectureNode("template_home", "aktive Route", color=GREEN_ACCENT)
        boot.move_to([-5.25, 1.45, 0])
        app.move_to([-2.05, 1.45, 0])
        host.move_to([1.2, 1.45, 0])
        route.move_to([4.45, 1.45, 0])

        persistent_ui = ArchitectureNode(
            "PersistentUI", "CanvasLayer", width=2.35, height=0.9, color=BLUE
        ).move_to([-0.2, -0.15, 0])
        transitions = ArchitectureNode(
            "TransitionLayer", "CanvasLayer", width=2.55, height=0.9, color=BLUE
        ).move_to([3.0, -0.15, 0])
        table = ArchitectureNode(
            "RouteTable", "Resource", width=2.3, height=0.9, color=GOLD_ACCENT
        ).move_to([-4.25, -2.05, 0])
        router = ArchitectureNode(
            "SceneRouter", "einziger Autoload", width=2.6, height=0.9, color=CYAN
        ).move_to([-1.05, -2.05, 0])

        start_links = VGroup(link(boot, app), link(app, host), link(host, route))
        owner_ui = Arrow(app.get_bottom(), persistent_ui.get_left(), buff=0.12, color=MUTED)
        owner_fx = Arrow(app.get_bottom(), transitions.get_left(), buff=0.12, color=MUTED)
        table_router = link(table, router, color=GOLD_ACCENT)
        router_host = Arrow(
            router.get_top(), host.get_bottom(), buff=0.12, color=CYAN, stroke_width=2.6
        )

        self.play(FadeIn(heading), run_time=0.5)
        self.play(FadeIn(boot, shift=RIGHT * 0.18), run_time=0.45)
        self.play(
            Succession(
                GrowArrow(start_links[0]),
                FadeIn(app, shift=RIGHT * 0.15),
                GrowArrow(start_links[1]),
                FadeIn(host, shift=RIGHT * 0.15),
                GrowArrow(start_links[2]),
                FadeIn(route, shift=RIGHT * 0.15),
            ),
            run_time=3.0,
        )
        self.play(
            AnimationGroup(
                GrowArrow(owner_ui),
                FadeIn(persistent_ui, shift=DOWN * 0.1),
                GrowArrow(owner_fx),
                FadeIn(transitions, shift=DOWN * 0.1),
                lag_ratio=0.18,
            ),
            run_time=1.35,
        )
        self.play(
            Succession(
                FadeIn(table),
                GrowArrow(table_router),
                FadeIn(router),
                GrowArrow(router_host),
            ),
            run_time=1.8,
        )
        self.play(
            Indicate(host, color=GREEN_ACCENT, scale_factor=1.04),
            Indicate(router, color=CYAN, scale_factor=1.04),
            run_time=0.9,
        )
        topology = VGroup(
            heading,
            boot,
            app,
            host,
            route,
            persistent_ui,
            transitions,
            table,
            router,
            start_links,
            owner_ui,
            owner_fx,
            table_router,
            router_host,
        )
        self.wait(0.7)
        self.play(FadeOut(topology), run_time=0.7)

    def show_route_replacement(self) -> None:
        heading = chapter_label("02", "Sicherer Route-Wechsel")
        heading.to_edge(UP, buff=0.45).to_edge(LEFT, buff=0.55)
        router = ArchitectureNode("SceneRouter", "navigate(route_id)", width=2.8)
        host = ArchitectureNode("RouteHost", "aktiver Slot", width=2.6, color=GREEN_ACCENT)
        old_route = ArchitectureNode("Route A", "bleibt zunächst aktiv", color=GOLD_ACCENT)
        next_route = ArchitectureNode("Route B", "wird vorbereitet", color=CYAN)
        router.move_to([-4.5, 0.45, 0])
        host.move_to([-0.8, 0.45, 0])
        old_route.move_to([3.55, 1.4, 0])
        next_route.move_to([3.55, -1.25, 0])

        request = link(router, host, color=CYAN)
        current_link = Arrow(host.get_right(), old_route.get_left(), buff=0.12, color=GOLD_ACCENT)
        prepare_link = Arrow(host.get_right(), next_route.get_left(), buff=0.12, color=CYAN)
        safe_label = Text(
            "Fehler? Route A bleibt erhalten.", font_size=22, color=MUTED
        ).to_edge(DOWN, buff=0.65)

        self.play(FadeIn(heading), run_time=0.45)
        self.play(FadeIn(router), FadeIn(host), FadeIn(old_route), run_time=0.7)
        self.play(GrowArrow(request), GrowArrow(current_link), run_time=0.7)
        self.play(FadeIn(next_route, shift=LEFT * 0.18), GrowArrow(prepare_link), run_time=0.8)
        self.play(FadeIn(safe_label), Circumscribe(old_route, color=GOLD_ACCENT), run_time=1.0)

        ready = Text("READY", font_size=20, color=GREEN_ACCENT, weight="BOLD")
        ready.next_to(next_route, DOWN, buff=0.15)
        self.play(FadeIn(ready, shift=UP * 0.1), run_time=0.4)
        self.play(
            old_route.animate.set_opacity(0.25).shift(UP * 0.25),
            next_route.animate.move_to(old_route.get_center()),
            FadeOut(current_link),
            FadeOut(prepare_link),
            run_time=1.15,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        active_link = Arrow(host.get_right(), next_route.get_left(), buff=0.12, color=GREEN_ACCENT)
        complete = Text("transition_completed", font_size=21, color=GREEN_ACCENT)
        complete.next_to(active_link, DOWN, buff=0.18)
        self.play(GrowArrow(active_link), FadeIn(complete), FadeOut(old_route), FadeOut(ready), run_time=0.8)
        self.play(Indicate(next_route, color=GREEN_ACCENT, scale_factor=1.05), run_time=0.8)
        self.wait(0.65)
        self.play(
            FadeOut(
                VGroup(
                    heading,
                    router,
                    host,
                    next_route,
                    request,
                    active_link,
                    complete,
                    safe_label,
                )
            ),
            run_time=0.7,
        )

    def show_dependencies(self) -> None:
        heading = chapter_label("03", "Abhängigkeiten fließen nur nach innen")
        heading.to_edge(UP, buff=0.45).to_edge(LEFT, buff=0.55)
        app = ArchitectureNode("Komposition", "verdrahtet", color=GOLD_ACCENT).move_to([0, 2.05, 0])
        feature_a = ArchitectureNode("Feature A", "eigene Dateien", color=CYAN).move_to([-3.4, 0.35, 0])
        service = ArchitectureNode("Service API", "enger Vertrag", color=GREEN_ACCENT).move_to([0, 0.35, 0])
        feature_b = ArchitectureNode("Feature B", "eigene Dateien", color=CYAN).move_to([3.4, 0.35, 0])
        shared = ArchitectureNode("Shared", "Engine + Definitionen", width=2.8, color=GREY_B).move_to([0, -2.0, 0])

        allowed = VGroup(
            Arrow(app.get_bottom(), feature_a.get_top(), buff=0.12, color=MUTED),
            Arrow(app.get_bottom(), service.get_top(), buff=0.12, color=MUTED),
            Arrow(app.get_bottom(), feature_b.get_top(), buff=0.12, color=MUTED),
            Arrow(feature_a.get_bottom(), shared.get_left(), buff=0.12, color=MUTED),
            Arrow(service.get_bottom(), shared.get_top(), buff=0.12, color=MUTED),
            Arrow(feature_b.get_bottom(), shared.get_right(), buff=0.12, color=MUTED),
        )
        forbidden = DashedLine(
            feature_a.get_bottom() + DOWN * 0.48,
            feature_b.get_bottom() + DOWN * 0.48,
            color=RED_ACCENT,
            dash_length=0.13,
        )
        cross = VGroup(
            Line(LEFT * 0.13 + UP * 0.13, RIGHT * 0.13 + DOWN * 0.13, color=RED_ACCENT),
            Line(LEFT * 0.13 + DOWN * 0.13, RIGHT * 0.13 + UP * 0.13, color=RED_ACCENT),
        ).move_to(forbidden.get_center())
        rule = Text("kein Feature-zu-Feature-Import", font_size=20, color=RED_ACCENT)
        rule.next_to(forbidden, DOWN, buff=0.12)

        self.play(FadeIn(heading), FadeIn(app), run_time=0.6)
        self.play(
            AnimationGroup(
                FadeIn(feature_a, shift=DOWN * 0.15),
                FadeIn(service, shift=DOWN * 0.15),
                FadeIn(feature_b, shift=DOWN * 0.15),
                lag_ratio=0.18,
            ),
            run_time=1.0,
        )
        self.play(AnimationGroup(*[GrowArrow(arrow) for arrow in allowed[:3]], lag_ratio=0.12), run_time=0.9)
        self.play(FadeIn(shared, shift=UP * 0.12), run_time=0.45)
        self.play(AnimationGroup(*[GrowArrow(arrow) for arrow in allowed[3:]], lag_ratio=0.12), run_time=0.9)
        self.play(Create(forbidden), FadeIn(cross), FadeIn(rule), run_time=0.7)
        self.play(
            Indicate(feature_a, color=CYAN, scale_factor=1.03),
            Indicate(feature_b, color=CYAN, scale_factor=1.03),
            run_time=0.8,
        )
        self.wait(0.7)
        self.play(
            FadeOut(VGroup(heading, app, feature_a, service, feature_b, shared, allowed, forbidden, cross, rule)),
            run_time=0.7,
        )

    def show_finale(self) -> None:
        heading = Text("Eine Architektur · viele 2D-Spieltypen", font_size=42, color=INK, weight="BOLD")
        heading.to_edge(UP, buff=0.75)
        shell = ArchitectureNode("Aktive Route", "Root-Typ bleibt frei", width=3.0, height=1.15, color=GREEN_ACCENT)
        shell.move_to(ORIGIN + DOWN * 0.1)
        variants = VGroup(
            Text("Node2D-Welt", font_size=24, color=CYAN),
            Text("Control-UI", font_size=24, color=GOLD_ACCENT),
            Text("gemischte Szene", font_size=24, color=GREEN_ACCENT),
            Text("Tool-Ansicht", font_size=24, color=WHITE),
        ).arrange(RIGHT, buff=0.75).to_edge(DOWN, buff=1.0)
        takeaway = Text(
            "Kleiner Kern. Klare Grenzen. Freie Spiellogik.",
            font_size=27,
            color=MUTED,
        ).next_to(shell, DOWN, buff=0.55)

        self.play(FadeIn(heading, shift=UP * 0.15), run_time=0.7)
        self.play(FadeIn(shell, scale=0.92), run_time=0.65)
        self.play(FadeIn(takeaway), run_time=0.55)
        self.play(AnimationGroup(*[FadeIn(item, shift=UP * 0.12) for item in variants], lag_ratio=0.16), run_time=1.1)
        self.play(Circumscribe(shell, color=GREEN_ACCENT), run_time=1.0)
        self.wait(1.4)
        self.play(FadeOut(VGroup(heading, shell, takeaway, variants)), run_time=0.8)
