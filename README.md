# 🎙️ RockPod

**A modern podcast sync utility for Rockbox iPods**

RockPod automatically downloads podcasts from RSS feeds and syncs them to your Rockbox-enabled iPod, complete with metadata, cover art, and a sleek macOS menu bar interface.

## ⚠️ Disclaimer

**This software is untested and provided as-is. Use at your own risk.** The author is not responsible for any damage to your iPod, computer, data loss, or other issues that may arise from using this software. Please ensure you have proper backups before using RockPod.

![RockPod Demo](https://img.shields.io/badge/Platform-macOS-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![License](https://img.shields.io/badge/License-MIT-orange)

## ✨ Features

- 🚀 **Parallel Downloads**: Download multiple podcast episodes simultaneously (3x faster)
- 🎯 **Smart Detection**: Auto-detects Rockbox iPods when connected
- 🏷️ **Rich Metadata**: Automatically tags episodes with titles, artwork, and podcast info
- 📱 **Menu Bar App**: Native macOS menu bar interface with progress indicators
- ⚙️ **Configurable**: Customize feeds, episode limits, and sync preferences
- 🔄 **Duplicate Prevention**: Never downloads the same episode twice
- 🧹 **Auto Cleanup**: Removes old episodes based on your preferences
- 🎵 **Music Inbox**: Also syncs music from a designated folder

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/jcompanion/rockpod.git
cd rockpod

# Run the setup script
./setup.sh
```

### 2. Configure Your Podcasts

Edit `config.yaml` to add your favorite podcasts:

```yaml
podcasts:
  - url: 'https://feeds.simplecast.com/54nAGcIl'
    folder: 'The Daily'
    keep_last: 7
  - url: 'https://feeds.megaphone.fm/hubermanlab'
    folder: 'Huberman Lab'
    keep_last: 5

library_dir: '~/RockPod/library'
music_inbox: '~/RockPod/music_inbox'
keep_last: 10  # Default episode limit
```

### 3. Launch RockPod

Choose your preferred launch method:

#### Option A: Double-Click App (Recommended)
- Double-click `RockPod.app` for a native macOS experience

#### Option B: Terminal Command
- Double-click `RockPod.command` to see detailed output

#### Option C: Quick Launch Script  
- Double-click `launch_rockpod.sh` for minimal startup

### 4. Connect Your iPod

1. Connect your Rockbox-enabled iPod
2. The menu bar icon will change from 🎙️ to 📱
3. Click "📱 Sync to iPod" to start syncing

## 🎛️ Menu Bar Interface

The RockPod menu bar provides these options:

- **📱 Sync to iPod**: Download new episodes and sync to iPod
- **📡 Fetch Podcasts**: Download new episodes only (no iPod required)  
- **🔍 Check iPod**: Verify iPod connection and storage info
- **📂 Open Library**: Open local podcast library in Finder
- **⚙️ Settings**: Edit configuration file
- **📊 Status**: View sync statistics and episode counts

## 🔧 Command Line Usage

```bash
# Download new episodes only
python rockpod_sync.py fetch

# Download episodes and sync to iPod
python rockpod_sync.py sync

# Sync existing library to iPod (no downloads)
python rockpod_sync.py sync-only
```

## 📋 Requirements

- **macOS 10.9+**
- **Python 3.8+** 
- **Rockbox-enabled iPod** (any model with Rockbox firmware)
- **Internet connection** for podcast downloads

### Python Dependencies
All automatically installed by `setup.sh`:
- `requests` - HTTP requests for downloads
- `feedparser` - RSS feed parsing  
- `mutagen` - Audio file tagging
- `tqdm` - Progress bars
- `PyYAML` - Configuration file parsing
- `rumps` - macOS menu bar integration

## 🎵 Supported Audio Formats

RockPod handles all major podcast formats:
- **MP3** (.mp3) - Most common
- **M4A/AAC** (.m4a, .aac) - Apple formats
- **MP4** (.mp4) - Video podcasts (audio only)
- **OGG** (.ogg) - Open format
- **FLAC** (.flac) - Lossless

## 🔒 Privacy & Data

RockPod is privacy-focused:
- ✅ All data stays on your computer
- ✅ No telemetry or tracking
- ✅ Direct RSS feed access (no third-party services)
- ✅ Open source and auditable

## 🐛 Troubleshooting

### iPod Not Detected
- Ensure iPod is mounted and visible in `/Volumes/`
- Verify Rockbox is installed (`.rockbox` folder exists)
- Check USB connection and try a different port

### Menu Bar App Crashes
- Check logs: `tail -f /tmp/rockpod.error.log`
- Restart with: `./launch_rockpod.sh`
- Report issues on GitHub with log details

### Download Failures
- Verify internet connection
- Check RSS feed URLs are accessible
- Some feeds may have geographic restrictions

### Permission Errors
- Ensure write access to library directory
- Check iPod isn't mounted read-only
- Run: `chmod -R 755 ~/RockPod/`

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Development Setup

```bash
git clone https://github.com/jcompanion/rockpod.git
cd rockpod
./setup.sh
```

### Areas for Contribution
- 🌍 **Cross-platform support** (Linux, Windows)
- 🎨 **UI improvements** and themes
- 📱 **Additional iPod models** and firmware support
- 🔧 **New features** and podcast sources
- 🐛 **Bug fixes** and performance improvements
- 📖 **Documentation** and tutorials

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Rockbox Project** - For the amazing open-source iPod firmware
- **feedparser** - Excellent RSS parsing library  
- **rumps** - Simple macOS menu bar framework
- **tqdm** - Beautiful progress bars

## 🔗 Links

- **GitHub**: [https://github.com/jcompanion/rockpod](https://github.com/jcompanion/rockpod)
- **Issues**: [Report bugs and request features](https://github.com/jcompanion/rockpod/issues)
- **Rockbox**: [https://www.rockbox.org/](https://www.rockbox.org/)

---

**Made with ❤️ for the iPod and podcast community**