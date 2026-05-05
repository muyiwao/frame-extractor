import subprocess
from pathlib import Path
import zipfile
import shutil
import uuid

def extract_frames(video_file, resolution, mode, interval, timestamp, start_t, end_t):
    session_id = str(uuid.uuid4())
    output_dir = Path(f"outputs/{session_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    res_map = {
        "1080p": "1920:1080",
        "2K": "2560:1440",
        "4K": "3840:2160"
    }

    target_res = res_map.get(resolution, resolution)
    t_w, t_h = target_res.split(":")

    vf_chain = f"scale={target_res}:force_original_aspect_ratio=increase:flags=lanczos,crop={t_w}:{t_h},setsar=1"

    input_path = Path(f"temp_{session_id}.mp4")
    with open(input_path, "wb") as f:
        f.write(video_file.getbuffer())

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

    zip_path = f"{session_id}_frames.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in output_dir.glob("*"):
            zipf.write(file, arcname=file.name)

    # Cleanup
    shutil.rmtree(output_dir)
    input_path.unlink(missing_ok=True)

    return zip_path
