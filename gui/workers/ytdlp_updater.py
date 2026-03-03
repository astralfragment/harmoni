"""yt-dlp update checker and installer worker."""

import subprocess
from PySide6.QtCore import QThread, Signal

from tools.ytdlp_update_checker import check_ytdlp_updates


class YtdlpUpdaterWorker(QThread):
    """Worker thread for checking and updating yt-dlp."""

    progress = Signal(int, str)  # progress percent, status message
    finished = Signal(bool, str)  # success, message

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cancelled = False

    def cancel(self):
        """Cancel the update."""
        self._cancelled = True

    def run(self):
        """Run the yt-dlp update check and installation."""
        try:
            self.progress.emit(10, "Checking for yt-dlp updates...")

            # Check for updates
            update_info = check_ytdlp_updates()
            if not update_info:
                self.finished.emit(False, "Could not check yt-dlp version")
                return

            current_version = update_info.get("current_version")
            latest_version = update_info.get("latest_version")
            has_update = update_info.get("update_available", False)

            if not has_update:
                self.finished.emit(
                    True,
                    f"yt-dlp is already up to date\nVersion: {current_version}"
                )
                return

            if not latest_version:
                self.finished.emit(False, update_info.get("message", "Could not fetch latest version"))
                return

            self.progress.emit(20, f"Update available: {current_version} → {latest_version}")
            self.progress.emit(30, "Installing yt-dlp update...")

            # Run pip install --upgrade yt-dlp
            result = subprocess.run(
                ["pip", "install", "--upgrade", "yt-dlp"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if self._cancelled:
                self.finished.emit(False, "Update cancelled")
                return

            self.progress.emit(90, "Verifying installation...")

            if result.returncode == 0:
                # Verify new version
                updated_info = check_ytdlp_updates()
                if updated_info:
                    new_version = updated_info.get("current_version", latest_version)
                    self.progress.emit(100, "Update complete!")
                    self.finished.emit(
                        True,
                        f"yt-dlp updated successfully\n{current_version} → {new_version}"
                    )
                else:
                    self.finished.emit(True, f"yt-dlp updated to {latest_version}")
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                self.finished.emit(False, f"Update failed:\n{error_msg[:200]}")

        except subprocess.TimeoutExpired:
            self.finished.emit(False, "Update timed out (took longer than 5 minutes)")
        except Exception as e:
            self.finished.emit(False, f"Update failed: {str(e)}")
