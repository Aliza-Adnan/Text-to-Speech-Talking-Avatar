import os
import subprocess
from gtts import gTTS

# Paths
BASE_IMAGE = "assets/avatar.jpg"  # Your static avatar image
TEMP_VIDEO = "temp_video.mp4"
OUTPUT_AUDIO = "output.wav"
OUTPUT_VIDEO = "final_output_fom.mp4"

def text_to_speech(text, output_path=OUTPUT_AUDIO):
    """Converts text to speech using gTTS and saves as a WAV file."""
    tts = gTTS(text, lang="en")
    tts.save("output.mp3")

    # Convert MP3 to WAV
    subprocess.run([
        "ffmpeg", "-i", "output.mp3", "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", output_path, "-y"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def image_to_video(image_path, output_video, duration=5, fps=25):
    """Converts a static image into a video file."""
    cmd = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_path,
        "-c:v", "libx264",
        "-t", str(duration),
        "-vf", f"fps={fps},format=yuv420p",
        "-y", output_video
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def generate_lipsync(input_video, input_audio, output_video):
    """Uses Pocketsphinx + FOMM to animate avatar's face with lip sync."""
    cmd = [
        "python", "first-order-model/demo.py",
        "--source_image", BASE_IMAGE,
        "--driven_audio", input_audio,
        "--output", output_video,
        "--cpu"
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    user_text = input("Enter text: ")
    
    print("Generating speech...")
    audio_path = text_to_speech(user_text)

    print("Creating video from image...")
    image_to_video(BASE_IMAGE, TEMP_VIDEO)

    print("Animating avatar...")
    generate_lipsync(TEMP_VIDEO, audio_path, OUTPUT_VIDEO)

    print(f"Animation complete. Check the output at {OUTPUT_VIDEO}")
