import streamlit as st
from pytube import YouTube
from PIL import Image
import requests
from io import BytesIO
import re

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

# Function to extract the video title from the URL
def extract_video_title(url):
    match = re.search(r"v=([^&]+)", url)
    if match:
        video_id = match.group(1)
        info_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(info_url)
        if response.status_code == 200:
            data = response.json()
            return data.get("title")
    return None

# Generate a default filename
def get_default_filename():
    return "video"

# Check if a URL is provided
if url:
    with st.spinner("Fetching video information..."):
        yt, thumbnail_url = get_video_info(url)

    if yt:
        st.subheader("Video Thumbnail:")
        thumbnail = resize_thumbnail(thumbnail_url)
        # Apply the rounded border to the thumbnail
        st.image(thumbnail, use_column_width=True, caption="Video Thumbnail", output_format='JPEG', channels="BGR")

        download_option = st.radio("Select download type:", ("Video", "Audio"))

        if download_option == "Video":
            video_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()

            # Generate a direct download link for the selected stream
            stream_options = [f"{stream.resolution} - {stream.mime_type} - {stream.itag}" for stream in video_streams]
            selected_stream_option = st.selectbox("Select a video stream to generate a direct download link:",
                                                  stream_options)
            if selected_stream_option:
                selected_stream_index = stream_options.index(selected_stream_option)
                selected_stream = video_streams[selected_stream_index]
                download_url = selected_stream.url

                # Set the download link with the video title as the filename
                video_title = extract_video_title(url)
                if video_title:
                    filename = f"{video_title}.mp4"
                else:
                    filename = f"{get_default_filename()}.mp4"

                st.subheader("Download Video:")
                st.markdown(f'<a href="{download_url}" download="{filename}">Click to Download</a>', unsafe_allow_html=True)

        if download_option == "Audio":
            audio_streams = yt.streams.filter(only_audio=True, file_extension='mp4')

            # Generate audio quality choices dynamically
            audio_quality_choices = [f"{audio_stream.abr.replace('kbps', '')}kbps" for audio_stream in audio_streams]
            audio_quality = st.selectbox("Select audio quality:", audio_quality_choices)
            selected_audio_stream = next(
                (audio_stream for audio_stream in audio_streams if audio_quality in audio_stream.abr), None)
            if selected_audio_stream:
                download_url = selected_audio_stream.url

                # Set the download link with the video title as the filename
                video_title = extract_video_title(url)
                if video_title:
                    filename = f"{video_title}.mp4"
                else:
                    filename = f"{get_default_filename()}.mp4"

                st.subheader("Download Audio:")
                st.markdown(f'<a href="{download_url}" download="{filename}">Click to Download</a>', unsafe_allow_html=True)

# Add a footer
st.markdown("Made with ❤️ by Shubham Gupta")
