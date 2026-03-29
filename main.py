import threading
import time
import os
import sys
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

from PIL import Image, ImageDraw, ImageGrab
import pystray
from pystray import MenuItem as item

class ScreenshotWorker:
    def __init__(self, save_dir, interval=20):
        self.save_dir = save_dir
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True # ensure thread doesn't block exit
            self.thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            try:
                # Capture the screen
                img = ImageGrab.grab()
                
                # Format current timestamp for unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(self.save_dir, f"screenshot_{timestamp}.png")
                
                # Save the image
                img.save(filename, "PNG")
            except Exception as e:
                pass # Ignoring errors silently as it runs in background
            
            # Wait for the next interval
            # We check the running flag frequently to allow quick exit
            for _ in range(self.interval * 10):
                if not self.running:
                    break
                time.sleep(0.1)

def create_tray_icon_image():
    # Create a simple 64x64 icon programmatically
    # A black background with a red square (looks like a record button)
    image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (16, 16, 48, 48),
        fill=(255, 0, 0))
    return image

def exit_action(icon, item, worker):
    worker.stop()
    icon.stop()

def main():
    # 1. Ask user for directory
    root = tk.Tk()
    root.withdraw() # Hide the small tkinter default window
    
    save_dir = filedialog.askdirectory(title="Válaszd ki a képernyőmentések helyét")
    
    # If the user clicks cancel, exit the program
    if not save_dir:
        sys.exit(0)
        
    # 2. Start the background screen capture worker
    worker = ScreenshotWorker(save_dir, interval=20)
    worker.start()
    
    # 3. Create the System Tray icon
    # using lambda to pass the worker instance to the exit action
    menu = (
        item('Kilépés (Exit)', lambda icon, item: exit_action(icon, item, worker)),
    )
    
    icon_image = create_tray_icon_image()
    icon = pystray.Icon("kepernyomento", icon_image, "Képernyőmentő fut...", menu)
    
    # 4. Run the tray icon (blocking call until icon.stop() is called)
    icon.run()

if __name__ == "__main__":
    main()
