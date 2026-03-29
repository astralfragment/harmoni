# Standalone Executable Guide

HARMONI is available as a standalone executable that requires no Python installation. This guide covers downloading, running, and building the executable.

## Downloading HARMONI

### From GitHub Releases

1. Go to the [Releases page](https://github.com/Ssenseii/harmoni/releases)
2. Download the version for your platform:
   - **Windows**: `HARMONI.exe`
   - **macOS (Apple Silicon)**: `HARMONI-macos-arm64.dmg`

---

## Running the Executable

### Windows

Double-click `HARMONI.exe` or run from command prompt:

```cmd
HARMONI.exe
```

### macOS

#### Installing from DMG

1. Open `HARMONI-macos-arm64.dmg`
2. Drag **HARMONI** into your **Applications** folder
3. Eject the DMG

#### macOS Security (Gatekeeper)

Since HARMONI is not signed with an Apple Developer certificate, macOS will block it on first launch:

> "HARMONI" can't be opened because Apple cannot check it for malicious software.

**To allow it:**

1. Open **System Settings > Privacy & Security**
2. Scroll down — you'll see a message about HARMONI being blocked
3. Click **"Open Anyway"**
4. Confirm when prompted

Alternatively, right-click (or Control-click) the app and select **Open** from the context menu. This bypasses Gatekeeper for that specific app.

You only need to do this once. After that, HARMONI will open normally.

#### Running from Terminal

```bash
# If installed to Applications
open /Applications/HARMONI.app

# If running from another location
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

FFmpeg is bundled with the standalone releases. If for some reason it's missing:

- **Windows**: The GUI will detect and offer to download it automatically
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Debian/Ubuntu)

---

## File Locations

When running as a standalone executable, files are stored relative to the executable:

### Windows

```
HARMONI.exe
├── config.json          # Configuration (created on first run)
├── data/
│   ├── exportify/       # Drop Exportify CSV files here
│   ├── tracks.json
│   └── playlists.json
└── music/               # Downloaded music output
```

### macOS

When installed to Applications, HARMONI stores its data in your home directory:

```
~/Library/Application Support/HARMONI/
├── config.json
├── data/
│   ├── exportify/
│   ├── tracks.json
│   └── playlists.json
└── music/
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

1. Copy the executable and `config.json` to any folder
2. Create `data/exportify/` subfolder for CSV imports
3. Run from anywhere

Music will download to the `music/` folder relative to the executable.

---

## Building from Source

### Windows

```bash
pip install -r requirements.txt
pyinstaller HARMONI.spec
```

The executable will be created in the `dist/` folder.

### macOS

Use the build script (requires Python 3.12+ and Homebrew):

```bash
chmod +x build-macos.sh
./build-macos.sh
```

This will:
- Install Python dependencies
- Install and bundle ffmpeg via Homebrew
- Convert the app icon to `.icns`
- Build with PyInstaller
- Create a `.dmg` file

Output: `HARMONI-macos-<arch>.dmg`

### Build Options

The `HARMONI.spec` file (Windows) configures:

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

### macOS: "HARMONI is damaged and can't be opened"

This can happen if the quarantine attribute is set. Remove it:

```bash
xattr -cr /Applications/HARMONI.app
```

Then try opening again.

### macOS: App won't open at all

Try launching from Terminal to see error output:

```bash
/Applications/HARMONI.app/Contents/MacOS/HARMONI
```

### Missing DLL errors (Windows)

Ensure you have the [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) installed.

### FFmpeg not found

The GUI will show FFmpeg status in Settings:

1. Go to Settings tab
2. Check "FFmpeg Status"
3. Click "Install FFmpeg" if not found

### Application crashes on startup

1. Delete `config.json` to reset to defaults
2. Run from command prompt/terminal to see error messages

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

1. Download the latest release from [GitHub](https://github.com/Ssenseii/harmoni/releases)
2. Replace the old executable (or drag the new `.app` to Applications on macOS)
3. Your `config.json` and data files are preserved

---

## Next Steps

- [GUI Guide](gui.md) - Learn all GUI features
- [Configuration Reference](configuration.md) - Customize settings
- [Spotify Setup](spotify-setup.md) - Connect your Spotify account
