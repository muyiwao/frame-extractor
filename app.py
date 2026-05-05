import streamlit as st
from extract_multiple_frames import extract_frames

st.set_page_config(page_title="Frame Extractor", layout="centered")

st.title("🎬 Video Frame Extractor")
st.write("Upload a video and extract frames easily.")

video = st.file_uploader("Upload Video", type=["mp4"])

resolution = st.selectbox("Resolution", ["1080p", "2K", "4K"])
mode = st.radio("Mode", ["Batch", "Single"])

interval = None
timestamp = ""

if mode == "Batch":
    interval = st.number_input("Interval (seconds)", min_value=1.0, value=60.0)
else:
    timestamp = st.text_input("Timestamp (HH:MM:SS)")

start_t = st.text_input("Start Time (optional)")
end_t = st.text_input("End Time (optional)")

if st.button("Extract Frames"):
    if video:
        with st.spinner("Processing video..."):
            output_zip = extract_frames(
                video,
                resolution,
                mode,
                interval,
                timestamp,
                start_t,
                end_t
            )

        with open(output_zip, "rb") as f:
            st.success("Frames extracted successfully!")
            st.download_button(
                "Download Frames",
                f,
                file_name="frames.zip"
            )
    else:
        st.warning("Please upload a video file.")