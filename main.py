import threading
import time
import os
import sys
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
                timestamp = datetime.now().strftime("%H%M%S")
                filename = os.path.join(self.save_dir, f"screenshot_{timestamp}.png")
                
                # Save the image
                img.save(filename, "PNG")
            except Exception as e:
                # Silently catch errors in background thread
                pass
            
            # Wait for the next interval
            for _ in range(self.interval * 10):
                if not self.running:
                    break
                time.sleep(0.1)

def create_tray_icon_image():
    # Create a simple 64x64 icon (black background with a red record circle)
    image = Image.new('RGB', (64, 64), color=(30, 30, 30))
    dc = ImageDraw.Draw(image)
    dc.ellipse((12, 12, 52, 52), fill=(255, 50, 50))
    return image

def exit_action(icon, item, worker):
    worker.stop()
    icon.stop()

def get_desktop_path():
    # Detect the desktop path across Windows environments
    return os.path.abspath(os.path.join(os.path.expanduser("~"), "Desktop"))

def main():
    # 1. Prepare target directory on Desktop with today's date
    desktop = get_desktop_path()
    today = datetime.now().strftime("%Y-%m-%d")
    save_dir = os.path.join(desktop, today)
    
    # Create the folder if it doesn't exist
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    except Exception as e:
        print(f"Error creating directory: {e}")
        sys.exit(1)
        
    # 2. Start the background screen capture worker
    worker = ScreenshotWorker(save_dir, interval=20)
    worker.start()
    
    # 3. Create the System Tray icon
    menu = (
        item('Mappa megnyitása', lambda: os.startfile(save_dir)),
        item('Kilépés', lambda icon, item: exit_action(icon, item, worker)),
    )
    
    icon_image = create_tray_icon_image()
    icon = pystray.Icon("kepernyomento", icon_image, f"Mentés ide: {today}", menu)
    
    # 4. Run the tray icon
    icon.run()

if __name__ == "__main__":
    main()

