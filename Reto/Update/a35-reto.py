import os
import sys
import time

RPMSG_DEVICE = "/dev/ttyRPMSG0"

def main():
    print(f"[*] Opening RPMsg device: {RPMSG_DEVICE}")
    
    try:
        # Open the device in Read/Write mode. 
        fd = os.open(RPMSG_DEVICE, os.O_RDWR | os.O_NONBLOCK)
    except FileNotFoundError:
        print(f"[!] Error: {RPMSG_DEVICE} not found.")
        print("    Did you start the M33 firmware and ensure it uses 'rpmsg-tty'?")
        sys.exit(1)
    except PermissionError:
        print(f"[!] Error: Permission denied to access {RPMSG_DEVICE}.")
        print("    Try running this script with 'sudo'.")
        sys.exit(1)

    print("[*] Waking up the Cortex-M33...")
    
    # This dummy message is CRITICAL: it tells the M33 our return address
    # so it knows where to send the OpenAMP packets!
    os.write(fd, b"wake up!\n")

    print("[*] Ready! Streaming live sensor data...")
    print("-" * 50)

    # Main loop: Capture M33 data and print it cleanly
    try:
        while True:
            try:
                # Read up to 512 bytes from the device (matching our C buffer size)
                data = os.read(fd, 512)
                if data:
                    # Print the received data without adding extra Python newlines
                    print(data.decode('utf-8', errors='replace'), end="", flush=True)
                else:
                    time.sleep(0.01)
            except BlockingIOError:
                # Normal for non-blocking reads when no data is available
                time.sleep(0.05)
            except OSError as e:
                print(f"\n[!] Error reading from {RPMSG_DEVICE}: {e}")
                break
                
    except KeyboardInterrupt:
        print("\n[*] Exiting due to Ctrl+C...")
    finally:
        os.close(fd)

if __name__ == "__main__":
    main()

