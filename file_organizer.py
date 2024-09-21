import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import difflib
import os
import glob
import shutil

# File Organizer Function
def organize_files(path, verbose=0):
    extensions = {
         "jpg": "images",
    "png": "images",
    "ico": "images",
    "gif": "images",
    "svg": "images",
    "sql": "sql",
    "exe": "programs",
    "msi": "programs",
    "pdf": "pdf",
    "xlsx": "excel",
    "csv": "excel",
    "rar": "archive",
    "zip": "archive",
    "gz": "archive",
    "tar": "archive",
    "docx": "word",
    "torrent": "torrent",
    "txt": "text",
    "ipynb": "python",
    "py": "python",
    "pptx": "powerpoint",
    "ppt": "powerpoint",
    "mp3": "audio",
    "wav": "audio",
    "mp4": "video",
    "m3u8": "video",
    "webm": "video",
    "ts": "video",
    "json": "json",
    "css": "web",
    "js": "web",
    "html": "web",
    "apk": "apk",
    "sqlite3": "sqlite3",
        # your dictionary here
    }
    for extension, folder_name in extensions.items():
        files = glob.glob(os.path.join(path, f"*.{extension}"))
        if not os.path.isdir(os.path.join(path, folder_name)) and files:
            os.mkdir(os.path.join(path, folder_name))
        for file in files:
            basename = os.path.basename(file)
            dst = os.path.join(path, folder_name, basename)
            shutil.move(file, dst)

# Code Monitor Class
class CodeMonitorHandler(FileSystemEventHandler):
    def __init__(self):
        self.files_cache = {}

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".py"):
            self.track_changes(event.src_path)

    def track_changes(self, file_path):
        with open(file_path, 'r') as f:
            current_content = f.readlines()

        previous_content = self.files_cache.get(file_path, [])
        diff = difflib.unified_diff(previous_content, current_content, lineterm='')

        for line in diff:
            if line.startswith('+ ') and not line.startswith('+++'):
                logging.info(f"Added in {file_path}: {line[2:].strip()}")
            elif line.startswith('- ') and not line.startswith('---'):
                logging.info(f"Deleted from {file_path}: {line[2:].strip()}")

        self.files_cache[file_path] = current_content

# Function to monitor code changes
def monitor_code(path):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        handlers=[
            logging.FileHandler("code_changes.log"),
            logging.StreamHandler()
        ]
    )
    event_handler = CodeMonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

# Main function to run tasks sequentially
def main():
    path = "."

    # Run file organizer
    organize_files(path, verbose=1)

    # Run code monitor
    monitor_code(path)

if __name__ == "__main__":
    main()
