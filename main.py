import os
import subprocess
import argparse
from gtts import gTTS

# Paths
BASE_IMAGE = "assets/avatar_1.jpg"
TEMP_VIDEO = "temp_video_1.mp4"
TEMP_OUTPUT = "temp_result_1.mp4"  # Temporary Wav2Lip output
OUTPUT_AUDIO = "output_1.wav"
OUTPUT_VIDEO = "static/final_output_1.mp4"

# Ensure temp directory exists
os.makedirs("temp", exist_ok=True)

def text_to_speech(text, output_path=OUTPUT_AUDIO):
    tts = gTTS(text, lang="en")
    tts.save("output.mp3")
    subprocess.run(["ffmpeg", "-i", "output.mp3", output_path, "-y"], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def image_to_video(image_path, output_video, audio_path, fps=25):
    audio_length = os.path.getsize(audio_path) / (16000 * 2)  # Approx duration
    cmd = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_path,
        "-c:v", "libx264",
        "-t", str(audio_length + 1.0),
        "-vf", f"fps={fps},scale=256:256,format=yuv420p",
        "-y", output_video
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def generate_lipsync(input_video, input_audio, output_video):
    cmd = [
        "python", "Wav2Lip/inference.py",
        "--checkpoint_path", "Wav2Lip/checkpoints/wav2lip_gan.pth",
        "--face", input_video,
        "--audio", input_audio,
        "--outfile", output_video,  # Direct final output
        "--wav2lip_batch_size", "4",
        "--resize_factor", "1",
        "--nosmooth"
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate a talking avatar video.")
    parser.add_argument('--text', required=True, help="Text to convert to speech and animate.")
    parser.add_argument('--output', required=True, help="Output path for the final video.")
    args = parser.parse_args()

    user_text = args.text  # Use the text passed from the command line

    print("Generating speech...")
    audio_path = text_to_speech(user_text)
    
    print("Creating video from image...")
    image_to_video(BASE_IMAGE, TEMP_VIDEO, audio_path)
    
    print("Animating avatar...")
    generate_lipsync(TEMP_VIDEO, audio_path, args.output)
    
    print(f"Done! Output: {args.output}")
