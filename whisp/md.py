from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .timefmt import hhmmss


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class Turn:
    start: float
    end: float
    text: str


def segments_to_turns(
    segments: Iterable[Segment],
    *,
    max_gap_s: float = 1.2,
    max_chars: int = 500,
) -> list[Turn]:
    turns: list[Turn] = []

    cur_start = None
    cur_end = None
    cur_text: list[str] = []

    def flush() -> None:
        nonlocal cur_start, cur_end, cur_text
        if cur_start is None or cur_end is None:
            return
        text = " ".join(t.strip() for t in cur_text if t.strip()).strip()
        if text:
            turns.append(Turn(start=cur_start, end=cur_end, text=text))
        cur_start = None
        cur_end = None
        cur_text = []

    prev_end: float | None = None

    for seg in segments:
        gap = (seg.start - prev_end) if prev_end is not None else 0.0
        would_overflow = (sum(len(t) for t in cur_text) + len(seg.text)) > max_chars

        if cur_start is None:
            cur_start = seg.start
            cur_end = seg.end
            cur_text = [seg.text]
        elif gap > max_gap_s or would_overflow:
            flush()
            cur_start = seg.start
            cur_end = seg.end
            cur_text = [seg.text]
        else:
            cur_end = seg.end
            cur_text.append(seg.text)

        prev_end = seg.end

    flush()
    return turns


def render_markdown(
    *,
    title: str,
    speaker: str,
    turns: list[Turn],
) -> str:
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append("## Transcript")
    lines.append("")

    for t in turns:
        ts = hhmmss(t.start)
        lines.append(f"**{speaker} ({ts}):**")
        lines.append("")
        lines.append(t.text)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
