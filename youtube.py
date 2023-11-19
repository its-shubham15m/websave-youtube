import streamlit as st
from pytube import YouTube
from PIL import Image
import requests
from io import BytesIO
import io

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
            video_streams = yt.streams.filter(progressive=True)
            video_streams = sorted(video_streams, key=lambda x: int(x.resolution.split('p')[0]), reverse=True)
            stream_options = [f"{stream.resolution} - {stream.mime_type}" for stream in video_streams]
            selected_stream_option = st.selectbox("Select a video stream to generate a direct download link:",
                                                  stream_options)
            if selected_stream_option:
                selected_stream_index = stream_options.index(selected_stream_option)
                selected_stream = video_streams[selected_stream_index]
                video_data = io.BytesIO()
                selected_stream.stream_to_buffer(video_data)
                video_data.seek(0)
                st.download_button(label="Click to Download", key=f"{yt.title}.{selected_stream.subtype}",
                                   data=video_data, file_name=f"{yt.title}.{selected_stream.subtype}")
        else:
            audio_streams = yt.streams.filter(only_audio=True)

            # Arrange audio streams in descending order by bitrate
            audio_streams = sorted(audio_streams, key=lambda x: int(x.abr.replace('kbps', '')), reverse=True)

            # Generate audio quality choices dynamically
            audio_quality_choices = [f"{audio_stream.abr.replace('kbps', '')}kbps" for audio_stream in audio_streams]
            audio_quality = st.selectbox("Select audio quality:", audio_quality_choices)
            selected_audio_stream = next(
                (audio_stream for audio_stream in audio_streams if audio_quality in audio_stream.abr), None)
            if selected_audio_stream:
                audio_data = io.BytesIO()
                selected_audio_stream.stream_to_buffer(audio_data)
                audio_data.seek(0)
                st.download_button(label="Click to Download", key=f"{yt.title}.mp3", data=audio_data,
                                   file_name=f"{yt.title}.mp3")
            else:
                st.warning("No audio stream available for the selected quality.")

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
st.markdown("Made with ❤️ by *Shubham Gupta*")