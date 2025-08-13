#!/usr/bin/env python3
"""
RockPod Sync - Podcast syncing tool for Rockbox iPods
Fetches podcasts from RSS feeds and syncs them to your Rockbox device
"""

import os
import sys
import json
import shutil
import re
import subprocess
import concurrent.futures
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from urllib.parse import urlparse

import yaml
import feedparser
import requests
from tqdm import tqdm
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, APIC, ID3NoHeaderError, TIT2, TALB, TPE1, TCON, TDRC
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4, MP4Cover

# Constants
APP_STATE = "state.json"
SAFE_CHARS = r"[^a-zA-Z0-9\-\._ ]"
USER_AGENT = "RockPod/1.0 (Podcast Sync for Rockbox)"


class RockPodSync:
    def __init__(self):
        self.config = self.load_config()
        self.library_dir = Path(self.config.get("library_dir", "~/RockPod/library")).expanduser()
        self.state_file = self.library_dir / APP_STATE
        self.state = self.load_state()
        
    def load_config(self) -> dict:
        """Load configuration from config.yaml"""
        config_path = Path(__file__).with_name("config.yaml")
        if not config_path.exists():
            print("Error: config.yaml not found. Please create it next to this script.")
            sys.exit(1)
        
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def load_state(self) -> dict:
        """Load state tracking (downloaded episodes)"""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text("utf-8"))
            except Exception:
                pass
        return {"feeds": {}, "version": "1.0"}
    
    def save_state(self):
        """Save state tracking"""
        self.library_dir.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2), encoding="utf-8")
    
    @staticmethod
    def slugify(text: str, maxlen: int = 120) -> str:
        """Create filesystem-safe names"""
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(SAFE_CHARS, "_", text)
        return text[:maxlen].rstrip("_.")
    
    def detect_ipod(self) -> Optional[Path]:
        """Auto-detect Rockbox iPod by looking for /.rockbox folder"""
        volumes = Path("/Volumes")
        if not volumes.exists():
            return None
        
        # Check for specific label if configured
        ipod_label = self.config.get("ipod_label", "").strip()
        if ipod_label:
            ipod_path = volumes / ipod_label
            if ipod_path.exists() and (ipod_path / ".rockbox").exists():
                return ipod_path
        
        # Auto-detect any volume with /.rockbox
        for volume in volumes.iterdir():
            try:
                if volume.is_dir() and (volume / ".rockbox").exists():
                    return volume
            except PermissionError:
                continue
        
        return None
    
    def download_file(self, url: str, dest: Path, desc: str = None) -> bool:
        """Download file with progress bar"""
        try:
            headers = {"User-Agent": USER_AGENT}
            with requests.get(url, stream=True, timeout=60, headers=headers) as r:
                r.raise_for_status()
                total_size = int(r.headers.get("content-length", 0))
                
                # Use temporary file during download
                temp_file = dest.with_suffix(dest.suffix + ".tmp")
                
                with open(temp_file, "wb") as f:
                    with tqdm(
                        total=total_size,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=desc or dest.name,
                        ncols=80,
                        file=sys.stdout  # Output to stdout instead of stderr
                    ) as pbar:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                
                # Move to final location
                temp_file.rename(dest)
                return True
                
        except Exception as e:
            print(f"  ⚠ Download failed: {e}")
            if temp_file.exists():
                temp_file.unlink()
            return False
    
    def get_file_extension(self, url: str, mime_type: str = None) -> str:
        """Determine file extension from URL or MIME type"""
        # Try from URL path
        parsed = urlparse(url)
        path = Path(parsed.path)
        if path.suffix:
            return path.suffix.lower()
        
        # Try from MIME type
        if mime_type:
            mime_map = {
                "audio/mpeg": ".mp3",
                "audio/mp3": ".mp3",
                "audio/mp4": ".m4a",
                "audio/aac": ".aac",
                "audio/ogg": ".ogg",
                "audio/flac": ".flac",
            }
            if mime_type in mime_map:
                return mime_map[mime_type]
        
        # Default to mp3
        return ".mp3"
    
    def find_cover_url(self, entry: Any, feed: Any) -> Optional[str]:
        """Extract cover art URL from feed or entry"""
        # Try entry-level artwork first
        candidates = [
            getattr(entry, "itunes_image", None),
            getattr(entry, "image", None),
        ]
        
        # Then try feed-level artwork
        if hasattr(feed, "feed"):
            candidates.extend([
                getattr(feed.feed, "itunes_image", None),
                getattr(feed.feed, "image", None),
            ])
        
        for candidate in candidates:
            if isinstance(candidate, dict) and "href" in candidate:
                return candidate["href"]
            elif isinstance(candidate, str) and candidate.startswith("http"):
                return candidate
        
        return None
    
    def download_cover(self, url: str) -> Optional[bytes]:
        """Download cover art"""
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": USER_AGENT})
            r.raise_for_status()
            return r.content
        except Exception:
            return None
    
    def tag_audio_file(
        self, 
        filepath: Path, 
        title: str, 
        artist: str = None, 
        album: str = None,
        date: str = None,
        cover_data: bytes = None
    ):
        """Add ID3/MP4 tags to audio file"""
        ext = filepath.suffix.lower()
        
        try:
            if ext in [".mp3"]:
                # Handle MP3 with ID3 tags
                try:
                    audio = EasyID3(str(filepath))
                except ID3NoHeaderError:
                    # Create ID3 tags if they don't exist
                    audio_file = MutagenFile(str(filepath), easy=True)
                    audio_file.add_tags()
                    audio = EasyID3(str(filepath))
                
                audio["title"] = title
                if artist:
                    audio["artist"] = artist
                if album:
                    audio["album"] = album
                audio["genre"] = "Podcast"
                if date:
                    audio["date"] = date[:10]
                audio.save()
                
                # Add cover art
                if cover_data:
                    id3 = ID3(str(filepath))
                    id3["APIC"] = APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3,  # Cover (front)
                        desc="Cover",
                        data=cover_data
                    )
                    id3.save(v2_version=3)
                    
            elif ext in [".m4a", ".mp4", ".aac"]:
                # Handle MP4/M4A/AAC
                mp4 = MP4(str(filepath))
                mp4["\xa9nam"] = title
                if artist:
                    mp4["\xa9ART"] = artist
                if album:
                    mp4["\xa9alb"] = album
                mp4["\xa9gen"] = "Podcast"
                if date:
                    mp4["\xa9day"] = date[:10]
                if cover_data:
                    mp4["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]
                mp4.save()
                
            else:
                # Try generic tagging for other formats
                audio = MutagenFile(str(filepath), easy=True)
                if audio is not None:
                    audio["title"] = title
                    if artist:
                        audio["artist"] = artist
                    if album:
                        audio["album"] = album
                    audio["genre"] = "Podcast"
                    audio.save()
                    
        except Exception as e:
            print(f"  ⚠ Tagging failed: {e}")
    
    def fetch_podcasts(self, progress_callback=None):
        """Fetch new episodes from all configured podcast feeds"""
        print("\n🎙️  Fetching podcasts...")
        
        feeds_state = self.state.setdefault("feeds", {})
        
        # First pass: check all feeds and collect new episodes to download
        episodes_to_download = []
        
        for feed_config in self.config.get("podcasts", []):
            url = feed_config["url"]
            folder_name = feed_config.get("folder", "Podcast")
            keep_last = feed_config.get("keep_last", self.config.get("keep_last", 10))
            
            print(f"\n📡 Checking: {folder_name}")
            print(f"   URL: {url}")
            
            # Parse RSS feed
            feed = feedparser.parse(url)
            if feed.bozo:
                print(f"  ⚠ Feed parse error: {feed.bozo_exception}")
                continue
            
            # Get or create show directory
            show_title = folder_name or getattr(feed.feed, "title", "Unknown Podcast")
            show_dir = self.library_dir / "Podcasts" / self.slugify(show_title)
            show_dir.mkdir(parents=True, exist_ok=True)
            
            # Track downloaded episodes for this feed
            known_episodes = set(feeds_state.get(url, []))
            new_episodes = []
            
            # Process entries (newest first)
            for entry in feed.entries[:keep_last]:
                # Get unique ID for episode
                guid = (
                    getattr(entry, "id", None) or 
                    getattr(entry, "guid", None) or 
                    getattr(entry, "link", None)
                )
                if not guid:
                    continue
                
                # Skip if already downloaded
                if guid in known_episodes:
                    continue
                
                # Find audio enclosure
                enclosure = None
                for link in getattr(entry, "links", []):
                    if link.get("rel") == "enclosure" and link.get("href"):
                        enclosure = link
                        break
                
                if not enclosure:
                    continue
                
                # Prepare episode info for download
                episode_info = {
                    'guid': guid,
                    'url': url,
                    'audio_url': enclosure["href"],
                    'mime_type': enclosure.get("type"),
                    'title': getattr(entry, "title", "Unknown Episode"),
                    'published': getattr(entry, "published", None),
                    'show_title': show_title,
                    'show_dir': show_dir,
                    'entry': entry,
                    'feed': feed,
                    'artist': (
                        getattr(entry, "author", None) or
                        getattr(feed.feed, "author", None) or
                        show_title
                    )
                }
                
                new_episodes.append(episode_info)
                episodes_to_download.append(episode_info)
            
            if new_episodes:
                print(f"  📥 {len(new_episodes)} new episode(s) found")
            else:
                print(f"  ✓ No new episodes")
        
        # Second pass: download all episodes concurrently
        if episodes_to_download:
            print(f"\n⬇️  Downloading {len(episodes_to_download)} episodes concurrently...")
            
            # Thread-safe progress tracking
            progress_lock = threading.Lock()
            completed_count = 0
            
            def download_episode(episode_info):
                nonlocal completed_count
                
                # Prepare file info
                ext = self.get_file_extension(episode_info['audio_url'], episode_info['mime_type'])
                
                # Create filename with date prefix if available
                date_prefix = ""
                if episode_info['published']:
                    try:
                        pub_date = datetime(*episode_info['entry'].published_parsed[:6])
                        date_prefix = pub_date.strftime("%Y-%m-%d ")
                    except:
                        pass
                
                filename = f"{date_prefix}{self.slugify(episode_info['title'])}{ext}"
                filepath = episode_info['show_dir'] / filename
                
                # Download episode
                if progress_callback:
                    with progress_lock:
                        progress_callback(f"⬇️ {episode_info['title'][:25]}...")
                
                success = self.download_file(
                    episode_info['audio_url'], 
                    filepath, 
                    desc=f"[{episode_info['show_title'][:15]}] {episode_info['title'][:30]}"
                )
                
                if success:
                    # Download cover art
                    cover_url = self.find_cover_url(episode_info['entry'], episode_info['feed'])
                    cover_data = self.download_cover(cover_url) if cover_url else None
                    
                    # Tag the file
                    self.tag_audio_file(
                        filepath,
                        title=episode_info['title'],
                        artist=episode_info['artist'],
                        album=episode_info['show_title'],
                        date=episode_info['published'],
                        cover_data=cover_data
                    )
                    
                    with progress_lock:
                        completed_count += 1
                        print(f"  ✅ [{completed_count}/{len(episodes_to_download)}] {episode_info['title']}")
                    
                    return episode_info['guid'], episode_info['url']
                else:
                    print(f"  ❌ Failed: {episode_info['title']}")
                    return None
            
            # Download episodes in parallel (max 3 concurrent downloads)
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_episode = {
                    executor.submit(download_episode, episode): episode 
                    for episode in episodes_to_download
                }
                
                # Update state as downloads complete
                for future in concurrent.futures.as_completed(future_to_episode):
                    result = future.result()
                    if result:
                        guid, feed_url = result
                        # Mark as downloaded
                        known_episodes = set(feeds_state.get(feed_url, []))
                        known_episodes.add(guid)
                        feeds_state[feed_url] = list(known_episodes)
        
        # Third pass: clean up old episodes
        print("\n🧹 Cleaning up old episodes...")
        for feed_config in self.config.get("podcasts", []):
            folder_name = feed_config.get("folder", "Podcast")
            keep_last = feed_config.get("keep_last", self.config.get("keep_last", 10))
            
            show_dir = self.library_dir / "Podcasts" / self.slugify(folder_name)
            if show_dir.exists():
                episodes = sorted(
                    show_dir.glob("*.*"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )
                
                for old_episode in episodes[keep_last:]:
                    print(f"  🗑️  Removing old: {old_episode.name}")
                    old_episode.unlink()
        
        self.save_state()
        print(f"\n✅ Podcast fetch complete! Downloaded {len(episodes_to_download)} new episodes")
    
    def sync_to_ipod(self):
        """Sync podcasts and music to iPod"""
        ipod = self.detect_ipod()
        if not ipod:
            print("\n❌ No Rockbox iPod detected!")
            print("   Make sure your iPod is connected and mounted.")
            print("   Looking for a volume with /.rockbox folder.")
            return False
        
        print(f"\n💾 iPod detected: {ipod}")
        
        # Sync podcasts
        src_podcasts = self.library_dir / "Podcasts"
        if src_podcasts.exists():
            dst_podcasts = ipod / "Podcasts"
            print(f"\n📁 Syncing podcasts to {dst_podcasts}")
            self.sync_directory(src_podcasts, dst_podcasts)
        
        # Sync music inbox
        music_inbox = self.config.get("music_inbox")
        if music_inbox:
            inbox_path = Path(music_inbox).expanduser()
            if inbox_path.exists():
                dst_music = ipod / "Music"
                print(f"\n🎵 Syncing music inbox to {dst_music}")
                self.sync_directory(inbox_path, dst_music)
        
        print("\n✅ Sync complete!")
        print("\n💡 Tip: In Rockbox, go to:")
        print("   Database → Update Now")
        print("   to refresh the music database with new files.")
        
        return True
    
    def sync_directory(self, src: Path, dst: Path):
        """Sync source directory to destination"""
        dst.mkdir(parents=True, exist_ok=True)
        
        files_copied = 0
        files_skipped = 0
        
        for src_file in src.rglob("*"):
            if src_file.is_file() and not src_file.name.startswith("."):
                rel_path = src_file.relative_to(src)
                dst_file = dst / rel_path
                
                # Check if we need to copy
                needs_copy = (
                    not dst_file.exists() or
                    src_file.stat().st_mtime > dst_file.stat().st_mtime or
                    src_file.stat().st_size != dst_file.stat().st_size
                )
                
                if needs_copy:
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dst_file)
                    files_copied += 1
                    print(f"  ✓ {rel_path}")
                else:
                    files_skipped += 1
        
        print(f"  📊 Copied: {files_copied}, Skipped: {files_skipped}")
    
    def run(self, command: str = "sync"):
        """Main entry point"""
        commands = {
            "fetch": self.fetch_podcasts,
            "sync": lambda: (self.fetch_podcasts(), self.sync_to_ipod()),
            "sync-only": self.sync_to_ipod,
        }
        
        if command in commands:
            commands[command]()
        else:
            print("Usage:")
            print("  python rockpod_sync.py fetch      # Fetch new episodes only")
            print("  python rockpod_sync.py sync       # Fetch + sync to iPod (default)")
            print("  python rockpod_sync.py sync-only  # Sync to iPod without fetching")
            sys.exit(1)


def main():
    """Main entry point"""
    command = sys.argv[1] if len(sys.argv) > 1 else "sync"
    
    try:
        syncer = RockPodSync()
        syncer.run(command)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()