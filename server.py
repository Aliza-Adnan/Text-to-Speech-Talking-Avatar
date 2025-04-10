from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # Add this import
import subprocess
import uuid
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create static directory if it doesn't exist
os.makedirs('static', exist_ok=True)

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/generate')
def generate():
    text = request.args.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    output_id = str(uuid.uuid4())
    output_filename = f'{output_id}.mp4'
    output_path = f'static/{output_filename}'
    
    try:
        subprocess.run([
            'python', 'main.py',
            '--text', text,
            '--output', output_path
        ], check=True)
        
        # Verify the file was created
        if not os.path.exists(output_path):
            return jsonify({'error': 'Video generation failed'}), 500
            
        return jsonify({
            'video_url': f'/static/{output_filename}'
        })
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Video generation failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)