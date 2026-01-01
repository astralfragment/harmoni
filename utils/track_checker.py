import os
from utils.logger import log_info


def track_key(track: dict) -> str:
    """Generate a unique key for a track based on artist and track name."""
    artist = (track.get("artist") or "").strip().lower()
    name = (track.get("track") or "").strip().lower()
    return f"{artist}|{name}"


def existing_track_keys_in_dir(directory: str) -> set:
    """
    Get a set of track keys for all audio files in a directory.
    Parses filenames in the format "Artist - Track.ext" to generate keys.
    """
    keys = set()
    if not os.path.exists(directory):
        return keys

    audio_extensions = {".mp3", ".m4a", ".opus", ".flac", ".wav", ".ogg", ".webm"}

    try:
        for filename in os.listdir(directory):
            name, ext = os.path.splitext(filename)
            if ext.lower() not in audio_extensions:
                continue

            # Parse "Artist - Track" format
            if " - " in name:
                parts = name.split(" - ", 1)
                artist = parts[0].strip().lower()
                track = parts[1].strip().lower()
                keys.add(f"{artist}|{track}")
    except OSError:
        pass

    return keys


def check_downloaded_files(output_dir, tracks):
    """
    Check which tracks have already been downloaded.
    Returns: (downloaded_count, pending_tracks_list)
    """
    downloaded = []
    pending = []

    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        existing_files = set(os.listdir(output_dir))
    except Exception:
        existing_files = set()

    for track in tracks:
        filename = f"{track['artist']} - {track['track']}.mp3".replace("/", "-")
        if filename in existing_files:
            downloaded.append(track)
        else:
            pending.append(track)

    log_info(f"Downloaded: {len(downloaded)} tracks, Pending: {len(pending)} tracks")
    return len(downloaded), pending


def check_downloaded_playlists(output_dir, playlists):
    """
    Checks which playlists and tracks have already been downloaded.
    Returns:
        downloaded_playlists: list of dicts with playlist info and downloaded tracks
        pending_playlists: list of dicts with playlist info and pending tracks
    """
    downloaded_playlists = []
    pending_playlists = []

    for pl in playlists:
        playlist_name = pl["name"]
        sanitized_name = playlist_name.replace("/", "-").strip()
        playlist_dir = os.path.join(output_dir, sanitized_name)

        # Check if playlist has direct "tracks" array (Exportify format)
        if pl.get("tracks") and isinstance(pl.get("tracks"), list) and len(pl.get("tracks", [])) > 0:
            first_track = pl.get("tracks")[0]
            if isinstance(first_track, dict) and "artist" in first_track and "track" in first_track:
                tracks = pl.get("tracks", [])
            else:
                # Try items structure
                tracks = [
                    {
                        "artist": item["track"]["artistName"],
                        "track": item["track"]["trackName"]
                    }
                    for item in pl.get("items", [])
                    if item.get("track")
                ]
        else:
            # Use items structure (Spotify export format)
            tracks = [
                {
                    "artist": item["track"]["artistName"],
                    "track": item["track"]["trackName"]
                }
                for item in pl.get("items", [])
                if item.get("track")
            ]

        if not os.path.exists(playlist_dir):
            log_info(f"Playlist folder missing: {playlist_name}")
            pending_playlists.append({
                "name": playlist_name,
                "tracks": tracks
            })
            continue

        existing_files = set(os.listdir(playlist_dir))
        downloaded_tracks = []
        pending_tracks = []

        for track in tracks:
            filename = f"{track['artist']} - {track['track']}.mp3".replace("/", "-")
            if filename in existing_files:
                downloaded_tracks.append(track)
            else:
                pending_tracks.append(track)

        log_info(f"{playlist_name} → Downloaded: {len(downloaded_tracks)}, Pending: {len(pending_tracks)}")

        if pending_tracks:
            pending_playlists.append({
                "name": playlist_name,
                "tracks": pending_tracks
            })
        else:
            downloaded_playlists.append({
                "name": playlist_name,
                "tracks": downloaded_tracks
            })

    return downloaded_playlists, pending_playlists
