import importlib
import time
import frontend
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import tkinter as tk
import os

class FrontendHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("frontend.py"):
            print(" Reloading Frontend...")
            reload_frontend()

def reload_frontend():
    try:
        importlib.reload(frontend)
        threading.Thread(target=frontend.run).start()
    except Exception as e:
        print("Error reloading Frontend:", e)

if __name__ == "__main__":
    print(" Watching for frontend changes...")
    event_handler = FrontendHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()

    os.system("python frontend.py")  # Start first instance

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
