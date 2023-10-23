import streamlit as st
from pytube import YouTube
from PIL import Image
import requests
import io

st.set_page_config(
    page_title="YouTube Media Downloader",
    page_icon=":arrow_down:",
    layout="wide"
)

st.title("YouTube Media Downloader")

url = st.text_input("Enter the YouTube URL:")

@st.cache
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
    img = Image.open(io.BytesIO(response.content))
    return img

if url:
    with st.spinner("Fetching video information..."):
        yt, thumbnail_url = get_video_info(url)

    if yt:
        st.subheader("Video Thumbnail:")
        thumbnail = resize_thumbnail(thumbnail_url)
        st.image(thumbnail, use_column_width=True, caption="Video Thumbnail", output_format='JPEG', channels="BGR")

        download_format = st.radio("Select Download Format:", ["MP3 (Audio)", "MP4 (Video)"])

        if st.button("Download Media"):
            try:
                if "MP3" in download_format:
                    audio_stream = yt.streams.filter(only_audio=True).first()
                    audio_data = io.BytesIO()
                    audio_stream.stream_to_buffer(audio_data)
                    audio_data.seek(0)
                    st.info(f"Preparing download of {yt.title}.mp3...")
                    st.download_button(label=f"Click to Download {yt.title}.mp3", key=f"{yt.title}.mp3", data=audio_data, file_name=f"{yt.title}.mp3")
                else:
                    video_stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
                    video_data = io.BytesIO()
                    video_stream.stream_to_buffer(video_data)
                    video_data.seek(0)
                    st.info(f"Preparing download of {yt.title}.mp4...")
                    st.download_button(label=f"Click to Download {yt.title}.mp4", key=f"{yt.title}.mp4", data=video_data, file_name=f"{yt.title}.mp4")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Add a footer
st.markdown("Made with ❤️ by Shubham Gupta")
