import streamlit as st
from pytube import YouTube
from PIL import Image
import requests
from io import BytesIO
import io
from moviepy.editor import VideoFileClip
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TDRC, TCON, TALB
import os

st.set_page_config(
    page_title="WebSave - YouTube",
    page_icon=Image.open("downloading.png"),
    layout="wide"
)

# Set the Streamlit app title
st.title("WebSave - Download YouTube Videos & Audios")

st.markdown(
    f"""
    <style>
    .stApp {{
        background: url("https://unsplash.com/photos/7PGqXW9k0ws/download?ixid=M3wxMjA3fDB8MXxzZWFyY2h8NDN8fG11c2ljJTIwYmFuZHxlbnwwfHx8fDE2OTgwODc0MTJ8MA&force=true");
        background-size: cover;
        background-position: center;
    }}

    .thumbnail-container {{
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
    }}

    .thumbnail-image {{
        width: 100%;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Input field for the YouTube URL
url = st.text_input("Enter the YouTube URL:")

@st.cache_data
def get_video_info(url):
    try:
        yt = YouTube(url)
        thumbnail_url = yt.thumbnail_url
        return yt, thumbnail_url
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None, None

def resize_thumbnail(thumbnail_url):
    response = requests.get(thumbnail_url)
    img = Image.open(BytesIO(response.content))
    return img

# Function to create audio file with metadata
def create_audio_with_metadata(yt, thumbnail_img, audio_data):
    audio = ID3()

    # Set album cover (thumbnail)
    audio.add(APIC(3, 'image/jpeg', 3, 'Front cover', thumbnail_img.tobytes()))

    # Set audio metadata
    audio["title"] = yt.title
    audio["artist"] = yt.author
    audio["date"] = str(yt.publish_date.year)
    audio["genre"] = "YouTube"
    audio["album"] = yt.title

    # Save audio with metadata
    audio_filename = f"{yt.title}.mp3"
    audio_path = os.path.join(".", audio_filename)
    audio_data.seek(0)
    with open(audio_path, "wb") as f:
        f.write(audio_data.read())
    audio.save(audio_path)
    return audio_path

# Function to create video file with thumbnail as cover
def create_video_with_thumbnail(yt, video_data, thumbnail_img):
    video_filename = f"{yt.title}.mp4"
    video_path = os.path.join(".", video_filename)
    video_data.seek(0)
    with open(video_path, "wb") as f:
        f.write(video_data.read())

    # Embed thumbnail as cover
    yt_thumbnail = yt.thumbnail_url
    video = VideoFileClip(video_path)
    video = video.set_duration(yt.length)
    video = video.set_audio(VideoFileClip(video_path).audio)
    video = video.set_thumbnail(yt_thumbnail)
    video.write_videofile(video_path)
    return video_path

# Check if a URL is provided
if url:
    with st.spinner("Fetching video information..."):
        yt, thumbnail_url = get_video_info(url)

    if yt:
        st.subheader("Video Thumbnail:")
        thumbnail = resize_thumbnail(thumbnail_url)
        st.image(thumbnail, use_column_width=True, caption="Video Thumbnail", output_format='JPEG', channels="BGR")

        download_format = st.radio("Select Download Format:", ["MP4 (Video)", "MP3 (Audio)"])
        if "MP4" in download_format:
            video_streams = yt.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc()
            selected_video_stream = video_streams[0]
            video_data = io.BytesIO()
            selected_video_stream.stream_to_buffer(video_data)

            # Create video file with thumbnail as cover
            video_path = create_video_with_thumbnail(yt, video_data, thumbnail)
            st.video(video_path)
        else:
            if audio_streams:
                selected_audio_stream = audio_streams[0]  # Get the first stream with desired audio quality
                audio_data = io.BytesIO()
                selected_audio_stream.stream_to_buffer(audio_data)

                # Create audio file with metadata
                audio_path = create_audio_with_metadata(yt, thumbnail, audio_data)
                st.audio(audio_path, format='audio/mp3', start_time=0, key=f"{yt.title}.mp3")

            else:
                st.warning(f"No {desired_audio_quality} audio stream available.")

# Contact developer
email = "shubhamgupta15m@gmail.com"
subject = "WebSave Inquiry"
mailto_link = f"mailto:{email}?subject={subject}"

# Apply CSS to style the link as a button
st.write(
    f'<a href="{mailto_link}" class="contact-button">Contact Developer</a>',
    unsafe_allow_html=True
)

# Define the CSS style for the button
st.markdown(
    """
    <style>
    .contact-button {
        background-color: #262730;
        color: white !important;
        padding: 5px 10px;
        text-align: center;
        text-decoration: none !important;
        display: inline-block;
        font-size: 18px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add a footer
st.markdown("Made with ❤️ by **Shubham Gupta**")
