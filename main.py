import os
import subprocess
import numpy as np
import cv2
from gtts import gTTS
from pathlib import Path

class Wav2LipAvatar:
    def __init__(self, wav2lip_dir="Wav2Lip"):
        """
        Initialize Wav2Lip system
        Args:
            wav2lip_dir: Path to Wav2Lip repository (clone from https://github.com/Rudrabha/Wav2Lip)
        """
        self.wav2lip_dir = Path(wav2lip_dir)
        self.avatar_img = self._load_avatar("assets/neutral_face.jpg")
        
        # Verify Wav2Lip installation
        assert (self.wav2lip_dir/"inference.py").exists(), "Wav2Lip not found at specified path"
        
    def _load_avatar(self, path):
        """Load avatar image with fallback placeholder"""
        try:
            img = cv2.imread(path)
            if img is None:
                raise FileNotFoundError
            return img
        except:
            # Create placeholder avatar
            img = np.zeros((256, 256, 3), dtype=np.uint8)  # Wav2Lip works best with 256x256
            img.fill(255)
            cv2.circle(img, (128, 128), 100, (0, 0, 255), -1)
            cv2.putText(img, "AVATAR", (60, 140), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            return img

    def generate_audio(self, text, output_path="output_audio.wav"):
        """Generate speech audio (WAV format works best with Wav2Lip)"""
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save as MP3 first (gTTS limitation)
        mp3_path = str(Path(output_path).with_suffix('.mp3'))
        tts.save(mp3_path)
        
        # Convert to WAV using ffmpeg
        cmd = f"ffmpeg -y -i {mp3_path} -acodec pcm_s16le -ar 16000 {output_path}"
        subprocess.run(cmd, shell=True, check=True)
        os.remove(mp3_path)
        
        return output_path

    def _run_wav2lip(self, face_path, audio_path, output_path):
        """Execute Wav2Lip inference"""
        cmd = [
            "python", str(self.wav2lip_dir/"inference.py"),
            "--checkpoint_path", str(self.wav2lip_dir/"checkpoints/wav2lip_gan.pth"),
            "--face", face_path,
            "--audio", audio_path,
            "--outfile", output_path,
            "--pads", "0", "10", "0", "0",  # Adjust padding if needed
            "--resize_factor", "1"  # Disable automatic resizing
        ]
        subprocess.run(cmd, check=True)

    def create_video(self, text, output_path="output.mp4"):
        """Generate lip-synced video with Wav2Lip"""
        # Prepare temporary files
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        face_path = str(temp_dir/"avatar.jpg")
        audio_path = str(temp_dir/"audio.wav")
        
        # Save avatar (resize for Wav2Lip if needed)
        cv2.imwrite(face_path, cv2.resize(self.avatar_img, (256, 256)))
        
        # Generate audio
        self.generate_audio(text, audio_path)
        
        # Run Wav2Lip
        self._run_wav2lip(face_path, audio_path, output_path)
        
        # Cleanup
        for f in temp_dir.glob("*"):
            f.unlink()
        temp_dir.rmdir()
        
        return output_path

if __name__ == "__main__":
    # Example usage
    avatar = Wav2LipAvatar(wav2lip_dir="Wav2Lip")  # Set your Wav2Lip path
    result = avatar.create_video("Hello world! This is now professionally lip-synced!")
    print(f"Final video saved to: {result}")