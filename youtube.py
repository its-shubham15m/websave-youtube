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

download_format = st.radio("Select Download Format:", ["MP4 (Video)", "MP3 (Audio)"])


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
        try:
            if "MP4" in download_format:
                video_streams = yt.streams.filter(progressive=True, file_extension="mp4").order_by(
                    'resolution').desc()
                stream_options = [f"{stream.resolution} - {stream.mime_type}" for stream in
                                  video_streams]
                selected_stream_option = st.selectbox("Select a video stream to generate a direct download link:",
                                                      stream_options)
                if selected_stream_option:
                    selected_stream_index = stream_options.index(selected_stream_option)
                    selected_stream = video_streams[selected_stream_index]
                    video_data = io.BytesIO()
                    selected_stream.stream_to_buffer(video_data)
                    video_data.seek(0)
                    st.download_button(label=f"Click to Download {yt.title}.mp4", key=f"{yt.title}.mp4",
                                       data=video_data, file_name=f"{yt.title}.mp4")
            else:
                audio_streams = yt.streams.filter(only_audio=True, file_extension='mp4')

                # Generate audio quality choices dynamically
                audio_quality_choices = [f"{audio_stream.abr.replace('kbps', '')}kbps" for audio_stream in
                                         audio_streams]
                audio_quality = st.selectbox("Select audio quality:", audio_quality_choices)
                selected_audio_stream = next(
                    (audio_stream for audio_stream in audio_streams if audio_quality in audio_stream.abr), None)
                if selected_audio_stream:
                    download_url = selected_audio_stream.url
                    st.subheader("Download Audio:")
                    st.markdown(f'<a href="{download_url}" download>Click to Download</a>', unsafe_allow_html=True)
                else:
                    st.warning("No audio stream available for the selected quality.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Contact developer
if st.button("Contact Developer"):
    email = "shubhamgupta15m@gmail.com"
    subject = "WebSave Inquiry"
    mailto_link = f"<a href='mailto:{email}?subject={subject}'>Contact Developer</a>"
    st.markdown(mailto_link, unsafe_allow_html=True)

# Add a footer
st.markdown("Made with ❤️ by Shubham Gupta")
