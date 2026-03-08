# 🧵 Cloth Simulation

An interactive real-time cloth simulation built with Python and Pygame. Grab, drag, pin, and tear a physics-driven cloth using your mouse.

![Python](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.0%2B-green?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Demo

> Grab any point on the cloth and drag it freely in any direction. The constraint solver pulls the surrounding fabric along naturally, while gravity and damping give it a realistic feel.

---

## Features

- **True grab-and-drag** — click any point and move it freely in all directions, including upward against gravity
- **Cloth tearing** — links snap when stretched too far
- **Pin / unpin points** — right-click any node to fix it in place or release it
- **Toggleable gravity** — float the cloth or let it fall
- **Stretch shading** — links shift from warm white toward red as they approach their tear threshold
- **60 FPS** Verlet integration physics with iterative constraint solving

---

## Requirements

- Python 3.7+
- [Pygame](https://www.pygame.org/) 2.0+

---

## Installation

```bash
# Clone the repo
git clone https://github.com/your-username/cloth-simulation.git
cd cloth-simulation

# Install dependency
pip install pygame
```

---

## Usage

```bash
python cloth_simulation.py
```

### Controls

| Input | Action |
|---|---|
| **Left-click + drag** | Grab and move the cloth |
| **Right-click** | Pin / unpin a point (pinned points glow orange) |
| **G** | Toggle gravity on / off |
| **R** | Reset the cloth |

---

## How It Works

The cloth is modelled as a grid of **Point** nodes connected by **Link** constraints.

**Physics loop (each frame):**

1. **Verlet integration** — each point's velocity is derived from its current and previous position, then gravity and damping are applied.
2. **Grab anchoring** — the grabbed point is teleported directly to the mouse cursor before *and* after the physics step, and re-locked during every constraint iteration, so gravity can never fight the drag.
3. **Constraint solving** — the solver iterates `N` times, nudging connected nodes back toward their rest distance. More iterations = stiffer cloth.
4. **Tear detection** — any link stretched beyond `2.8×` its rest length is permanently removed.
5. **Boundary clamping** — points are kept inside the window with a velocity reflection.

---

## Configuration

All tunable constants are at the top of `cloth_simulation.py`:

| Constant | Default | Description |
|---|---|---|
| `CLOTH_COLS` | `30` | Number of nodes horizontally |
| `CLOTH_ROWS` | `22` | Number of nodes vertically |
| `SPACING` | `22` | Pixels between nodes |
| `GRAVITY` | `0.5` | Downward acceleration per frame |
| `DAMPING` | `0.98` | Velocity retention (1.0 = no damping) |
| `CONSTRAINT_ITER` | `8` | Solver iterations (higher = stiffer) |
| `TEAR_DISTANCE` | `SPACING × 2.8` | Link stretch before tearing |
| `GRAB_RADIUS` | `36` | Pixel radius for grab detection |

---

## License

MIT
