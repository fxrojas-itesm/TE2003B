import os
import sys
import gi

# Force GTK 3.0 to ensure STM32 OpenSTLinux compatibility
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

RPMSG_DEVICE = "/dev/ttyRPMSG0"

class SensorDashboard(Gtk.Window):
    def __init__(self):
        super().__init__(title="STM32MP25 Sensor Dashboard")
        self.set_default_size(500, 350)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Apply the dark theme CSS
        self.setup_css()
        
        # Main layout container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_border_width(30)
        self.add(vbox)
        
        # Header Title
        title = Gtk.Label(label="🛰️ Core-to-Core Sensor Hub")
        title.get_style_context().add_class("title")
        vbox.pack_start(title, False, False, 0)
        
        vbox.pack_start(Gtk.Separator(), False, False, 0)
        
        # Grid layout for sensor values
        grid = Gtk.Grid(column_spacing=30, row_spacing=20)
        grid.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(grid, True, True, 0)
        
        # Value Labels
        self.lbl_gps = Gtk.Label(label="Searching for satellites...")
        self.lbl_tof = Gtk.Label(label="Initializing...")
        self.lbl_temp = Gtk.Label(label="-- °C")
        self.lbl_press = Gtk.Label(label="-- kPa")
        
        for lbl in [self.lbl_gps, self.lbl_tof, self.lbl_temp, self.lbl_press]:
            lbl.set_halign(Gtk.Align.START)
            lbl.get_style_context().add_class("value")
        
        # Attach to grid
        grid.attach(self._create_header("🌍 GPS Location:"), 0, 0, 1, 1)
        grid.attach(self.lbl_gps, 1, 0, 1, 1)
        
        grid.attach(self._create_header("📏 Laser Distance:"), 0, 1, 1, 1)
        grid.attach(self.lbl_tof, 1, 1, 1, 1)
        
        grid.attach(self._create_header("🌡️ Temperature:"), 0, 2, 1, 1)
        grid.attach(self.lbl_temp, 1, 2, 1, 1)
        
        grid.attach(self._create_header("☁️ Air Pressure:"), 0, 3, 1, 1)
        grid.attach(self.lbl_press, 1, 3, 1, 1)

        # Status Bar at the bottom
        self.status_label = Gtk.Label(label="Connecting to Cortex-M33 OpenAMP...")
        self.status_label.get_style_context().add_class("status")
        vbox.pack_end(self.status_label, False, False, 0)

        # Buffer for incoming RPMsg data
        self.buffer = ""
        self.fd = -1
        
        # Start connection process after UI renders
        GLib.idle_add(self.connect_rpmsg)

    def setup_css(self):
        css = b"""
        window {
            background-color: #121212;
        }
        .title {
            font-size: 26px;
            font-weight: 800;
            color: #00e5ff;
        }
        .header {
            font-size: 16px;
            font-weight: bold;
            color: #a0aab5;
        }
        .value {
            font-size: 18px;
            font-weight: bold;
            font-family: monospace;
            color: #00ff88;
        }
        .status {
            font-size: 12px;
            color: #ff5555;
            font-style: italic;
        }
        .status-ok {
            color: #55ff55;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), 
            provider, 
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _create_header(self, text):
        lbl = Gtk.Label(label=text)
        lbl.set_halign(Gtk.Align.END)
        lbl.get_style_context().add_class("header")
        return lbl

    def connect_rpmsg(self):
        try:
            self.fd = os.open(RPMSG_DEVICE, os.O_RDWR | os.O_NONBLOCK)
            
            # Send the dummy message so the M33 registers our endpoint address!
            os.write(self.fd, b"wake up!\n")
            
            # Watch the file descriptor asynchronously
            GLib.io_add_watch(self.fd, GLib.IO_IN, self.on_data_ready)
            
            self.status_label.set_text("✅ Connected via OpenAMP")
            self.status_label.get_style_context().add_class("status-ok")
            
        except FileNotFoundError:
            self.status_label.set_text(f"❌ Error: {RPMSG_DEVICE} not found. Is M33 running?")
        except PermissionError:
            self.status_label.set_text(f"❌ Permission Denied. Run with sudo.")
        except Exception as e:
            self.status_label.set_text(f"❌ Connection Error: {e}")

    def on_data_ready(self, fd, condition):
        try:
            data = os.read(fd, 512)
            if data:
                # Append raw incoming data to our buffer
                self.buffer += data.decode('utf-8', errors='replace')
                self.process_buffer()
                
            return True # Returning True keeps the IO watch alive!
            
        except BlockingIOError:
            return True
        except OSError as e:
            self.status_label.set_text(f"❌ Connection Lost: {e}")
            self.status_label.get_style_context().remove_class("status-ok")
            return False # Returning False removes the IO watch

    def process_buffer(self):
        # Process the buffer line by line
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            line = line.strip()
            
            if not line:
                continue
                
            # Parse the prefixes and update GTK labels
            if line.startswith("[NEO6MV2]:"):
                val = line.replace("[NEO6MV2]:", "").strip()
                self.lbl_gps.set_text(val)
                
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

