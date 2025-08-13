#!/usr/bin/env python3
"""
RockPod Menu Bar App - macOS menu bar interface for RockPod Sync
Provides quick access to podcast syncing from the menu bar
"""

import os
import sys
import subprocess
import threading
import json
from pathlib import Path
from datetime import datetime

try:
    import rumps
except ImportError:
    print("Error: rumps not installed. Install with: pip install rumps")
    sys.exit(1)

# Try to import the main sync module
try:
    from rockpod_sync import RockPodSync
except ImportError:
    print("Error: rockpod_sync.py not found in the same directory")
    sys.exit(1)


class RockPodMenuApp(rumps.App):
    """Menu bar app for RockPod sync"""
    
    def __init__(self):
        super(RockPodMenuApp, self).__init__(
            name="RockPod",
            icon=None,  # Use text instead of icon
            quit_button="Quit RockPod"
        )
        
        # Initialize sync manager
        try:
            self.syncer = RockPodSync()
            self.connected = False
            self.last_sync = self.load_last_sync()
            self.is_syncing = False
            self.sync_progress = ""
            self.animation_index = 0
            self.animation_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            
            # Set up menu
            self.menu = [
                rumps.MenuItem("📱 Sync to iPod", callback=self.sync_to_ipod),
                rumps.MenuItem("📡 Fetch Podcasts", callback=self.fetch_podcasts),
                None,  # Separator
                rumps.MenuItem("🔍 Check iPod", callback=self.check_ipod),
                rumps.MenuItem("📂 Open Library", callback=self.open_library),
                None,  # Separator
                rumps.MenuItem("⚙️ Settings", callback=self.open_config),
                rumps.MenuItem("📊 Status", callback=self.show_status),
                None,  # Separator
            ]
            
            # Start background iPod detection
            self.start_ipod_monitor()
            
            # Start animation timer
            self.start_animation_timer()
            
            # Update initial status
            self.update_status()
            
        except Exception as e:
            rumps.alert(
                title="Configuration Error",
                message=f"Could not load config.yaml: {e}\n\nPlease check your configuration."
            )
            rumps.quit_application()
    
    def load_last_sync(self) -> str:
        """Load last sync time from state"""
        try:
            if self.syncer.state_file.exists():
                state = json.loads(self.syncer.state_file.read_text())
                last_sync = state.get("last_sync")
                if last_sync:
                    dt = datetime.fromisoformat(last_sync)
                    return dt.strftime("%b %d, %I:%M %p")
        except:
            pass
        return "Never"
    
    def save_last_sync(self):
        """Save last sync time to state"""
        self.syncer.state["last_sync"] = datetime.now().isoformat()
        self.syncer.save_state()
        self.last_sync = datetime.now().strftime("%b %d, %I:%M %p")
    
    def start_ipod_monitor(self):
        """Monitor for iPod connection in background"""
        def monitor():
            import time
            while True:
                ipod = self.syncer.detect_ipod()
                old_connected = self.connected
                self.connected = ipod is not None
                
                if self.connected != old_connected:
                    self.update_status()
                    # Notifications removed to prevent crashes
                
                time.sleep(5)  # Check every 5 seconds
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def start_animation_timer(self):
        """Start timer for progress animation"""
        rumps.Timer(self.update_animation, 0.1).start()
    
    def update_animation(self, _):
        """Update animation in menu bar"""
        if self.is_syncing:
            spinner = self.animation_chars[self.animation_index]
            self.animation_index = (self.animation_index + 1) % len(self.animation_chars)
            self.title = f"{spinner} {self.sync_progress}"
        else:
            self.update_status()
    
    def update_status(self):
        """Update menu bar icon based on connection status"""
        if not self.is_syncing:
            if self.connected:
                self.title = "📱 RockPod"
            else:
                self.title = "🎙️ RockPod"
    
    @rumps.clicked("📱 Sync to iPod")
    def sync_to_ipod(self, _):
        """Sync podcasts to iPod"""
        if not self.connected:
            rumps.alert(
                title="No iPod Detected",
                message="Please connect your Rockbox iPod and try again."
            )
            return
        
        if self.is_syncing:
            rumps.alert(
                title="Already Syncing",
                message="A sync is already in progress. Please wait for it to complete."
            )
            return
        
        self.is_syncing = True
        self.sync_progress = "Starting..."
        
        def sync_thread():
            try:
                # Run sync as subprocess to avoid stdout issues
                import subprocess
                
                # Change to the script directory
                script_dir = Path(__file__).parent
                sync_script = script_dir / "rockpod_sync.py"
                
                self.sync_progress = "Syncing..."
                
                # Run the sync script with minimal output
                result = subprocess.run([
                    sys.executable, str(sync_script), "sync"
                ], 
                cwd=script_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
                )
                
                if result.returncode == 0:
                    self.save_last_sync()
                    
                    # Count episodes
                    podcast_dir = self.syncer.library_dir / "Podcasts"
                    episode_count = sum(1 for _ in podcast_dir.rglob("*.m*") if _.is_file())
                    
                    self.sync_progress = f"✅ {episode_count} eps"
                else:
                    self.sync_progress = "❌ Failed"
                    
            except subprocess.TimeoutExpired:
                self.sync_progress = "⏰ Timeout"
            except Exception:
                self.sync_progress = f"❌ Error"
            finally:
                # Clear sync status after 5 seconds
                import time
                time.sleep(5)
                self.is_syncing = False
                self.sync_progress = ""
        
        thread = threading.Thread(target=sync_thread)
        thread.start()
    
    @rumps.clicked("📡 Fetch Podcasts")
    def fetch_podcasts(self, _):
        """Fetch new podcast episodes"""
        if self.is_syncing:
            rumps.alert(
                title="Already Working",
                message="Please wait for the current operation to complete."
            )
            return
        
        self.is_syncing = True
        self.sync_progress = "Checking feeds..."
        
        def fetch_thread():
            try:
                # Run fetch as subprocess to avoid stdout issues
                import subprocess
                
                # Change to the script directory
                script_dir = Path(__file__).parent
                sync_script = script_dir / "rockpod_sync.py"
                
                self.sync_progress = "Fetching..."
                
                # Run the fetch script with minimal output
                result = subprocess.run([
                    sys.executable, str(sync_script), "fetch"
                ], 
                cwd=script_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    # Count episodes
                    podcast_dir = self.syncer.library_dir / "Podcasts"
                    episode_count = sum(1 for _ in podcast_dir.rglob("*.m*") if _.is_file())
                    
                    self.sync_progress = f"✅ {episode_count} eps"
                else:
                    self.sync_progress = "❌ Failed"
                
            except subprocess.TimeoutExpired:
                self.sync_progress = "⏰ Timeout"
            except Exception:
                self.sync_progress = f"❌ Error"
            finally:
                import time
                time.sleep(5)
                self.is_syncing = False
                self.sync_progress = ""
        
        thread = threading.Thread(target=fetch_thread)
        thread.start()
    
    @rumps.clicked("🔍 Check iPod")
    def check_ipod(self, _):
        """Check iPod connection status"""
        try:
            ipod = self.syncer.detect_ipod()
            if ipod:
                # Get iPod info safely
                try:
                    # Check if .rockbox folder exists
                    rockbox_path = ipod / ".rockbox"
                    if rockbox_path.exists():
                        # Try to get space info
                        try:
                            stat = os.statvfs(str(ipod))
                            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
                            total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
                            used_gb = total_gb - free_gb
                            
                            message = (
                                f"Location: {ipod}\n"
                                f"Rockbox: ✅ Detected\n"
                                f"Space: {used_gb:.1f}GB used / {total_gb:.1f}GB total\n"
                                f"Free: {free_gb:.1f}GB"
                            )
                        except (OSError, PermissionError):
                            message = (
                                f"Location: {ipod}\n"
                                f"Rockbox: ✅ Detected\n"
                                f"Status: Ready for sync"
                            )
                    else:
                        message = f"Location: {ipod}\nRockbox: ❌ Not detected"
                except Exception:
                    message = f"Connected at: {ipod}\nStatus: Unknown"
                
                rumps.alert(
                    title="iPod Connected ✅",
                    message=message
                )
            else:
                rumps.alert(
                    title="No iPod Detected",
                    message="Make sure your Rockbox iPod is connected and mounted.\n\nLooking for a volume with /.rockbox folder."
                )
        except Exception as e:
            rumps.alert(
                title="Error Checking iPod",
                message=f"An error occurred: {str(e)[:100]}"
            )
    
    @rumps.clicked("📂 Open Library")
    def open_library(self, _):
        """Open podcast library folder in Finder"""
        library = self.syncer.library_dir
        library.mkdir(parents=True, exist_ok=True)
        subprocess.run(["open", str(library)])
    
    @rumps.clicked("⚙️ Settings")
    def open_config(self, _):
        """Open config.yaml in default editor"""
        config_path = Path(__file__).with_name("config.yaml")
        subprocess.run(["open", str(config_path)])
    
    @rumps.clicked("📊 Status")
    def show_status(self, _):
        """Show sync status and statistics"""
        # Count podcasts and episodes
        podcast_dir = self.syncer.library_dir / "Podcasts"
        
        show_count = 0
        episode_count = 0
        total_size_mb = 0
        
        if podcast_dir.exists():
            shows = list(podcast_dir.iterdir())
            show_count = len([s for s in shows if s.is_dir()])
            
            for show in shows:
                if show.is_dir():
                    for episode in show.glob("*.*"):
                        if episode.is_file():
                            episode_count += 1
                            total_size_mb += episode.stat().st_size / (1024*1024)
        
        # Get configured feeds
        feed_count = len(self.syncer.config.get("podcasts", []))
        
        status = (
            f"Last Sync: {self.last_sync}\n"
            f"iPod: {'Connected ✅' if self.connected else 'Not Connected ❌'}\n\n"
            f"Library Stats:\n"
            f"• {feed_count} feeds configured\n"
            f"• {show_count} shows downloaded\n"
            f"• {episode_count} episodes\n"
            f"• {total_size_mb:.1f} MB total"
        )
        
        rumps.alert(title="RockPod Status", message=status)


def main():
    """Main entry point for menu bar app"""
    # Check if running from correct directory
    if not Path("rockpod_sync.py").exists():
        print("Error: rockpod_menu.py must be run from the same directory as rockpod_sync.py")
        sys.exit(1)
    
    # Check if config exists
    if not Path("config.yaml").exists():
        print("Error: config.yaml not found. Please create it first.")
        sys.exit(1)
    
    # Check for virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: Not running in a virtual environment.")
        print("Run './setup.sh' first to set up the environment.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Run the app
    app = RockPodMenuApp()
    app.run()


if __name__ == "__main__":
    main()