import numpy as np
import cv2
from gtts import gTTS
from pydub import AudioSegment
import os
import ffmpeg

class LightweightAvatarTTS:
    def __init__(self):
        # Load base avatar image
        self.avatar_img = cv2.imread("assets/neutral_face.jpg")
        if self.avatar_img is None:
            # Create a placeholder if image not found
            self.avatar_img = np.zeros((300, 300, 3), dtype=np.uint8)
            self.avatar_img.fill(255)  # White background
            cv2.circle(self.avatar_img, (150, 150), 100, (0, 0, 255), -1)  # Red face
            cv2.putText(self.avatar_img, "AVATAR", (80, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
    def generate_audio(self, text, output_path="output_audio.mp3"):
        """Generate speech audio from text using gTTS"""
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        return output_path
    
    def generate_viseme_frames(self, audio_path):
        """Generate simple facial animation frames"""
        audio = AudioSegment.from_mp3(audio_path)
        duration_sec = len(audio) / 1000.0
        fps = 25
        frame_count = int(duration_sec * fps)
        
        frames = []
        for i in range(frame_count):
            # Simple mouth movement based on frame position
            progress = i/frame_count
            mouth_open = int(20 * abs(np.sin(progress * 10 * np.pi)))
            
            frame = self.avatar_img.copy()
            cv2.ellipse(frame, (150, 200), (40, mouth_open), 0, 180, 360, (0, 0, 0), -1)
            frames.append(frame)
        
        return frames
    
    def create_video(self, text, output_path="output.mp4"):
        """Full pipeline with ffmpeg for audio-video merging"""
        # Generate audio
        audio_path = self.generate_audio(text)
        
        # Generate silent video
        frames = self.generate_viseme_frames(audio_path)
        height, width = frames[0].shape[:2]
        
        # First save video without audio
        silent_video_path = "temp_silent.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(silent_video_path, fourcc, 25, (width, height))
        
        for frame in frames:
            video_writer.write(frame)
        video_writer.release()
        
        # Now combine audio and video using ffmpeg
        try:
            video_stream = ffmpeg.input(silent_video_path)
            audio_stream = ffmpeg.input(audio_path)
            
            ffmpeg.output(
                video_stream, 
                audio_stream, 
                output_path, 
                vcodec='libx264', 
                acodec='aac', 
                strict='experimental'
            ).overwrite_output().run()
            
        except ffmpeg.Error as e:
            print("FFmpeg error:", e.stderr.decode())
            raise
        
        # Clean up temporary files
        os.remove(silent_video_path)
        
        return output_path

if __name__ == "__main__":
    avatar = LightweightAvatarTTS()
    result = avatar.create_video("Hello world, this is a test of TTS with facial animation.")
    print(f"Video created at: {result}")