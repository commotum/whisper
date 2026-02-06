# whisper

Local Whisper transcription tools (CLI-first).

## Install

Inside this repo:

```bash
uv sync
```

## Usage

Transcribe an audio/video file to markdown (turn-level timestamps):

```bash
uv run whisp md-transcribe path/to/media.mp4 --out /path/to/transcript.md --speaker 'Dwarkesh Patel'
```

By default, it writes next to the media file with a `.md` extension and prints the output path.

## Notes

- Requires `ffmpeg` (installed on this machine).
- Uses `openai-whisper` and will use CUDA if available.
