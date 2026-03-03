# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-03-03

### Added
- **yt-dlp Update Checker & Installer**: Implemented a comprehensive update system for yt-dlp with:
  - Automatic update detection through the update checker module
  - In-app notifications to alert users when updates are available
  - One-click installer for seamless yt-dlp updates
  - New `ytdlp_updater.py` worker module handling update logic in GUI thread

### Changed
- **Settings View**: Now automatically reloads configuration on save and updates the UI to reflect changes immediately
- **Spotify Integration**: Refactored token expiration checking to use the TokenManager, improving code maintainability and centralizing token lifecycle management
- **Main Window**: Updated to support the new yt-dlp update checker integration

### Why
These changes were made to improve user experience and code quality:
1. Users can now keep yt-dlp updated without manual intervention, ensuring access to the latest features and bug fixes
2. Settings changes take immediate effect without requiring app restart (I think you'll have to reload the app after installing yt-dlp because visually it shows not installed)
3. Centralized token management through TokenManager reduces duplication and potential bugs in token handling across different parts of the application
4. when you open the app, there will be some quick cli openings which is a bit scary but don't worry, it's just small scripts to check for things if they are there or not.

## [1.0.0] - 2026-01-01

### Added
- Initial stable release of Harmoni
- GUI version 1.0.0 with core features
- Initial yt-dlp update checker foundation
