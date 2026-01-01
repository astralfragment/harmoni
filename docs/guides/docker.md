# Docker Deployment

Run HARMONI in Docker without installing Python or ffmpeg locally.

## Prerequisites

- Docker
- Docker Compose (recommended)

---

## Option A: Docker Compose (Recommended)

```bash
# Build the image
docker compose build

# Run the application
docker compose run --rm --service-ports spotify-yt-dlp-downloader
```

> For older Docker versions, use `docker-compose` instead.

---

## Option B: Docker Only

```bash
# Build the image
docker build -t spotify-yt-dlp-downloader .

# Run the container
docker run --rm -it \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/music:/app/music" \
  -v "$(pwd)/export:/app/export" \
  -v "$(pwd)/config.json:/app/config.json" \
  -e TERM=xterm-256color \
  spotify-yt-dlp-downloader
```

---

## Persistent Data

The following directories are mounted as volumes to persist data:

| Local Path | Container Path | Purpose |
|------------|----------------|---------|
| `./data` | `/app/data` | Tracks, playlists, history, Exportify CSVs |
| `./music` | `/app/music` | Downloaded audio files |
| `./export` | `/app/export` | JSON exports |
| `./config.json` | `/app/config.json` | Configuration settings |

---

## Common Commands

```bash
# Rebuild after code changes
docker compose build --no-cache

# Run interactively
docker compose run --rm spotify-yt-dlp-downloader

# Open a shell in the container (debugging)
docker compose run --rm --entrypoint /bin/sh spotify-yt-dlp-downloader
```

---

## Interactive Mode Notes

HARMONI is an interactive CLI app requiring a TTY:

- Docker Compose sets `stdin_open: true` and `tty: true` automatically
- With plain Docker, always use `-it` flags
- If menus don't respond properly, use a real terminal (not an IDE console) and ensure `TERM` is set
