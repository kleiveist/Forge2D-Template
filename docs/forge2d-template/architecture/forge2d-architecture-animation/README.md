<!-- AUTO-GENERATED:backlink START -->
[← Back](forge2d-architecture-animation.md)
<!-- AUTO-GENERATED:backlink END -->
# Forge2D Runtime Architecture – Manim Animation

Diese Animation erklärt die genre-neutrale Laufzeitarchitektur des
Forge2D-Templates in vier Schritten:

1. stabiler Startpfad von `Bootstrap` zu `ApplicationRoot`;
2. Besitz von `RouteHost`, persistenter UI und Übergangsebene;
3. sicherer Austausch genau einer aktiven Route durch `SceneRouter`;
4. erlaubte Abhängigkeitsrichtung zwischen Komposition, Features, Services und
   gemeinsamem Code.

## Mit Manim rendern

Voraussetzung: Python 3.11+ und eine funktionsfähige Installation von
[Manim Community](https://www.manim.community/).

```bash
python -m pip install -r requirements.txt
manim -pqh forge2d_architecture.py Forge2DArchitecture
```

Für einen schnelleren Testrender:

```bash
manim -pql forge2d_architecture.py Forge2DArchitecture
```

Die Szene ist vollständig vektorbasiert und verwendet keine externen Bilder
oder Fonts. Farben, Texte, Laufzeiten und Kapitel lassen sich oben in
`forge2d_architecture.py` anpassen.

## Dateien

- `forge2d_architecture.py` – editierbare Manim-Szene
- `forge2d_architecture.mp4` – gerenderte Vorschau
- `forge2d_architecture.gif` – kompakte Vorschau für Chats und Dokumentation
- `forge2d_architecture_poster.png` – Standbild
- `fallback_render.py` – portabler Vorschau-Renderer für Umgebungen ohne Cairo

Fachliche Grundlage ist
`docs/forge2d-template/architecture/runtime-overview.md` des Forge2D-Templates.
