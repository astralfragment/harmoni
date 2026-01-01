# CLI Guide

HARMONI includes a full-featured command-line interface for terminal users and automation. This guide covers all CLI menus and commands.

## Launching the CLI

```bash
python main.py
# or
./start.sh
```

The CLI uses an interactive menu system powered by [questionary](https://github.com/tmbo/questionary).

---

## Main Menu

```
🎵 Welcome to HARMONI Spotify & Music Downloader — Select an option:
> Downloads Menu
  Management Menu
  Automation Menu
  Tools Menu
  Config Menu
  Exit
```

Use arrow keys to navigate, Enter to select.

---

## Downloads Menu

The primary menu for downloading music.

### Options

| Option | Description |
|--------|-------------|
| **Download all pending (sequential)** | Download tracks one at a time from CSV/JSON sources |
| **Download all pending (batch async)** | Download multiple tracks concurrently |
| **Search & Download a single track** | Search YouTube and download a specific song |
| **Spotify Web API (OAuth)** | Access your Spotify playlists and liked songs |
| **Download from Exportify CSV folder** | Import and download from Exportify CSV files |
| **Download from playlists file** | Download from legacy playlists.json format |
| **Download from YouTube link/playlist** | Download directly from YouTube URLs |

### Spotify Web API Submenu

```
🎧 Spotify Web API — What would you like to do?
> Authenticate with Spotify (OAuth PKCE)
  Download from my playlists
  Download from liked songs
  Spotify API credential setup help
  Log out (clear cached token)
  Back
```

**Authentication Flow:**
1. Select "Authenticate with Spotify"
2. A browser opens for Spotify login
3. HARMONI captures the callback automatically (or you can paste the redirect URL)
4. Token is cached for future sessions

---

## Management Menu

Tools for managing your downloaded library.

| Option | Description |
|--------|-------------|
| **Retry failed downloads** | Re-attempt previously failed downloads |
| **Detect duplicates** | Find duplicate files in your library |
| **Organize files by artist/album** | Reorganize files into artist/album folders |
| **Embed metadata in MP3s** | Add ID3 tags to downloaded MP3 files |

---

## Automation Menu

Schedule and automate download tasks.

| Option | Description |
|--------|-------------|
| **Resume paused batch download** | Continue an interrupted batch download |
| **Schedule a download job** | Schedule downloads for later |
| **Sync exportify folder now** | Manually trigger CSV sync |
| **Schedule automatic sync** | Start continuous sync monitoring |
| **Run cleanup** | Remove temp files and empty directories |
| **Backup all data files** | Create backups of JSON data files |
| **View backup status** | Show backup statistics |
| **Clear sync state** | Force re-sync of all files |

### Sync Feature

The sync feature monitors your Exportify folder for new CSV files and automatically imports them.

```bash
# Enable auto-sync in config.json
"auto_sync_enabled": true,
"auto_sync_interval": 300  # seconds
```

---

## Tools Menu

Utility tools for library management.

| Tool | Description |
|------|-------------|
| **System check** | Verify system dependencies (ffmpeg, yt-dlp) |
| **Library cleanup** | Remove broken/corrupted audio files |
| **Playlist to track list** | Convert playlists to CSV/JSON track lists |
| **Dependency check** | Check all required dependencies |
| **Library export as JSON** | Export your library metadata as JSON |
| **Compress music** | Reduce file sizes of downloaded music |
| **Choose audio format** | Change the default audio output format |
| **Open log** | View the application log file |
| **Help** | Display help information |

---

## Config Menu

Manage application settings.

| Option | Description |
|--------|-------------|
| **View current config** | Display all current settings |
| **Update a setting** | Change individual settings |
| **Switch config profile** | Apply a preset configuration profile |
| **Toggle automation features** | Enable/disable auto-cleanup, backup, sync |
| **Reset to defaults** | Reset all settings to defaults |
| **Validate configuration** | Check for configuration errors |

### Configuration Profiles

HARMONI includes preset profiles:

- **default** - Balanced settings for most users
- **quality** - Higher quality audio settings
- **fast** - Optimized for speed

---

## Input Sources

The CLI supports multiple track input sources:

### 1. Exportify CSV (Recommended)

Drop CSV files from [exportify.net](https://exportify.net) into the `data/exportify/` folder.

```
data/exportify/
├── My Playlist.csv
├── Liked Songs.csv
└── Summer Vibes.csv
```

### 2. tracks.json

A JSON file with track data:

```json
[
  {"artist": "Artist Name", "track": "Song Title"},
  {"artist": "Another Artist", "track": "Another Song"}
]
```

### 3. playlists.json

Legacy format for playlist exports:

```json
[
  {
    "name": "Playlist Name",
    "items": [
      {
        "track": {
          "artistName": "Artist",
          "trackName": "Song"
        }
      }
    ]
  }
]
```

### 4. Spotify API

Direct access to your Spotify account (requires setup).

---

## Song Selection

When downloading playlists, HARMONI offers selection options:

```
📋 Select songs from 'My Playlist' (52 tracks):
> Download all
  Select which to download
  Skip already downloaded
  Back
```

**Skip already downloaded** only downloads songs not already in your library.

---

## Keyboard Navigation

| Key | Action |
|-----|--------|
| `↑` `↓` | Navigate menu options |
| `Enter` | Select option |
| `Space` | Toggle checkbox selection |
| `Ctrl+C` | Cancel current operation |

---

## Configuration File

The CLI reads from `config.json`:

```json
{
  "tracks_file": "data/tracks.json",
  "playlists_file": "data/playlists.json",
  "output_dir": "music",
  "audio_format": "mp3",
  "sleep_between": 5,
  "retry_attempts": 3,
  "retry_delay": 10,
  "exportify_watch_folder": "data/exportify",
  "auto_cleanup": false,
  "auto_backup": true,
  "auto_sync_enabled": false
}
```

See [Configuration Reference](configuration.md) for all options.

---

## Examples

### Download from Exportify

```bash
# 1. Export playlists from exportify.net
# 2. Save CSV files to data/exportify/
# 3. Run HARMONI
python main.py

# 4. Select: Downloads Menu > Download from Exportify CSV folder
# 5. Choose playlists to download
```

### Search and Download

```bash
python main.py
# Select: Downloads Menu > Search & Download a single track
# Enter artist: The Beatles
# Enter song: Let It Be
```

### Batch Download with Retry

```bash
python main.py
# Select: Downloads Menu > Download all pending (batch async)
# If some fail:
# Select: Management Menu > Retry failed downloads
```

---

## Troubleshooting

### "No tracks found"

- Check that your CSV/JSON files are in the correct location
- Verify file format matches expected structure
- Run **Tools Menu > Dependency check**

### Downloads failing frequently

1. Update yt-dlp: `pip install --upgrade yt-dlp`
2. Increase sleep time in config (reduces rate limiting)
3. Check your internet connection

### Spotify authentication issues

1. Ensure Client ID is set in `config.json`
2. Add correct redirect URI in Spotify Dashboard
3. Check firewall isn't blocking port 8888

---

## Next Steps

- [GUI Guide](gui.md) - Graphical interface alternative
- [Configuration Reference](configuration.md) - All settings explained
- [Spotify Setup](spotify-setup.md) - Detailed Spotify API setup
