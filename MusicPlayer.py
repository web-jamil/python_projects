import pygame
import os
import time
from pygame import mixer

class MusicPlayer:
    def __init__(self, music_directory: str):
        """
        Initializes the MusicPlayer.

        Args:
            music_directory (str): The path to the folder containing music files.
        """
        print("Initializing Music Player...")
        try:
            pygame.init()
            mixer.init()
            self.music_directory = music_directory
            self.playlist = []
            self.current_track_index = 0  # Changed to _index for clarity
            self.volume = 0.5  # Default volume (0.0 to 1.0)
            mixer.music.set_volume(self.volume)
            self.paused = False
            self.load_playlist()
            print("Music Player initialized successfully.")
        except Exception as e:
            print(f"Error initializing mixer: {e}")
            print("Please ensure you have pygame installed (`pip install pygame`)")
            print("and that your audio drivers are correctly set up.")
            pygame.quit() # Ensure pygame resources are released on error
            exit() # Exit the program if initialization fails

    def load_playlist(self):
        """Loads music files from the specified directory."""
        if not os.path.exists(self.music_directory):
            os.makedirs(self.music_directory)
            print(f"Created '{self.music_directory}' folder. Please add some MP3/WAV/OGG files there.")
            self.playlist = []
            return

        # List all files and filter for supported audio formats
        self.playlist = [os.path.join(self.music_directory, f) 
                         for f in os.listdir(self.music_directory) 
                         if f.lower().endswith(('.mp3', '.wav', '.ogg'))]
        
        if not self.playlist:
            print(f"No music files found in '{self.music_directory}' folder.")
            self.current_track_index = 0 # Reset index if playlist is empty
        else:
            print(f"Loaded {len(self.playlist)} tracks from '{self.music_directory}'.")
            # Ensure current_track_index is valid if playlist changed
            if self.current_track_index >= len(self.playlist):
                self.current_track_index = 0 # Reset if out of bounds

    def play(self):
        """Play the current track."""
        if not self.playlist:
            print("No tracks in playlist! Add music files to the specified directory.")
            return
            
        try:
            # Stop any currently playing music before loading a new one
            mixer.music.stop() 
            mixer.music.load(self.playlist[self.current_track_index])
            mixer.music.set_volume(self.volume)
            mixer.music.play()
            self.paused = False
            print(f"Now playing: {os.path.basename(self.playlist[self.current_track_index])}")
        except pygame.error as e:
            print(f"Error playing track {os.path.basename(self.playlist[self.current_track_index])}: {e}")
            # Try to skip to the next track if the current one causes an error
            print("Attempting to skip to the next track due to error.")
            self.next_track()
        except IndexError:
            print("Playlist is empty or current track index is invalid.")
            self.playlist = [] # Clear playlist if indexing failed
            self.load_playlist() # Try reloading
    
    def pause(self):
        """Pause or unpause playback."""
        if mixer.music.get_busy() or mixer.music.get_paused():
            if self.paused:
                mixer.music.unpause()
                self.paused = False
                print("Resumed playback.")
            else:
                mixer.music.pause()
                self.paused = True
                print("Playback paused.")
        else:
            print("No track is currently playing or paused.")
    
    def stop(self):
        """Stop playback."""
        if mixer.music.get_busy() or mixer.music.get_paused():
            mixer.music.stop()
            self.paused = False
            print("Playback stopped.")
        else:
            print("No track is currently playing.")
    
    def next_track(self):
        """Skip to next track."""
        if not self.playlist:
            print("No tracks in playlist to skip.")
            return
            
        self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
        self.play() # Play the new current track
    
    def prev_track(self):
        """Go to previous track."""
        if not self.playlist:
            print("No tracks in playlist to skip.")
            return
            
        self.current_track_index = (self.current_track_index - 1 + len(self.playlist)) % len(self.playlist)
        self.play() # Play the new current track
    
    def volume_up(self):
        """Increase volume by 10%."""
        self.volume = round(min(1.0, self.volume + 0.1), 1) # Round for cleaner percentages
        mixer.music.set_volume(self.volume)
        print(f"Volume: {int(self.volume * 100)}%")
    
    def volume_down(self):
        """Decrease volume by 10%."""
        self.volume = round(max(0.0, self.volume - 0.1), 1) # Round for cleaner percentages
        mixer.music.set_volume(self.volume)
        print(f"Volume: {int(self.volume * 100)}%")

    def get_current_track_info(self):
        """Returns information about the currently selected track."""
        if self.playlist and 0 <= self.current_track_index < len(self.playlist):
            return os.path.basename(self.playlist[self.current_track_index])
        return "No track selected"

    def run(self):
        """Main player interface."""
        print("\n--- Simple Music Player ---")
        print("---------------------------")
        print("Controls:")
        print("[1] Play/Pause    [2] Stop")
        print("[3] Next Track    [4] Previous Track")
        print("[+] Volume Up     [-] Volume Down")
        print("[q] Quit")
        print("---------------------------")
        
        if not self.playlist:
            print("No music found. Please add MP3/WAV/OGG files to the specified music directory.")
            print("Then, restart the player.")
            input("Press Enter to quit...") # Wait for user to read message
            return # Exit if no music

        # Start playing the first track automatically if there are tracks
        print(f"Starting with: {self.get_current_track_info()}")
        self.play()
            
        while True:
            # Display current track and status in the prompt
            current_status = "Playing" if mixer.music.get_busy() else "Stopped"
            if self.paused:
                current_status = "Paused"
            
            prompt_text = f"[{current_status} | {self.get_current_track_info()}] > "
            command = input(prompt_text).strip().lower()
            
            if command == '1':
                self.pause()
            elif command == '2':
                self.stop()
            elif command == '3':
                self.next_track()
            elif command == '4':
                self.prev_track()
            elif command == '+':
                self.volume_up()
            elif command == '-':
                self.volume_down()
            elif command == 'q':
                self.stop()
                print("Goodbye!")
                break
            else:
                print("Invalid command. Please try again.")
            
            # Check if music has ended to automatically play next track
            if not mixer.music.get_busy() and not self.paused and self.playlist:
                # Give a tiny moment for the status to update
                time.sleep(0.1)
                # Ensure it's truly not busy and not paused, then play next if needed
                if not mixer.music.get_busy() and not self.paused:
                    print("\nTrack ended. Playing next track...")
                    self.next_track()

        pygame.quit() # Properly uninitialize pygame

if __name__ == "__main__":
    # --- IMPORTANT: Set your music directory here ---
    # This should be the path to the folder where your music files are stored.
    # You can use an absolute path or a relative path.
    # Replace this path with the actual path to your music folder.
    # For example: r"C:\Users\YourUser\Music" on Windows
    # Or: "/home/youruser/Music" on Linux
    # Or: "/Users/youruser/Music" on macOS
    
    # Create a 'music' folder in the same directory as this script if you want a local one
    # music_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music")
    
    # Or use a specific path
    music_folder_path = r"C:\Users\ASUS\Music" # This was the path from your original code

    player = MusicPlayer(music_folder_path)
    player.run()
