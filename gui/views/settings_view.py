"""Settings view for configuration management."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QCheckBox,
    QGroupBox, QFormLayout, QFileDialog, QMessageBox,
    QSpacerItem, QSizePolicy, QScrollArea, QFrame,
    QProgressBar
)
from PySide6.QtCore import Signal

from config import save_config, validate_config, DEFAULT_CONFIG
from utils.ffmpeg import check_ffmpeg_available


class SettingsView(QWidget):
    """Settings configuration view."""

    config_saved = Signal()  # Emits when config is saved

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.ffmpeg_worker = None
        self._setup_ui()
        self._load_values()
        self._check_ffmpeg_status()

    def _setup_ui(self):
        """Set up the settings UI."""
        # Main layout with scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        # Title
        title = QLabel("Settings")
        title.setObjectName("title")
        layout.addWidget(title)

        # FFmpeg Status Group - placed at top for visibility
        ffmpeg_group = QGroupBox("FFmpeg Status")
        ffmpeg_layout = QVBoxLayout(ffmpeg_group)
        ffmpeg_layout.setSpacing(10)

        # Status row
        status_row = QHBoxLayout()
        self.ffmpeg_status_icon = QLabel("●")
        self.ffmpeg_status_icon.setFixedWidth(20)
        status_row.addWidget(self.ffmpeg_status_icon)

        self.ffmpeg_status_label = QLabel("Checking...")
        status_row.addWidget(self.ffmpeg_status_label, 1)

        self.ffmpeg_install_btn = QPushButton("Install FFmpeg")
        self.ffmpeg_install_btn.setObjectName("secondary")
        self.ffmpeg_install_btn.clicked.connect(self._install_ffmpeg)
        status_row.addWidget(self.ffmpeg_install_btn)

        self.ffmpeg_refresh_btn = QPushButton("Refresh")
        self.ffmpeg_refresh_btn.setObjectName("secondary")
        self.ffmpeg_refresh_btn.setFixedWidth(70)
        self.ffmpeg_refresh_btn.clicked.connect(self._check_ffmpeg_status)
        status_row.addWidget(self.ffmpeg_refresh_btn)

        ffmpeg_layout.addLayout(status_row)

        # Progress bar (hidden by default)
        self.ffmpeg_progress = QProgressBar()
        self.ffmpeg_progress.setVisible(False)
        ffmpeg_layout.addWidget(self.ffmpeg_progress)

        self.ffmpeg_progress_label = QLabel("")
        self.ffmpeg_progress_label.setObjectName("subtitle")
        self.ffmpeg_progress_label.setVisible(False)
        ffmpeg_layout.addWidget(self.ffmpeg_progress_label)

        # Help text
        ffmpeg_help = QLabel(
            "FFmpeg is required for audio conversion. "
            "Click 'Install FFmpeg' to automatically download and install it."
        )
        ffmpeg_help.setObjectName("subtitle")
        ffmpeg_help.setWordWrap(True)
        ffmpeg_layout.addWidget(ffmpeg_help)

        layout.addWidget(ffmpeg_group)

        # Output Settings Group
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout(output_group)
        output_layout.setSpacing(12)

        # Output directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("Select output directory...")
        output_dir_layout.addWidget(self.output_dir_input)
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondary")
        browse_btn.setFixedWidth(70)
        browse_btn.clicked.connect(self._browse_output_dir)
        output_dir_layout.addWidget(browse_btn)
        output_layout.addRow("Output Directory:", output_dir_layout)

        # Audio format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp3", "flac", "wav", "aac", "ogg", "m4a"])
        output_layout.addRow("Audio Format:", self.format_combo)

        layout.addWidget(output_group)

        # Spotify Settings Group
        spotify_group = QGroupBox("Spotify Settings")
        spotify_layout = QFormLayout(spotify_group)
        spotify_layout.setSpacing(12)

        # Client ID
        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("Enter your Spotify Client ID")
        spotify_layout.addRow("Client ID:", self.client_id_input)

        # Redirect URI (read-only)
        self.redirect_uri_input = QLineEdit()
        self.redirect_uri_input.setReadOnly(True)
        spotify_layout.addRow("Redirect URI:", self.redirect_uri_input)

        # Help text
        help_label = QLabel(
            "To get a Spotify Client ID:\n"
            "1. Go to developer.spotify.com/dashboard\n"
            "2. Create a new app\n"
            "3. Add http://127.0.0.1:8888/callback to Redirect URIs\n"
            "4. Copy the Client ID here"
        )
        help_label.setObjectName("subtitle")
        help_label.setWordWrap(True)
        spotify_layout.addRow("", help_label)

        layout.addWidget(spotify_group)

        # Download Settings Group
        download_group = QGroupBox("Download Settings")
        download_layout = QFormLayout(download_group)
        download_layout.setSpacing(12)

        # Sleep between downloads
        self.sleep_input = QLineEdit()
        self.sleep_input.setPlaceholderText("5")
        self.sleep_input.setFixedWidth(80)
        download_layout.addRow("Sleep Between (sec):", self.sleep_input)

        # Retry attempts
        self.retry_input = QLineEdit()
        self.retry_input.setPlaceholderText("3")
        self.retry_input.setFixedWidth(80)
        download_layout.addRow("Retry Attempts:", self.retry_input)

        layout.addWidget(download_group)

        # Metadata Settings Group
        metadata_group = QGroupBox("Metadata Settings")
        metadata_layout = QFormLayout(metadata_group)
        metadata_layout.setSpacing(12)

        # Enable metadata
        self.metadata_check = QCheckBox("Enable metadata embedding")
        metadata_layout.addRow("", self.metadata_check)

        # Metadata template
        self.template_combo = QComboBox()
        self.template_combo.addItems(["basic", "comprehensive", "dj-mix"])
        metadata_layout.addRow("Template:", self.template_combo)

        # MusicBrainz lookup
        self.musicbrainz_check = QCheckBox("Enable MusicBrainz lookup")
        metadata_layout.addRow("", self.musicbrainz_check)

        layout.addWidget(metadata_group)

        # Backup Settings Group
        backup_group = QGroupBox("Backup Settings")
        backup_layout = QFormLayout(backup_group)
        backup_layout.setSpacing(12)

        # Auto backup
        self.backup_check = QCheckBox("Enable automatic backups")
        backup_layout.addRow("", self.backup_check)

        # Max backups
        self.max_backups_input = QLineEdit()
        self.max_backups_input.setPlaceholderText("10")
        self.max_backups_input.setFixedWidth(80)
        backup_layout.addRow("Max Backups:", self.max_backups_input)

        layout.addWidget(backup_group)

        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setObjectName("secondary")
        reset_btn.clicked.connect(self._reset_to_defaults)
        buttons_layout.addWidget(reset_btn)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save_settings)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

    def _load_values(self):
        """Load current config values into the form."""
        self.output_dir_input.setText(self.config.get("output_dir", "music"))
        self.format_combo.setCurrentText(self.config.get("audio_format", "mp3"))
        self.client_id_input.setText(self.config.get("spotify_client_id", ""))
        self.redirect_uri_input.setText(self.config.get("spotify_redirect_uri", "http://127.0.0.1:8888/callback"))
        self.sleep_input.setText(str(self.config.get("sleep_between", 5)))
        self.retry_input.setText(str(self.config.get("retry_attempts", 3)))
        self.metadata_check.setChecked(self.config.get("enable_metadata_embedding", True))
        self.template_combo.setCurrentText(self.config.get("metadata_template", "basic"))
        self.musicbrainz_check.setChecked(self.config.get("enable_musicbrainz_lookup", True))
        self.backup_check.setChecked(self.config.get("auto_backup", True))
        self.max_backups_input.setText(str(self.config.get("max_backups", 10)))

    def _check_ffmpeg_status(self):
        """Check FFmpeg installation status."""
        available, message = check_ffmpeg_available()

        if available:
            self.ffmpeg_status_icon.setStyleSheet("color: #4caf50; font-size: 14px;")
            self.ffmpeg_status_label.setText(f"Installed: {message.replace('FFmpeg found at: ', '')}")
            self.ffmpeg_status_label.setStyleSheet("color: #4caf50;")
            self.ffmpeg_install_btn.setText("Reinstall")
        else:
            self.ffmpeg_status_icon.setStyleSheet("color: #ef5350; font-size: 14px;")
            self.ffmpeg_status_label.setText("Not installed")
            self.ffmpeg_status_label.setStyleSheet("color: #ef5350;")
            self.ffmpeg_install_btn.setText("Install FFmpeg")

    def _install_ffmpeg(self):
        """Start FFmpeg installation."""
        from gui.workers.ffmpeg_installer import FFmpegInstallerWorker

        # Confirm installation
        reply = QMessageBox.question(
            self,
            "Install FFmpeg",
            "This will download and install FFmpeg (~100MB).\n\n"
            "The installation is required for audio conversion.\n\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply != QMessageBox.Yes:
            return

        # Disable buttons during installation
        self.ffmpeg_install_btn.setEnabled(False)
        self.ffmpeg_refresh_btn.setEnabled(False)

        # Show progress
        self.ffmpeg_progress.setVisible(True)
        self.ffmpeg_progress_label.setVisible(True)
        self.ffmpeg_progress.setValue(0)

        # Create and start worker
        self.ffmpeg_worker = FFmpegInstallerWorker()
        self.ffmpeg_worker.progress.connect(self._on_ffmpeg_progress)
        self.ffmpeg_worker.finished.connect(self._on_ffmpeg_finished)
        self.ffmpeg_worker.start()

    def _on_ffmpeg_progress(self, percent: int, message: str):
        """Handle FFmpeg installation progress."""
        self.ffmpeg_progress.setValue(percent)
        self.ffmpeg_progress_label.setText(message)

    def _on_ffmpeg_finished(self, success: bool, message: str):
        """Handle FFmpeg installation completion."""
        # Hide progress
        self.ffmpeg_progress.setVisible(False)
        self.ffmpeg_progress_label.setVisible(False)

        # Re-enable buttons
        self.ffmpeg_install_btn.setEnabled(True)
        self.ffmpeg_refresh_btn.setEnabled(True)

        # Show result
        if success:
            QMessageBox.information(self, "Installation Complete", message)
            self._check_ffmpeg_status()
        else:
            QMessageBox.warning(self, "Installation Failed", message)
            self._check_ffmpeg_status()

        # Clean up worker
        self.ffmpeg_worker = None

    def _browse_output_dir(self):
        """Open folder browser for output directory."""
        current_dir = self.output_dir_input.text() or os.path.expanduser("~")

        # Make sure the current dir exists, otherwise use home
        if not os.path.isdir(current_dir):
            current_dir = os.path.expanduser("~")

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            current_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            # Use the selected folder path
            self.output_dir_input.setText(folder)
            # Auto-save to make sure it takes effect
            self._update_config_value("output_dir", folder)

    def _update_config_value(self, key: str, value):
        """Update a single config value and save."""
        self.config[key] = value
        try:
            save_config(self.config)
        except Exception:
            pass  # Silently fail for individual updates

    def _save_settings(self):
        """Save current settings to config."""
        try:
            # Update config dict
            output_dir = self.output_dir_input.text().strip()
            if not output_dir:
                output_dir = "music"

            self.config["output_dir"] = output_dir
            self.config["audio_format"] = self.format_combo.currentText()
            self.config["spotify_client_id"] = self.client_id_input.text()
            self.config["sleep_between"] = int(self.sleep_input.text() or 5)
            self.config["retry_attempts"] = int(self.retry_input.text() or 3)
            self.config["enable_metadata_embedding"] = self.metadata_check.isChecked()
            self.config["metadata_template"] = self.template_combo.currentText()
            self.config["enable_musicbrainz_lookup"] = self.musicbrainz_check.isChecked()
            self.config["auto_backup"] = self.backup_check.isChecked()
            self.config["max_backups"] = int(self.max_backups_input.text() or 10)

            # Validate
            is_valid, errors = validate_config(self.config)
            if not is_valid:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Invalid settings:\n" + "\n".join(errors)
                )
                return

            # Create output directory if it doesn't exist
            if output_dir and not os.path.isabs(output_dir):
                # For relative paths, create from current working directory
                os.makedirs(output_dir, exist_ok=True)
            elif output_dir:
                # For absolute paths, try to create
                os.makedirs(output_dir, exist_ok=True)

            # Save
            save_config(self.config)
            self.config_saved.emit()
            QMessageBox.information(self, "Success", "Settings saved successfully!")

        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid value: {e}")
        except PermissionError:
            QMessageBox.warning(
                self,
                "Permission Error",
                f"Cannot create output directory:\n{output_dir}\n\n"
                "Please choose a different location."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for key, value in DEFAULT_CONFIG.items():
                self.config[key] = value
            self._load_values()
            QMessageBox.information(self, "Reset", "Settings reset to defaults.")
