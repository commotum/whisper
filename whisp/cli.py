from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path

import typer

from . import md

app = typer.Typer(add_completion=False, no_args_is_help=True)


def _run(cmd: list[str]) -> int:
    typer.echo("$ " + " ".join(shlex.quote(c) for c in cmd), err=True)
    return subprocess.run(cmd).returncode


def _default_title_from_path(p: Path) -> str:
    return p.stem.replace("_", " ")


@app.command()
def md_transcribe(
    media: Path = typer.Argument(..., exists=True, dir_okay=False, help="Audio/video file."),
    out: Path | None = typer.Option(None, "--out", help="Write markdown to this path."),
    title: str | None = typer.Option(None, "--title", help="Markdown title (defaults from filename)."),
    speaker: str = typer.Option("Speaker", "--speaker", help="Speaker label to use in markdown."),
    model: str = typer.Option("large-v3", "--model", help="Whisper model name."),
    device: str | None = typer.Option(None, "--device", help="Force device: cuda|cpu (default: auto)."),
    max_gap_s: float = typer.Option(1.2, "--max-gap", help="New turn if gap between segments exceeds this."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging."),
):
    """Transcribe media to a nice markdown transcript with turn-level timestamps."""

    if out is None:
        out = media.with_suffix(".md")

    out.parent.mkdir(parents=True, exist_ok=True)

    if title is None:
        title = _default_title_from_path(media)

    # Lazy import (torch/whisper are heavy)
    import torch  # type: ignore
    import whisper  # type: ignore

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    if verbose:
        typer.echo(f"media={media}", err=True)
        typer.echo(f"out={out}", err=True)
        typer.echo(f"model={model}", err=True)
        typer.echo(f"device={device}", err=True)

    w = whisper.load_model(model, device=device)
    result = w.transcribe(str(media))

    segments = [md.Segment(start=s["start"], end=s["end"], text=s["text"]) for s in result.get("segments", [])]
    turns = md.segments_to_turns(segments, max_gap_s=max_gap_s)
    text = md.render_markdown(title=title, speaker=speaker, turns=turns)

    out.write_text(text, encoding="utf-8")

    # For chaining: print the output path
    sys.stdout.write(str(out) + "\n")


@app.command()
def gate():
    """Fast local checks (ruff + pytest)."""
    venv_bin = Path(sys.executable).resolve().parent

    def tool(args: list[str]) -> int:
        exe = venv_bin / args[0]
        if exe.exists():
            cmd = [str(exe), *args[1:]]
        else:
            cmd = [sys.executable, "-m", args[0].replace("-", "_"), *args[1:]]
        return _run(cmd)

    rc = tool(["ruff", "check", "."])
    if rc != 0:
        raise typer.Exit(rc)
    rc = tool(["pytest", "-q"])
    raise typer.Exit(rc)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
