# Auto Cut Studio

Auto Cut Studio is a local video cutting toolkit for Windows. It removes silence, keeps speech tight, can preserve motion, and can clean voice audio without sending your files to a cloud service.

The project includes two ways to work:

- A drag and drop batch file for fast desktop use.
- A local web app with file upload, mode selection, live logs, progress, and download links.

## Features

- Smart silence cutting powered by `auto-editor`.
- Multiple edit presets for different content styles.
- Light voice denoise and volume consistency with a bundled FFmpeg helper.
- Batch processing for more than one file at a time.
- Bilingual local web interface with English and Bangla controls.
- Stylish language switch for instant interface translation.
- Outputs are saved locally and never leave the machine.

## Edit Modes

| Mode | Purpose |
| --- | --- |
| Normal | Default silence based smart cut. |
| Safe | Keeps more space around speech to reduce clipped words. |
| Podcast | Cuts silence, slightly speeds speech, and balances voice level. |
| Soft | Fast-forwards silent parts instead of removing them completely. |
| Motion-aware | Keeps sections with speech or visible movement. |
| Light denoise | Runs a smart cut, then applies light audio denoise. |
| Voice consistent | Runs a smart cut with EBU voice volume normalization. |
| Clean voice | Runs a smart cut, denoise, and volume consistency. |

## Requirements

- Windows 10 or Windows 11.
- Python 3.11 or newer.
- Internet access during setup.

During setup, the project installs:

- `auto-editor`
- `Flask`
- `imageio-ffmpeg`

You do not need to install FFmpeg globally. The `imageio-ffmpeg` package provides a local FFmpeg binary for cleanup modes.

## Setup

1. Install Python from <https://www.python.org/downloads/>.
2. During installation, enable `Add python.exe to PATH`.
3. Download or clone this repository.
4. Run:

```bat
setup.bat
```

The setup script creates a local `.venv` folder and installs the required packages.

## Drag and Drop Workflow

1. Run `setup.bat` once.
2. Drag one or more videos onto:

```bat
Drag and Drop Auto Edit.bat
```

3. Choose a mode from the menu.
4. Wait for the process to finish.

Output files are saved next to the original video with a mode suffix:

```text
my-video_normal-cut.mp4
my-video_safe-cut.mp4
my-video_clean-cut.mp4
```

If a file already exists, the tool adds a number to keep the older output.

## Web App Workflow

1. Run `setup.bat` once.
2. Start the app:

```bat
Start Web App.bat
```

3. Open:

```text
http://127.0.0.1:7860
```

4. Drop or select video files.
5. Pick an edit mode.
6. Click `Start processing`.
7. Download finished files from the results panel.

Use the `EN | বাংলা` switch in the top bar to change the interface language.

The web app stores uploaded files in `uploads/` and processed files in `outputs/`. Both folders are ignored by Git.

## Command Line Use

After setup, you can run the engine directly:

```bat
.venv\Scripts\auto-editor.exe "input.mp4" --output "output.mp4"
```

For voice normalization:

```bat
.venv\Scripts\auto-editor.exe "input.mp4" --audio-normalize ebu --output "output.mp4"
```

## Project Structure

```text
.
|-- app.py
|-- audio_cleanup.py
|-- smartcut.py
|-- requirements.txt
|-- setup.bat
|-- Start Web App.bat
|-- Drag and Drop Auto Edit.bat
|-- static/
|   |-- app.js
|   `-- styles.css
`-- templates/
    `-- index.html
```

## Troubleshooting

### Python was not found

Install Python again and enable `Add python.exe to PATH`. Then run `setup.bat`.

### auto-editor was not found

Run `setup.bat` from the project folder. The batch tools expect `.venv` to exist in the same folder.

### Cleanup mode did not run

Run `setup.bat` again. Cleanup modes require `imageio-ffmpeg`.

### Browser cannot open the app

Make sure `Start Web App.bat` is still running. The address is:

```text
http://127.0.0.1:7860
```

## Notes

- The web app is designed for local use.
- The Flask server is not intended to be exposed directly to the public internet.
- Large videos may take time to upload into the local app and process.

## Creator and Credit

Created by **Kholipha Ahmmad Al-Amin** | **খলিফা আহম্মেদ আল-আমিন**.

**Title:** Software Engineer & AI Specialist, Founder & CEO at EquiSaaS BD, Principal Consultant at AR IT Consultancy, Full-Stack Developer & SaaS Product Builder.

**Portfolio:** <https://kholipha-ahmmad-al-amin.equisaas-bd.com/>

**Official links:**

- GitHub: <https://github.com/kholipha-ahmmad-al-amin>
- LinkedIn: <https://www.linkedin.com/in/kholipha-ahmmad-al-amin>
- X: <https://x.com/al_amin5519>
- Facebook: <https://www.facebook.com/kholipha.ahmmad.al.amin>
- Instagram: <https://www.instagram.com/kholipha.ahmmad.al.amin>

## License

MIT License.
