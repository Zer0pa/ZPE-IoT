from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple, Union

# Eight cardinal/diagonal directions (R, UR, U, UL, L, DL, D, DR)
DIRS: Tuple[Tuple[int, int], ...] = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
)


@dataclass(frozen=True)
class MoveTo:
    x: int
    y: int


@dataclass(frozen=True)
class DrawDir:
    direction: int  # 0-7

    def delta(self) -> Tuple[int, int]:
        dx, dy = DIRS[self.direction]
        return dx, dy


@dataclass
class PolylineShape:
    points: List[Tuple[float, float]]
    stroke: str | None = None
    stroke_width: float | None = None
    fill: str | None = None


@dataclass
class StrokePath:
    commands: List[Union[MoveTo, DrawDir]]
    stroke: str | None = None
    stroke_width: float | None = None
    fill: str | None = None


StrokeCommand = Union[MoveTo, DrawDir]


def quantize_polylines(polylines: Sequence[PolylineShape]) -> List[PolylineShape]:
    """Snap normalized polylines to integer grid coordinates, preserving style."""
    quantized: List[PolylineShape] = []
    for poly in polylines:
        snapped: List[Tuple[int, int]] = []
        for x, y in poly.points:
            snapped.append((int(round(x)), int(round(y))))
        # drop consecutive duplicates to keep strokes compact
        deduped: List[Tuple[int, int]] = []
        for pt in snapped:
            if not deduped or deduped[-1] != pt:
                deduped.append(pt)
        if len(deduped) >= 2:
            quantized.append(
                PolylineShape(
                    points=deduped,
                    stroke=poly.stroke,
                    stroke_width=poly.stroke_width,
                    fill=poly.fill,
                )
            )
    return quantized


def _direction_for_step(dx: int, dy: int) -> int:
    try:
        return DIRS.index((dx, dy))
    except ValueError:
        raise ValueError(f"invalid step ({dx}, {dy}); expected unit step")


def polylines_to_strokes(polylines: Sequence[PolylineShape]) -> List[StrokePath]:
    """Convert integer polylines into move + 8-direction draw steps, preserving style."""
    paths: List[StrokePath] = []
    for poly in polylines:
        if len(poly.points) < 2:
            continue
        commands: List[StrokeCommand] = []
        x0, y0 = poly.points[0]
        commands.append(MoveTo(int(x0), int(y0)))
        cx, cy = int(x0), int(y0)
        for (nx, ny) in poly.points[1:]:
            nx_i, ny_i = int(nx), int(ny)
            dx = nx_i - cx
            dy = ny_i - cy
            # walk the segment with unit 8-direction steps
            while dx != 0 or dy != 0:
                step_dx = 0 if dx == 0 else (1 if dx > 0 else -1)
                step_dy = 0 if dy == 0 else (1 if dy > 0 else -1)
                dir_idx = _direction_for_step(step_dx, step_dy)
                commands.append(DrawDir(dir_idx))
                cx += step_dx
                cy += step_dy
                dx = nx_i - cx
                dy = ny_i - cy
        paths.append(
            StrokePath(
                commands=commands,
                stroke=poly.stroke,
                stroke_width=poly.stroke_width,
                fill=poly.fill,
            )
        )
    return paths


def strokes_to_polylines(paths: Iterable[StrokePath]) -> List[PolylineShape]:
    """Reconstruct polylines (with style) from stroke paths."""
    out: List[PolylineShape] = []
    for path in paths:
        polylines: List[Tuple[int, int]] = []
        cx = cy = 0
        for cmd in path.commands:
            if isinstance(cmd, MoveTo):
                if polylines:
                    # treat multiple MoveTos within a path as breaks
                    out.append(
                        PolylineShape(
                            points=polylines,
                            stroke=path.stroke,
                            stroke_width=path.stroke_width,
                            fill=path.fill,
                        )
                    )
                    polylines = []
                cx, cy = cmd.x, cmd.y
                polylines.append((cx, cy))
            elif isinstance(cmd, DrawDir):
                dx, dy = cmd.delta()
                cx += dx
                cy += dy
                polylines.append((cx, cy))
            else:
                raise TypeError(f"unknown stroke command {cmd!r}")
        if polylines:
            out.append(
                PolylineShape(
                    points=polylines,
                    stroke=path.stroke,
                    stroke_width=path.stroke_width,
                    fill=path.fill,
                )
            )
    return out
