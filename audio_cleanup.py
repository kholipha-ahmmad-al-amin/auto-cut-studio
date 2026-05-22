import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def find_ffmpeg() -> str | None:
    root = Path(__file__).resolve().parent
    candidates = [
        root / "tools" / "ffmpeg.exe",
        root / "tools" / "ffmpeg" / "ffmpeg.exe",
        root / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe",
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    found = shutil.which("ffmpeg")
    if found:
        return found

    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def build_audio_filter(denoise: bool, normalize: bool) -> str:
    filters: list[str] = []

    if denoise:
        filters.append("afftdn=nr=8:nf=-28")

    if normalize:
        filters.append("dynaudnorm=f=150:g=15:p=0.95")
        filters.append("loudnorm=I=-16:LRA=11:TP=-1.5")

    return ",".join(filters)


def audio_codec_args(output_path: Path) -> list[str]:
    ext = output_path.suffix.lower()

    if ext == ".wav":
        return ["-c:a", "pcm_s16le"]
    if ext == ".flac":
        return ["-c:a", "flac"]
    if ext == ".mp3":
        return ["-c:a", "libmp3lame", "-b:a", "192k"]

    return ["-c:a", "aac", "-b:a", "160k"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Post-process auto-editor output with light FFmpeg audio cleanup."
    )
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--denoise", action="store_true")
    parser.add_argument("--normalize", action="store_true")
    args = parser.parse_args()

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print(
            "FFmpeg was not found. Put ffmpeg.exe in .\\tools\\ffmpeg\\bin\\ "
            "or install imageio-ffmpeg in the local .venv.",
            file=sys.stderr,
        )
        return 2

    audio_filter = build_audio_filter(args.denoise, args.normalize)
    if not audio_filter:
        print("No audio cleanup filter was requested.", file=sys.stderr)
        return 2

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        ffmpeg,
        "-hide_banner",
        "-y",
        "-i",
        str(input_path),
        "-map",
        "0",
        "-c:v",
        "copy",
        "-c:s",
        "copy",
        "-c:d",
        "copy",
        "-af",
        audio_filter,
        "-ar",
        "48000",
    ]

    cmd.extend(audio_codec_args(output_path))

    if output_path.suffix.lower() in {".mp4", ".m4v", ".mov"}:
        cmd.extend(["-movflags", "+faststart"])

    cmd.append(str(output_path))

    completed = subprocess.run(cmd)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
