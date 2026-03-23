#!/usr/bin/env python3
"""
HARMONI Desktop GUI - Main Entry Point

This is the GUI version of the HARMONI music downloader.
For the CLI version, use main.py instead.
"""

import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def check_dependencies():
    """Check for required dependencies."""
    missing = []

    try:
        import PySide6
    except ImportError:
        missing.append("PySide6")

    try:
        import yt_dlp
    except ImportError:
        missing.append("yt-dlp")

    if missing:
        print("Missing required dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nPlease install them with:")
        print("  pip install -r requirements.txt")
        sys.exit(1)


def get_app_dir() -> str:
    """Get the application directory (works for both script and frozen exe)."""
    import sys
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))


def create_default_config():
    """Create default config.json if it doesn't exist."""
    import shutil

    app_dir = get_app_dir()
    config_path = os.path.join(app_dir, "config.json")
    example_path = os.path.join(app_dir, "config.json.example")

    if not os.path.exists(config_path):
        if os.path.exists(example_path):
            shutil.copy(example_path, config_path)
            print(f"Created config.json from example file")
        else:
            # Create minimal config
            import json
            from config import DEFAULT_CONFIG

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            print(f"Created default config.json")


def configure_bundled_binaries():
    """Add bundled bin/ directory to PATH so ffmpeg and yt-dlp are found."""
    from utils.ffmpeg import configure_ffmpeg_path
    try:
        configure_ffmpeg_path()
    except FileNotFoundError:
        pass  # ffmpeg not bundled, will be handled later


def check_ffmpeg():
    """Check if FFmpeg is available."""
    from utils.ffmpeg import check_ffmpeg_available

    available, message = check_ffmpeg_available()
    if not available:
        print(f"Warning: {message}")
        print("Audio downloads may not work without FFmpeg.")
        print("")
        print("To install FFmpeg:")
        print("  - Windows: Download from https://github.com/BtbN/FFmpeg-Builds/releases")
        print("  - macOS: brew install ffmpeg")
        print("  - Linux: sudo apt install ffmpeg")
        print("")


def main():
    """Main entry point for the GUI application."""
    # Set Windows App User Model ID for proper taskbar icon
    import sys
    if sys.platform == 'win32':
        try:
            import ctypes
            app_id = 'harmoni.musicdownloader.gui.1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            pass

    # Set up bundled binaries (ffmpeg, yt-dlp) before anything checks for them
    configure_bundled_binaries()

    # Check dependencies first
    check_dependencies()

    # Now we can import PySide6
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("HARMONI")
    app.setApplicationDisplayName("HARMONI - Music Downloader")
    app.setOrganizationName("HARMONI")

    # Create config if needed
    create_default_config()

    # Check FFmpeg
    check_ffmpeg()

    # Load config
    try:
        from config import load_config
        config = load_config()
    except Exception as e:
        QMessageBox.critical(
            None,
            "Configuration Error",
            f"Failed to load configuration:\n{e}\n\n"
            "Please check your config.json file."
        )
        sys.exit(1)

    # Check for yt-dlp updates
    try:
        from tools.ytdlp_update_checker import check_ytdlp_updates
        update_info = check_ytdlp_updates()
        if update_info and update_info.get('update_available'):
            message = (
                f"yt-dlp Update Available\n\n"
                f"Current version: {update_info['current_version']}\n"
                f"Latest version: {update_info['latest_version']}\n\n"
                f"To update, run:\n"
                f"  pip install --upgrade yt-dlp"
            )
            QMessageBox.information(
                None,
                "Update Available",
                message
            )
    except Exception:
        pass  # Silently ignore update check failures

    # Apply stylesheet
    from gui.styles import get_stylesheet
    app.setStyleSheet(get_stylesheet())

    # Create and show main window
    from gui.main_window import MainWindow
    from gui.resources.icons import get_app_icon

    window = MainWindow(config)

    # Set application icon
    app_icon = get_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
        window.setWindowIcon(app_icon)

    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
