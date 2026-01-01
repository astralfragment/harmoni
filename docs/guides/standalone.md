# Standalone Executable Guide

HARMONI is available as a standalone executable that requires no Python installation. This guide covers downloading, running, and building the executable.

## Downloading HARMONI

### From GitHub Releases

1. Go to the [Releases page](https://github.com/Ssenseii/spotify-yt-dlp-downloader/releases)
2. Download the latest `HARMONI.exe` (Windows) or `HARMONI` (Linux/macOS)
3. Run the executable - no installation required

---

## Running the Executable

### Windows

Double-click `HARMONI.exe` or run from command prompt:

```cmd
HARMONI.exe
```

### Linux/macOS

```bash
chmod +x HARMONI  # Make executable (first time only)
./HARMONI
```

---

## First Run Setup

On first launch, HARMONI will:

1. Create a `config.json` file in the same directory (from the bundled template)
2. Create necessary data folders (`data/`, `music/`)
3. Check for FFmpeg and offer to install it if missing

### FFmpeg

FFmpeg is required for audio conversion. The GUI will detect if FFmpeg is missing and offer to download it automatically.

**Manual installation:**

- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Debian/Ubuntu)

---

## File Locations

When running as a standalone executable, files are stored relative to the executable:

```
HARMONI.exe
├── config.json          # Configuration (created on first run)
├── data/
│   ├── exportify/       # Drop Exportify CSV files here
│   ├── tracks.json
│   └── playlists.json
└── music/               # Downloaded music output
```

---

## Configuration

Edit `config.json` to customize settings:

```json
{
  "output_dir": "music",
  "audio_format": "mp3",
  "sleep_between": 5,
  "retry_attempts": 3
}
```

Or use the Settings tab in the GUI.

See [Configuration Reference](configuration.md) for all options.

---

## Portable Mode

The executable is fully portable:

1. Copy `HARMONI.exe` and `config.json` to any folder
2. Create `data/exportify/` subfolder for CSV imports
3. Run from anywhere

Music will download to the `music/` folder relative to the executable.

---

## Building from Source

To build your own executable:

### Prerequisites

```bash
pip install pyinstaller
pip install -r requirements.txt
```

### Build Command

```bash
pyinstaller HARMONI.spec
```

The executable will be created in the `dist/` folder.

### Build Options

The `HARMONI.spec` file configures:

- **Entry point**: `gui_main.py` (GUI version)
- **Bundled files**: `config.json.example`, icon resources
- **Icon**: `gui/resources/icons/app/app_icon.ico`
- **Console**: Hidden (GUI mode)

### Custom Build

To create a CLI-only executable:

```bash
pyinstaller --onefile --name HARMONI-CLI main.py
```

---

## Troubleshooting

### "Windows protected your PC"

Windows SmartScreen may block unsigned executables:

1. Click "More info"
2. Click "Run anyway"

This warning appears because the executable is not code-signed.

### Missing DLL errors

Ensure you have the [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) installed.

### FFmpeg not found

The GUI will show FFmpeg status in Settings:

1. Go to Settings tab
2. Check "FFmpeg Status"
3. Click "Install FFmpeg" if not found

### Application crashes on startup

1. Delete `config.json` to reset to defaults
2. Run from command prompt to see error messages:
   ```cmd
   HARMONI.exe
   ```

### Antivirus false positives

Some antivirus software flags PyInstaller executables as suspicious. This is a known issue with PyInstaller. You can:

1. Add an exception for HARMONI in your antivirus
2. Build from source to verify the code
3. Use the Python version instead

---

## Limitations

The standalone executable has some limitations compared to the Python version:

| Feature | Executable | Python |
|---------|------------|--------|
| Auto-updates | Manual download | `pip install --upgrade` |
| Custom plugins | No | Yes |
| Debug mode | Limited | Full |
| File size | ~50MB | ~5MB (+ dependencies) |

---

## Updates

To update the standalone version:

1. Download the latest release from GitHub
2. Replace the old executable
3. Your `config.json` and data files are preserved

---

## Next Steps

- [GUI Guide](gui.md) - Learn all GUI features
- [Configuration Reference](configuration.md) - Customize settings
- [Spotify Setup](spotify-setup.md) - Connect your Spotify account
