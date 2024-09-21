import os
import time
import logging
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import difflib

def notify_user(message):
    try:
        subprocess.run(["notify-send", "Code Monitor Alert", message], stderr=subprocess.DEVNULL)
    except Exception as e:
        logging.error(f"Failed to send notification: {e}")

# Set up logging
log_file = "code_changes.log"
log_file_path = os.path.abspath(log_file)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

class CodeMonitorHandler(FileSystemEventHandler):
    def __init__(self):
        self.files_cache = {}
        self.ignored_files = {log_file_path, 'code_changes.log', '.git', '__pycache__', '*.pyc'}

    def should_ignore(self, path):
        return any(ignored in path for ignored in self.ignored_files) or path.endswith('.pyc')

    def on_any_event(self, event):
        if self.should_ignore(event.src_path):
            return

        if event.event_type == 'created':
            self.on_created(event)
        elif event.event_type == 'deleted':
            self.on_deleted(event)
        elif event.event_type == 'modified':
            self.on_modified(event)

    def on_created(self, event):
        if not event.is_directory:
            message = f"File created: {event.src_path}"
            logging.info(message)
            notify_user(message)

    def on_deleted(self, event):
        if not event.is_directory:
            message = f"File deleted: {event.src_path}"
            logging.info(message)
            notify_user(message)

    def on_modified(self, event):
        if not event.is_directory:
            self.track_changes(event.src_path)

    def track_changes(self, file_path):
        if not os.path.exists(file_path):
            return

        try:
            with open(file_path, 'r') as f:
                current_content = f.readlines()
        except Exception as e:
            logging.error(f"Error reading {file_path}: {e}")
            return

        previous_content = self.files_cache.get(file_path, [])
        diff = difflib.unified_diff(previous_content, current_content, lineterm='')

        changes_detected = False
        for line in diff:
            changes_detected = True
            if line.startswith('+ ') and not line.startswith('+++'):
                message = f"Added in {file_path}: {line[2:].strip()}"
                logging.info(message)
                notify_user(message)
            elif line.startswith('- ') and not line.startswith('---'):
                message = f"Deleted from {file_path}: {line[2:].strip()}"
                logging.info(message)
                notify_user(message)

        if changes_detected:
            self.files_cache[file_path] = current_content

def main():
    path = "."  # Current directory
    event_handler = CodeMonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    logging.info(f"Started monitoring code changes in: {path}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Stopped monitoring code changes.")

    observer.join()
if __name__ == "__main__":
    main()