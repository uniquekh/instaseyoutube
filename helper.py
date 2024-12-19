import os
import string
import time
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.config import IMAGEMAGICK_BINARY  # You can import if you need to check ImageMagick setup
import moviepy.video.fx.all as vfx
from instaloader import Instaloader, Post
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Initialize Instaloader
L = Instaloader()

# -------- Helper Functions --------

def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in filename if c in valid_chars).strip()

def linkdownload(link):
    id_pattern = r"(/p/|/reel/)([a-zA-Z0-9_-]+)/"
    match = re.search(id_pattern, link)

    if match:
        id = match.group(2)
        post = Post.from_shortcode(L.context, id)
        
        caption = post.caption or "No caption available"
        first_line = caption.split('\n')[0]
        limited_caption = ' '.join(first_line.split()[:8])
        sanitized_caption = sanitize_filename(limited_caption)

        download_folder = "downloads"
        os.makedirs(download_folder, exist_ok=True)

        L.download_post(post, target=download_folder)

        video_files = [file for file in os.listdir(download_folder) if file.endswith('.mp4')]

        if video_files:
            video_path = os.path.join(download_folder, video_files[0])
            new_video_name = f"{sanitized_caption}.mp4"
            new_video_path = os.path.join(download_folder, new_video_name)

            os.rename(video_path, new_video_path)
            return new_video_path, sanitized_caption
        else:
            return "", "Error: No video file found."
    else:
        return "", "Invalid link!"

def add_watermark(video_path, watermark_image=r"C:\\Users\\mujeem khan\\Desktop\\Youtube Uploader\\Untitled_design-removebg-preview.png", transparency=0.8, width=900, height=180, position=('center', 250)):
    output_path = f"watermarked_{os.path.basename(video_path)}"
    try:
        video = VideoFileClip(video_path).fx(vfx.lum_contrast, lum=0.1, contrast=0.2)
        watermark = ImageClip(watermark_image).resize(width=width, height=height).set_opacity(transparency)

        watermark = watermark.set_position((position[0], video.h - position[1] - height)).set_duration(video.duration)
        final_video = CompositeVideoClip([video, watermark]).set_audio(video.audio)
        final_video = final_video.fx(vfx.fadeout, 1)

        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        return output_path
    except Exception as e:
        return None

def merge_outro(video_path, outro_path, output_path, fade_duration=1):
    try:
        video = VideoFileClip(video_path)
        outro = VideoFileClip(outro_path).resize(width=video.w).fadein(fade_duration)
        final_video = concatenate_videoclips([video, outro])
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        return output_path
    except Exception as e:
        return None

def authenticate_youtube():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('be_positive_client.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(file_path, title, description, tags, category_id="22", privacy_status="public"):
    youtube = authenticate_youtube()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {"privacyStatus": privacy_status}
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    try:
        response = request.execute()
    except HttpError as error:
        print(f"An error occurred: {error}")

def cleanup_downloads():
    download_folder = "downloads"
    if os.path.exists(download_folder):
        for file in os.listdir(download_folder):
            file_path = os.path.join(download_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                pass
