from flask import Flask, request, jsonify
import subprocess
import uuid

app = Flask(__name__)

@app.route('/generate')
def generate():
    text = request.args.get('text')
    output_id = str(uuid.uuid4())
    
    # Your processing code here (call your existing script)
    subprocess.run([
        'python', 'main.py',
        '--text', text,
        '--output', f'static/{output_id}.mp4'
    ])
    
    return jsonify({
        'video_url': f'/static/{output_id}.mp4'
    })

app.run(host='0.0.0.0', port=8080)