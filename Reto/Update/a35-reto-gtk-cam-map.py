import os
import sys
import cv2
import gi
import threading

# Force GTK 3.0
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf

# Verify map libraries exist
try:
    from staticmap import StaticMap, CircleMarker
    HAS_STATICMAP = True
except ImportError:
    HAS_STATICMAP = False
    print("[!] Warning: 'staticmap' or 'Pillow' is not installed. Live map is disabled.")

RPMSG_DEVICE = "/dev/ttyRPMSG0"
VIDEO_DEVICE = "/dev/video0"

class SensorDashboard(Gtk.Window):
    def __init__(self):
        super().__init__(title="STM32MP25 Sensor Hub & Vision")
        self.set_default_size(1150, 600)  # Made wider to fit the map
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.setup_css()
        
        # Main split layout (Horizontal)
        main_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40)
        main_hbox.set_border_width(30)
        self.add(main_hbox)
        
        # ==========================================
        # LEFT COLUMN: SENSORS & MAP
        # ==========================================
        left_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_hbox.pack_start(left_vbox, False, False, 0)
        
        title = Gtk.Label(label="🛰️ Core-to-Core Sensors")
        title.get_style_context().add_class("title")
        left_vbox.pack_start(title, False, False, 0)
        
        # Sensor Grid
        grid = Gtk.Grid(column_spacing=30, row_spacing=15)
        grid.set_halign(Gtk.Align.CENTER)
        left_vbox.pack_start(grid, False, False, 0)
        
        self.lbl_gps = Gtk.Label(label="Searching for satellites...")
        self.lbl_tof = Gtk.Label(label="Initializing...")
        self.lbl_temp = Gtk.Label(label="-- °C")
        self.lbl_press = Gtk.Label(label="-- kPa")
        
        for lbl in [self.lbl_gps, self.lbl_tof, self.lbl_temp, self.lbl_press]:
            lbl.set_halign(Gtk.Align.START)
            lbl.get_style_context().add_class("value")
        
        grid.attach(self._create_header("🌍 GPS:"), 0, 0, 1, 1)
        grid.attach(self.lbl_gps, 1, 0, 1, 1)
        
        grid.attach(self._create_header("📏 TOF:"), 0, 1, 1, 1)
        grid.attach(self.lbl_tof, 1, 1, 1, 1)
        
        grid.attach(self._create_header("🌡️ Temp:"), 0, 2, 1, 1)
        grid.attach(self.lbl_temp, 1, 2, 1, 1)
        
        grid.attach(self._create_header("☁️ Press:"), 0, 3, 1, 1)
        grid.attach(self.lbl_press, 1, 3, 1, 1)

        left_vbox.pack_start(Gtk.Separator(), False, False, 10)

        # Map Area
        map_title = Gtk.Label(label="🗺️ Live Location")
        map_title.get_style_context().add_class("title")
        left_vbox.pack_start(map_title, False, False, 0)

        self.map_image = Gtk.Image()
        left_vbox.pack_start(self.map_image, True, True, 0)

        # Status Bar
        self.status_label = Gtk.Label(label="Connecting to Cortex-M33 OpenAMP...")
        self.status_label.get_style_context().add_class("status")
        left_vbox.pack_end(self.status_label, False, False, 0)

        # ==========================================
        # RIGHT COLUMN: CAMERA
        # ==========================================
        right_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        main_hbox.pack_start(right_vbox, True, True, 0)
        
        self.cam_title = Gtk.Label(label="📷 Live Camera Feed")
        self.cam_title.get_style_context().add_class("title")
        right_vbox.pack_start(self.cam_title, False, False, 0)
        
        self.cam_image = Gtk.Image()
        right_vbox.pack_start(self.cam_image, True, True, 0)

        # ==========================================
        # STATES & INIT
        # ==========================================
        self.buffer = ""
        self.fd = -1
        self.last_lat = None
        self.last_lon = None
        
        # Open Camera
        self.cap = cv2.VideoCapture(VIDEO_DEVICE)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        if not self.cap.isOpened():
            self.cam_title.set_text("❌ Camera Not Found")
            self.cam_title.get_style_context().add_class("status")
        else:
            GLib.timeout_add(33, self.update_camera_frame)
            
        GLib.idle_add(self.connect_rpmsg)

    def setup_css(self):
        css = b"""
        window { background-color: #121212; }
        .title { font-size: 24px; font-weight: 800; color: #00e5ff; }
        .header { font-size: 16px; font-weight: bold; color: #a0aab5; }
        .value { font-size: 18px; font-weight: bold; font-family: monospace; color: #00ff88; }
        .status { font-size: 12px; color: #ff5555; font-style: italic; }
        .status-ok { color: #55ff55; }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _create_header(self, text):
        lbl = Gtk.Label(label=text)
        lbl.set_halign(Gtk.Align.END)
        lbl.get_style_context().add_class("header")
        return lbl

    # --- MAP LOGIC (BACKGROUND THREAD) ---
    def _fetch_and_update_map(self, lat, lon):
        try:
            # Generate the map image
            m = StaticMap(400, 300)
            marker = CircleMarker((lon, lat), '#00e5ff', 12)
            m.add_marker(marker)
            image = m.render()
            
            # Ensure format is RGB for GTK
            if image.mode != "RGB":
                image = image.convert("RGB")
                
            data = image.tobytes()
            w, h = image.size
            
            # Safely pass the raw pixels back to the GTK main thread
            GLib.idle_add(self._set_map_image, data, w, h)
            
        except Exception as e:
            print("Map render error:", e)

    def _set_map_image(self, data, w, h):
        pixbuf = GdkPixbuf.Pixbuf.new_from_data(
            data, GdkPixbuf.Colorspace.RGB, False, 8, w, h, w * 3
        )
        self.map_image.set_from_pixbuf(pixbuf)

    def trigger_map_update(self, lat, lon):
        if not HAS_STATICMAP: return
        # Run network requests in the background so the UI doesn't freeze!
        thread = threading.Thread(target=self._fetch_and_update_map, args=(lat, lon))
        thread.daemon = True
        thread.start()

    # --- CAMERA LOGIC ---
    def update_camera_frame(self):
        if not self.cap.isOpened(): return False
            
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, d = frame_rgb.shape
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                frame_rgb.tobytes(), GdkPixbuf.Colorspace.RGB, False, 8, w, h, w * 3
            )
            self.cam_image.set_from_pixbuf(pixbuf)
        return True 

    # --- OPENAMP RPMsg LOGIC ---
    def connect_rpmsg(self):
        try:
            self.fd = os.open(RPMSG_DEVICE, os.O_RDWR | os.O_NONBLOCK)
            os.write(self.fd, b"wake up!\n")
            GLib.io_add_watch(self.fd, GLib.IO_IN, self.on_data_ready)
            self.status_label.set_text("✅ Connected via OpenAMP")
            self.status_label.get_style_context().add_class("status-ok")
        except Exception as e:
            self.status_label.set_text(f"❌ Connection Error: {e}")

    def on_data_ready(self, fd, condition):
        try:
            data = os.read(fd, 512)
            if data:
                self.buffer += data.decode('utf-8', errors='replace')
                self.process_buffer()
            return True
        except BlockingIOError: return True
        except OSError as e:
            self.status_label.set_text(f"❌ Connection Lost: {e}")
            self.status_label.get_style_context().remove_class("status-ok")
            return False

    def process_buffer(self):
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            line = line.strip()
            if not line: continue
            
            # --- PARSE GPS AND TRIGGER MAP ---
            if line.startswith("[NEO6MV2]:"):
                val = line.replace("[NEO6MV2]:", "").strip()
                self.lbl_gps.set_text(val)
                
                # Check if coordinates are valid (e.g., "X=48.11, Y=11.51")
                if "X=" in val and "Y=" in val:
                    try:
                        parts = val.split(',')
                        lat = float(parts[0].replace("X=", "").strip())
                        lon = float(parts[1].replace("Y=", "").strip())
                        
                        # Only re-download map if we moved by ~10 meters (0.0001 deg)
                        if self.last_lat is None or abs(lat - self.last_lat) > 0.0001 or abs(lon - self.last_lon) > 0.0001:
                            self.last_lat = lat
                            self.last_lon = lon
                            self.trigger_map_update(lat, lon)
                    except Exception:
                        pass
                        
            # --- PARSE OTHER SENSORS ---
            elif line.startswith("[VL53L0X]:"):
                val = line.replace("[VL53L0X]:", "").replace("D=", "").strip()
                self.lbl_tof.set_text(f"{val} mm")
                
            elif line.startswith("[BME280]:"):
                parts = line.replace("[BME280]:", "").split(",")
                if len(parts) == 2:
                    t = parts[0].strip().replace("T=", "")
                    p = parts[1].strip().replace("P=", "")
                    self.lbl_temp.set_text(f"{t} °C")
                    self.lbl_press.set_text(f"{p} kPa")

def main():
    app = SensorDashboard()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()

