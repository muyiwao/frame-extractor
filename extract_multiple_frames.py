import subprocess
from pathlib import Path
import zipfile
import shutil
import uuid
import json

def get_video_resolution(input_path):
    """Extract video width & height using ffprobe"""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        str(input_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)

    width = data["streams"][0]["width"]
    height = data["streams"][0]["height"]

    return width, height


def build_vf_chain(target_height):
    """
    Scale video while preserving aspect ratio
    Width auto-adjusts
    """
    return f"scale=-2:{target_height}:flags=lanczos,setsar=1"


def extract_frames(video_file, resolution, mode, interval, timestamp, start_t, end_t):
    session_id = str(uuid.uuid4())
    output_dir = Path(f"outputs/{session_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Resolution now represents TARGET HEIGHT ONLY
    res_map = {
        "1080p": 1080,
        "2K": 1440,
        "4K": 2160
    }

    target_height = res_map.get(resolution, 1440)

    input_path = Path(f"temp_{session_id}.mp4")
    with open(input_path, "wb") as f:
        f.write(video_file.getbuffer())

    # Detect original resolution (for logging/debugging)
    orig_w, orig_h = get_video_resolution(input_path)

    # Build aspect-ratio-safe filter
    vf_chain = build_vf_chain(target_height)

    time_args = []
    if start_t:
        time_args += ["-ss", start_t]
    if end_t:
        time_args += ["-to", end_t]

    if mode == "Batch":
        output_pattern = output_dir / "frame_%03d.png"

        command = ["ffmpeg", "-y"] + time_args + [
            "-i", str(input_path),
            "-vf", f"fps=1/{interval},{vf_chain}",
            "-q:v", "2",
            str(output_pattern)
        ]
    else:
        output_file = output_dir / "frame.png"

        command = [
            "ffmpeg", "-y",
            "-ss", timestamp,
            "-i", str(input_path),
            "-vf", vf_chain,
            "-frames:v", "1",
            "-q:v", "2",
            str(output_file)
        ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        return f"Error: {result.stderr}"

    # Zip output
    zip_path = f"{session_id}_frames.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in output_dir.glob("*"):
            zipf.write(file, arcname=file.name)

    # Cleanup
    shutil.rmtree(output_dir)
    input_path.unlink(missing_ok=True)

    return zip_path