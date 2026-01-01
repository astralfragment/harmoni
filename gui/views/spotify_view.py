"""Spotify view for browsing playlists and downloading tracks."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QListWidget, QListWidgetItem,
    QSplitter, QGroupBox, QProgressBar, QMessageBox,
    QCheckBox, QAbstractItemView, QFrame
)
from PySide6.QtCore import Qt, Signal

from gui.workers.download_queue import DownloadQueue
from gui.workers.spotify_worker import SpotifyWorker
from gui.dialogs.oauth_dialog import SpotifyOAuthDialog
from spotify_api.auth import SpotifyPKCEAuth


class SpotifyView(QWidget):
    """View for Spotify playlist browsing and track selection."""

    connection_changed = Signal(bool)  # Emits connection status

    def __init__(self, config: dict, queue: DownloadQueue, parent=None):
        super().__init__(parent)
        self.config = config
        self.queue = queue
        self.worker = None
        self.current_tracks = []
        self._setup_ui()
        self._check_connection()

    def _setup_ui(self):
        """Set up the Spotify UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Spotify")
        title.setObjectName("title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Connection status
        self.status_label = QLabel("Not connected")
        self.status_label.setObjectName("subtitle")
        header_layout.addWidget(self.status_label)

        self.connect_btn = QPushButton("Connect to Spotify")
        self.connect_btn.clicked.connect(self._show_oauth_dialog)
        header_layout.addWidget(self.connect_btn)

        layout.addLayout(header_layout)

        # Progress bar for loading
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Playlists
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)

        playlists_label = QLabel("Playlists")
        playlists_label.setObjectName("section")
        left_layout.addWidget(playlists_label)

        # Refresh button
        refresh_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setObjectName("secondary")
        self.refresh_btn.clicked.connect(self._refresh_playlists)
        self.refresh_btn.setEnabled(False)
        refresh_layout.addWidget(self.refresh_btn)

        self.liked_btn = QPushButton("Liked Songs")
        self.liked_btn.setObjectName("secondary")
        self.liked_btn.clicked.connect(self._fetch_liked_songs)
        self.liked_btn.setEnabled(False)
        refresh_layout.addWidget(self.liked_btn)

        refresh_layout.addStretch()
        left_layout.addLayout(refresh_layout)

        # Playlist list
        self.playlist_list = QListWidget()
        self.playlist_list.itemClicked.connect(self._on_playlist_selected)
        left_layout.addWidget(self.playlist_list)

        splitter.addWidget(left_panel)

        # Right panel - Tracks
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)

        # Tracks header
        tracks_header = QHBoxLayout()
        self.tracks_label = QLabel("Tracks")
        self.tracks_label.setObjectName("section")
        tracks_header.addWidget(self.tracks_label)

        tracks_header.addStretch()

        # Select all checkbox
        self.select_all_check = QCheckBox("Select All")
        self.select_all_check.stateChanged.connect(self._toggle_select_all)
        tracks_header.addWidget(self.select_all_check)

        right_layout.addLayout(tracks_header)

        # Tracks table
        self.tracks_table = QTableWidget()
        self.tracks_table.setColumnCount(4)
        self.tracks_table.setHorizontalHeaderLabels(["", "Artist", "Track", "Album"])
        self.tracks_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.tracks_table.setColumnWidth(0, 40)
        self.tracks_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tracks_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tracks_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tracks_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tracks_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tracks_table.verticalHeader().setVisible(False)
        right_layout.addWidget(self.tracks_table)

        # Add to queue button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.track_count_label = QLabel("0 tracks selected")
        btn_layout.addWidget(self.track_count_label)

        self.add_btn = QPushButton("Add to Download Queue")
        self.add_btn.clicked.connect(self._add_selected_to_queue)
        self.add_btn.setEnabled(False)
        btn_layout.addWidget(self.add_btn)

        right_layout.addLayout(btn_layout)

        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([300, 700])

        layout.addWidget(splitter, 1)

    def _check_connection(self):
        """Check if we have a valid Spotify token."""
        auth = SpotifyPKCEAuth(self.config)
        token = auth.load_cached_token()

        if token and token.access_token:
            # Check if expired
            if token.is_expired():
                if token.refresh_token:
                    try:
                        auth.refresh_access_token(refresh_token=token.refresh_token)
                        self._set_connected(True)
                        return
                    except Exception:
                        pass
                self._set_connected(False)
            else:
                self._set_connected(True)
        else:
            self._set_connected(False)

    def _set_connected(self, connected: bool):
        """Update UI based on connection status."""
        if connected:
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: #1db954;")
            self.connect_btn.setText("Reconnect")
            self.refresh_btn.setEnabled(True)
            self.liked_btn.setEnabled(True)
            self.connection_changed.emit(True)
            # Auto-refresh playlists
            self._refresh_playlists()
        else:
            self.status_label.setText("Not connected")
            self.status_label.setStyleSheet("")
            self.connect_btn.setText("Connect to Spotify")
            self.refresh_btn.setEnabled(False)
            self.liked_btn.setEnabled(False)
            self.connection_changed.emit(False)

    def _show_oauth_dialog(self):
        """Show the OAuth login dialog."""
        dialog = SpotifyOAuthDialog(self.config, self)
        dialog.auth_completed.connect(self._on_auth_completed)
        dialog.exec()

    def _on_auth_completed(self, success: bool, message: str):
        """Handle OAuth completion."""
        if success:
            self._set_connected(True)
        else:
            QMessageBox.warning(self, "Authentication Failed", message)

    def _refresh_playlists(self):
        """Refresh the playlist list."""
        if self.worker and self.worker.isRunning():
            return

        self.worker = SpotifyWorker(self.config)
        self.worker.playlists_loaded.connect(self._on_playlists_loaded)
        self.worker.error.connect(self._on_error)
        self.worker.progress.connect(self._on_progress)
        self.worker.fetch_playlists()

        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.refresh_btn.setEnabled(False)

    def _on_playlists_loaded(self, playlists: list):
        """Handle playlists loaded."""
        self.progress_bar.hide()
        self.refresh_btn.setEnabled(True)

        self.playlist_list.clear()
        for playlist in playlists:
            item = QListWidgetItem(f"{playlist['name']} ({playlist['tracks_total']} tracks)")
            item.setData(Qt.UserRole, playlist)
            self.playlist_list.addItem(item)

    def _on_playlist_selected(self, item: QListWidgetItem):
        """Handle playlist selection."""
        playlist = item.data(Qt.UserRole)
        if not playlist:
            return

        if self.worker and self.worker.isRunning():
            return

        self.worker = SpotifyWorker(self.config)
        self.worker.tracks_loaded.connect(self._on_tracks_loaded)
        self.worker.error.connect(self._on_error)
        self.worker.progress.connect(self._on_progress)
        self.worker.fetch_playlist_tracks(playlist["id"], playlist["name"])

        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.tracks_label.setText(f"Tracks - {playlist['name']}")

    def _fetch_liked_songs(self):
        """Fetch user's liked songs."""
        if self.worker and self.worker.isRunning():
            return

        self.worker = SpotifyWorker(self.config)
        self.worker.liked_songs_loaded.connect(self._on_liked_songs_loaded)
        self.worker.error.connect(self._on_error)
        self.worker.progress.connect(self._on_progress)
        self.worker.fetch_liked_songs()

        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.liked_btn.setEnabled(False)

    def _on_liked_songs_loaded(self, tracks: list):
        """Handle liked songs loaded."""
        self.progress_bar.hide()
        self.liked_btn.setEnabled(True)
        self.tracks_label.setText("Tracks - Liked Songs")
        self._populate_tracks(tracks)

    def _on_tracks_loaded(self, playlist_id: str, tracks: list):
        """Handle tracks loaded."""
        self.progress_bar.hide()
        self._populate_tracks(tracks)

    def _populate_tracks(self, tracks: list):
        """Populate the tracks table."""
        self.current_tracks = tracks
        self.tracks_table.setRowCount(0)
        self.select_all_check.setChecked(False)

        for track in tracks:
            row = self.tracks_table.rowCount()
            self.tracks_table.insertRow(row)

            # Checkbox
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self._update_selection_count)
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.tracks_table.setCellWidget(row, 0, checkbox_widget)

            # Track data
            self.tracks_table.setItem(row, 1, QTableWidgetItem(track.get("artist", "")))
            self.tracks_table.setItem(row, 2, QTableWidgetItem(track.get("track", "")))
            self.tracks_table.setItem(row, 3, QTableWidgetItem(track.get("album", "")))

        self._update_selection_count()
        self.add_btn.setEnabled(len(tracks) > 0)

    def _toggle_select_all(self, state: int):
        """Toggle all checkboxes."""
        checked = state == Qt.Checked
        for row in range(self.tracks_table.rowCount()):
            widget = self.tracks_table.cellWidget(row, 0)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(checked)

    def _update_selection_count(self):
        """Update the selected track count label."""
        count = self._get_selected_count()
        self.track_count_label.setText(f"{count} tracks selected")

    def _get_selected_count(self) -> int:
        """Get number of selected tracks."""
        count = 0
        for row in range(self.tracks_table.rowCount()):
            widget = self.tracks_table.cellWidget(row, 0)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    count += 1
        return count

    def _get_selected_tracks(self) -> list:
        """Get list of selected tracks."""
        selected = []
        for row in range(self.tracks_table.rowCount()):
            widget = self.tracks_table.cellWidget(row, 0)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    if row < len(self.current_tracks):
                        selected.append(self.current_tracks[row])
        return selected

    def _add_selected_to_queue(self):
        """Add selected tracks to download queue."""
        tracks = self._get_selected_tracks()
        if not tracks:
            QMessageBox.information(self, "No Selection", "Please select tracks to download.")
            return

        # Get playlist name for the queue
        playlist_name = self.tracks_label.text().replace("Tracks - ", "")

        # Add to queue
        self.queue.add_tracks(tracks, playlist=playlist_name)

        QMessageBox.information(
            self,
            "Added to Queue",
            f"Added {len(tracks)} tracks to download queue.\n\n"
            "Go to Downloads to start downloading."
        )

    def _on_progress(self, message: str, current: int, total: int):
        """Handle progress updates."""
        if total > 0:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(current)
        else:
            self.progress_bar.setRange(0, 0)

    def _on_error(self, message: str):
        """Handle errors."""
        self.progress_bar.hide()
        self.refresh_btn.setEnabled(True)
        self.liked_btn.setEnabled(True)
        QMessageBox.warning(self, "Error", message)
