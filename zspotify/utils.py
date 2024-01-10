import os
import json
import datetime


class Archive:

    def __init__(self, file):
        self.file = file
        self.data = self.load()

    def load(self):
        if self.file.exists():
            with open(self.file, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Error loading archive: {e}")
                    return {}
        return {}

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=4)

    def add(self, track_id, artist=None, track_name=None, fullpath=None,
            audio_type=None, timestamp=None, save=True):
        if not timestamp:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data[track_id] = {
            "artist": artist,
            "track_name": track_name,
            "audio_type": audio_type,
            "fullpath": str(fullpath),
            "timestamp": timestamp
        }
        print(f"Added to archive: {artist} - {track_name}")
        if save:
            self.save()

    def get(self, track_id):
        return self.data.get(track_id)

    def remove(self, track_id):
        self.data.pop(track_id)
        self.save()

    def exists(self, track_id):
        return track_id in self.data

    def get_all(self):
        return self.data

    def get_ids_from_old_archive(self, old_archive_file):
        archive = []
        folder = old_archive_file.parent
        with open(old_archive_file, "r", encoding="utf-8") as f:
            for line in f.readlines():
                song = line.split("\t")
                try:
                    track_id, timestamp, artist, track_name, file_name = song
                    fullpath = folder / file_name
                    if fullpath.exists():
                        archive.append({
                            "track_id": track_id,
                            "track_artist": artist,
                            "track_name": track_name,
                            "timestamp": timestamp,
                            "fullpath": str(fullpath)
                        })
                except ValueError:
                    print(f"Error parsing line: {line}")

        return archive

    def archive_migration(self, paths_to_check):
        """Migrates the old archive to the new one"""
        for path in paths_to_check:
            old_archive_path = path / ".song_archive"
            if old_archive_path.exists():
                print("Found old archive, migrating to new one...")
                self._migrate_tracks_from_old_to_new_archive(old_archive_path)
                self._remove_old_archive(old_archive_path)

    def _migrate_tracks_from_old_to_new_archive(self, old_archive_path):
        tracks = self.get_ids_from_old_archive(old_archive_path)
        for track in tracks:
            if self.exists(track['track_id']):
                print(f"Skipping {track['track_name']} - Already in archive")
                continue
            self.add(track['track_id'],
                     artist=track['track_artist'],
                     track_name=track['track_name'],
                     fullpath=track['fullpath'],
                     timestamp=track['timestamp'],
                     audio_type="music",
                     save=False)
        self.save()
        print(f"Migration complete from: {old_archive_path}")

    def _remove_old_archive(self, old_archive_path):
        try:
            os.remove(old_archive_path)
        except OSError as e:
            print(f"Unable to remove old archive: {old_archive_path}. Reason: {e}")


class FormatUtils:
    """Utility class for string formatting and sanitization."""

    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    RESET = "\033[0m"

    def sanitize_data(value: str) -> str:
        """Returns the string with problematic characters removed."""
        SANITIZE_CHARS = ["\\", "/", ":", "*", "?", "'", "<", ">", '"', "|"]

        for char in SANITIZE_CHARS:
            value = value.replace(char, "" if char != "|" else "-")
        return value

