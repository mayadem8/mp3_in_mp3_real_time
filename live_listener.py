import sounddevice as sd
import soundfile as sf
import subprocess
import numpy as np
import threading
import time
from collections import deque
from datetime import timedelta


SR = 44100
WINDOW_SEC = 5      
HOP_SEC = 1         
AUDFPRINT_DIR = "audfprint"
DB_PATH = "../fpdb.pklz"


target_start = None
target_end = None
last_match_time = None
grace_nomatch = 2
nomatch_count = 0

# --- Buffer ---
buffer = deque(maxlen=SR * WINDOW_SEC)
stream_time = 0.0


def format_timestr(seconds: float):
    return str(timedelta(seconds=int(seconds)))


def audio_callback(indata, frames, time_info, status):
    """Record the audio stream into the buffer."""
    if status:
        print("!", status)
    buffer.extend(indata[:, 0])  # mono only


def process_loop():
    """Background audio processing every HOP_SEC seconds."""
    global target_start, target_end, last_match_time, nomatch_count, stream_time

    while True:
        if len(buffer) >= SR * WINDOW_SEC:
            # Take the last WINDOW_SEC seconds of audio from the buffer
            chunk = np.array(buffer)[-SR * WINDOW_SEC:]
            chunk_file = f"{AUDFPRINT_DIR}/temp_chunk.wav"
            sf.write(chunk_file, chunk, SR)

            # For logging: window time (to keep track of time ranges)
            win_start = max(0.0, stream_time - WINDOW_SEC)
            win_end = stream_time

            # Run audfprint to match the audio chunk
            result = subprocess.run(
                ["python", "audfprint.py", "match", f"--dbase={DB_PATH}", "temp_chunk.wav"],
                cwd=AUDFPRINT_DIR,
                capture_output=True, text=True
            )

            matched = False
            for line in result.stdout.splitlines():
                if "Matched" in line:
                    matched = True
                    offset = 0.0
                    if " at " in line:
                        try:
                            offset = float(line.split(" at ")[1].split()[0])
                        except:
                            pass

                    # Aligned match time (relative to the stream)
                    aligned_time = stream_time + offset

                    if target_start is None:
                        target_start = aligned_time
                        print(f"(win {format_timestr(win_start)}–{format_timestr(win_end)}) "
                              f"START aligned={format_timestr(aligned_time)}")

                    target_end = aligned_time
                    last_match_time = aligned_time
                    nomatch_count = 0
                    print(f"(win {format_timestr(win_start)}–{format_timestr(win_end)}) "
                          f"MATCH aligned={format_timestr(aligned_time)} (offset {offset:+.1f}s)")

            if not matched:
                print(f"(win {format_timestr(win_start)}–{format_timestr(win_end)}) NOMATCH")
                if target_start is not None:
                    nomatch_count += 1
                    if nomatch_count >= grace_nomatch:
                        # Extend the segment end by grace period after last match
                        if last_match_time is not None:
                            target_end = last_match_time + (grace_nomatch * HOP_SEC)

                        duration = target_end - target_start
                        print(f" END at {format_timestr(target_end)}   "
                              f"segment: {format_timestr(target_start)}–{format_timestr(target_end)}")
                        print(f" DURATION: {format_timestr(duration)} ({duration:.2f}s)")

                        # Reset segment tracking
                        target_start, target_end, last_match_time, nomatch_count = None, None, None, 0

        time.sleep(HOP_SEC)
        stream_time += HOP_SEC


def main():
    print(" Starting real-ime listener (Ctrl+C to stop)...")

    threading.Thread(target=process_loop, daemon=True).start()

    with sd.InputStream(channels=1, samplerate=SR, callback=audio_callback):
        while True:
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(" Stopped by user")
