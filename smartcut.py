from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parent
WINDOWS_AUTO_EDITOR = ROOT / ".venv" / "Scripts" / "auto-editor.exe"
POSIX_AUTO_EDITOR = ROOT / ".venv" / "bin" / "auto-editor"
AUDIO_HELPER = ROOT / "audio_cleanup.py"


@dataclass(frozen=True)
class Mode:
    key: str
    label: str
    suffix: str
    description: str
    auto_args: tuple[str, ...] = ()
    cleanup_args: tuple[str, ...] = ()

    @property
    def needs_cleanup(self) -> bool:
        return bool(self.cleanup_args)


MODES: dict[str, Mode] = {
    "normal": Mode(
        key="normal",
        label="Normal",
        suffix="_normal-cut",
        description="Default silence based smart cut.",
    ),
    "safe": Mode(
        key="safe",
        label="Safe",
        suffix="_safe-cut",
        description="Keeps more space around speech to reduce clipped words.",
        auto_args=("--margin", "0.5s"),
    ),
    "podcast": Mode(
        key="podcast",
        label="Podcast",
        suffix="_podcast-cut",
        description="Cuts silence, slightly speeds speech, and balances voice level.",
        auto_args=("--margin", "0.25s", "--video-speed", "1.08", "--audio-normalize", "ebu"),
    ),
    "soft": Mode(
        key="soft",
        label="Soft",
        suffix="_soft-cut",
        description="Fast-forwards silent parts instead of removing them completely.",
        auto_args=("--margin", "0.2s", "--silent-speed", "8"),
    ),
    "motion": Mode(
        key="motion",
        label="Motion-aware",
        suffix="_motion-cut",
        description="Keeps sections with speech or visible movement.",
        auto_args=("--edit", "(or (audio 0.04) (motion 0.02))"),
    ),
    "denoise": Mode(
        key="denoise",
        label="Light denoise",
        suffix="_denoise-cut",
        description="Applies a light voice cleanup pass after the smart cut.",
        cleanup_args=("--denoise",),
    ),
    "voice": Mode(
        key="voice",
        label="Voice consistent",
        suffix="_voice-cut",
        description="Runs smart cut with EBU voice volume normalization.",
        auto_args=("--audio-normalize", "ebu"),
    ),
    "clean": Mode(
        key="clean",
        label="Clean voice",
        suffix="_clean-cut",
        description="Runs smart cut, denoise, and voice volume consistency.",
        cleanup_args=("--denoise", "--normalize"),
    ),
}


LogFn = Callable[[str], None]


def clean_log_message(message: str) -> str:
    return message.encode("ascii", "ignore").decode("ascii").strip()


def find_auto_editor() -> str:
    if WINDOWS_AUTO_EDITOR.exists():
        return str(WINDOWS_AUTO_EDITOR)
    if POSIX_AUTO_EDITOR.exists():
        return str(POSIX_AUTO_EDITOR)

    found = shutil.which("auto-editor")
    if found:
        return found

    raise FileNotFoundError("auto-editor was not found. Run setup.bat or install requirements.txt.")


def unique_output_path(input_path: Path, output_dir: Path, suffix: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem
    ext = input_path.suffix or ".mp4"
    candidate = output_dir / f"{stem}{suffix}{ext}"
    count = 1

    while candidate.exists():
        count += 1
        candidate = output_dir / f"{stem}{suffix}_{count}{ext}"

    return candidate


def run_command(command: list[str], log: LogFn) -> int:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(ROOT),
    )

    assert process.stdout is not None
    buffer = ""

    while True:
        chunk = process.stdout.read(1)
        if not chunk:
            break

        if chunk in {"\r", "\n"}:
            message = clean_log_message(buffer)
            if message:
                log(message)
            buffer = ""
        else:
            buffer += chunk

    message = clean_log_message(buffer)
    if message:
        log(message)

    return process.wait()


def process_video(input_file: str | Path, mode_key: str, output_dir: str | Path, log: LogFn) -> Path:
    mode = MODES.get(mode_key, MODES["normal"])
    source = Path(input_file).resolve()
    destination = unique_output_path(source, Path(output_dir).resolve(), mode.suffix)
    auto_editor = find_auto_editor()

    if not source.exists():
        raise FileNotFoundError(f"Input file was not found: {source}")

    work_output = destination
    temp_file: Path | None = None

    if mode.needs_cleanup:
        handle, temp_name = tempfile.mkstemp(prefix="auto-cut-", suffix=source.suffix or ".mp4")
        os.close(handle)
        temp_file = Path(temp_name)
        work_output = temp_file

    command = [auto_editor, str(source), *mode.auto_args, "--output", str(work_output)]
    log(f"Running {mode.label} mode")

    edit_code = run_command(command, log)
    if edit_code != 0:
        if temp_file and temp_file.exists():
            temp_file.unlink()
        raise RuntimeError(f"auto-editor failed with exit code {edit_code}")

    if mode.needs_cleanup:
        log("Running audio cleanup")
        cleanup_command = [sys.executable, str(AUDIO_HELPER), str(work_output), str(destination), *mode.cleanup_args]
        cleanup_code = run_command(cleanup_command, log)

        if cleanup_code != 0:
            log("Audio cleanup failed. Keeping the smart cut output without cleanup.")
            shutil.move(str(work_output), str(destination))
        elif temp_file and temp_file.exists():
            temp_file.unlink()

    log(f"Saved {destination.name}")
    return destination
