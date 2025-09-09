# arm_controller.py  (run this inside the same process as your detection)
import serial, time, threading, glob, sys

# ----- Configuration -----
SERIAL_BAUD = 115200
SERIAL_PORTS = ['/dev/ttyACM0', '/dev/ttyUSB0']  # fallback list
PICK_THRESHOLD = 0.8
CONFIRM_FRAMES = 3    # require detection above threshold for N frames
HOME_POS = {'base':0, 's1':20, 's2':20, 'claw_open':60, 'claw_closed':10}
# angle limits
BASE_MIN, BASE_MAX = 0, 180
S1_MIN, S1_MAX = 20, 160
S2_MIN, S2_MAX = 20, 160
CLAW_OPEN = HOME_POS['claw_open']
CLAW_CLOSED = HOME_POS['claw_closed']

# ----- Serial connect -----
def find_serial_port():
    for p in SERIAL_PORTS:
        try:
            s = serial.Serial(p, SERIAL_BAUD, timeout=1)
            time.sleep(1)
            if s.is_open:
                print("Connected to", p)
                return s
        except Exception:
            continue
    # try glob
    for p in glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*'):
        try:
            s = serial.Serial(p, SERIAL_BAUD, timeout=1)
            time.sleep(1)
            if s.is_open:
                print("Connected to", p)
                return s
        except Exception:
            pass
    raise RuntimeError("Could not open serial port to Arduino. Plug it in and check /dev/ttyACM0 or /dev/ttyUSB0")

ser = find_serial_port()

def send_move(b, s1, s2, claw):
    cmd = f"M,{int(b)},{int(s1)},{int(s2)},{int(claw)}\n"
    ser.write(cmd.encode('utf-8'))
    # optionally read reply
    time.sleep(0.02)

# ----- Mapping functions (image coords -> servo angles) -----
def map_value(val, in_min, in_max, out_min, out_max):
    v = (val - in_min) / (in_max - in_min)
    return out_min + v * (out_max - out_min)

def compute_angles_from_bbox(cx, cy, bw, bh, frame_w, frame_h):
    """
    cx,cy = bbox center (pixels) in frame coords
    bw,bh = bbox width/height (pixels)
    returns base, s1, s2, claw angles (0..180)
    """
    # Base: map horizontal position to base angle (flip if needed)
    base = map_value(cx, 0, frame_w, BASE_MIN, BASE_MAX)

    # Shoulder1: map vertical position -> pitch: higher y (lower in frame) => smaller angle (arm down)
    # Adjust range based on your arm geometry
    s1 = map_value(cy, 0, frame_h, S1_MAX := S1_MAX if 'S1_MAX' in globals() else 160, S1_MIN := S1_MIN if 'S1_MIN' in globals() else 20)
    # But above due to variable assignment style, let's use explicit:
    s1 = map_value(cy, 0, frame_h, S1_MAX, S1_MIN)

    # Shoulder2 (elbow): use bbox height (bigger bbox -> close -> more folded elbow)
    # If bh large (close), make elbow angle smaller (folded)
    # Map bh from (0.05*frame_h .. 0.6*frame_h) to [S2_MAX .. S2_MIN]
    min_bh = 0.02 * frame_h
    max_bh = 0.6 * frame_h
    bh_clamped = max(min(bh, max_bh), min_bh)
    s2 = map_value(bh_clamped, min_bh, max_bh, S2_MAX, S2_MIN)

    # Claw: open before move, close to pick
    claw = CLAW_OPEN
    # Constrain
    base = max(min(base, BASE_MAX), BASE_MIN)
    s1 = max(min(s1, S1_MAX), S1_MIN)
    s2 = max(min(s2, S2_MAX), S2_MIN)
    return int(base), int(s1), int(s2), int(claw)

# ----- Pick sequence (runs in background thread) -----
is_busy = False

def pick_sequence(frame_w, frame_h, bbox):
    """
    bbox: (x_center, y_center, w, h) in pixels
    """
    global is_busy
    if is_busy:
        return
    is_busy = True
    try:
        cx, cy, bw, bh = bbox
        # compute target angles
        base_t, s1_t, s2_t, claw_t = compute_angles_from_bbox(cx, cy, bw, bh, frame_w, frame_h)
        print("Target angles:", base_t, s1_t, s2_t)

        # Step 0 - ensure claw open and move to above target (safe z)
        send_move(HOME_POS['base'], HOME_POS['s1'], HOME_POS['s2'], CLAW_OPEN)
        time.sleep(0.8)

        # Move base roughly first
        send_move(base_t, HOME_POS['s1'], HOME_POS['s2'], CLAW_OPEN)
        time.sleep(0.8)

        # Move shoulders towards target
        send_move(base_t, s1_t, s2_t, CLAW_OPEN)
        time.sleep(0.8)

        # close claw -> pick
        send_move(base_t, s1_t, s2_t, CLAW_CLOSED)
        time.sleep(0.6)

        # lift a bit after pick - adjust angles to lift (decrease s1 by 15 deg)
        send_move(base_t, max(S1_MIN, s1_t - 20), s2_t, CLAW_CLOSED)
        time.sleep(0.6)

        # rotate to drop zone (example: base to 150 deg)
        drop_base = 150
        send_move(drop_base, HOME_POS['s1'], HOME_POS['s2'], CLAW_CLOSED)
        time.sleep(0.8)

        # open claw to drop
        send_move(drop_base, HOME_POS['s1'], HOME_POS['s2'], CLAW_OPEN)
        time.sleep(0.4)

        # go back home
        send_move(HOME_POS['base'], HOME_POS['s1'], HOME_POS['s2'], CLAW_OPEN)
        time.sleep(0.8)

        print("Pick sequence finished")
    except Exception as e:
        print("Pick sequence error:", e)
    finally:
        is_busy = False

# Example call:
# threading.Thread(target=pick_sequence, args=(frame_w, frame_h, (cx,cy,bw,bh)), daemon=True).start()
