from flask import Flask, request, jsonify, send_file
import os
import subprocess
import uuid
import time
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads')
MEDIA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media')
TEMP_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils', 'temp')
MANIM_TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils', 'templates')

# Create necessary directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MEDIA_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(MANIM_TEMPLATE_FOLDER, exist_ok=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok", "message": "Manim app backend is running"})

@app.route('/api/generate', methods=['POST'])
def generate_animation():
    """
    Generate a Manim animation from text description
    
    Expected JSON payload:
    {
        "description": "Text description of the animation to generate"
    }
    """
    if not request.json or 'description' not in request.json:
        return jsonify({"error": "Missing description parameter"}), 400
    
    description = request.json['description']
    
    # Generate a unique ID for this job
    job_id = str(uuid.uuid4())
    
    try:
        # Step 1: Convert description to Manim code
        manim_code = text_to_manim_code(description, job_id)
        
        # Step 2: Save the code to a temporary Python file
        script_path = os.path.join(TEMP_FOLDER, f"{job_id}.py")
        with open(script_path, 'w') as f:
            f.write(manim_code)
        
        # Step 3: Run Manim to generate the animation
        output_path = run_manim(script_path, job_id)
        
        if not output_path or not os.path.exists(output_path):
            return jsonify({"error": "Failed to generate animation"}), 500
        
        # Step 4: Return the path to the generated video
        video_url = f"/static/media/{job_id}/ManimScene.mp4"
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "video_url": video_url,
            "code": manim_code
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/video/<job_id>', methods=['GET'])
def get_video(job_id):
    """Serve the generated video file"""
    # Sanitize job_id to prevent directory traversal
    job_id = secure_filename(job_id)
    
    # Look for the video file
    video_path = os.path.join(MEDIA_FOLDER, 'videos', job_id, '480p15', 'ManimScene.mp4')
    
    if not os.path.exists(video_path):
        return jsonify({"error": "Video not found"}), 404
    
    return send_file(video_path, mimetype='video/mp4')

def text_to_manim_code(description, job_id):
    """
    Convert text description to Manim code
    
    This is a simplified version that uses templates for common animations.
    In a production app, this would use a more sophisticated NLP approach or LLM.
    """
    # For the prototype, we'll use a simple template-based approach
    # In a real implementation, this would use OpenAI API or another LLM
    
    # Basic template for a Manim scene
    template = """from manim import *

class ManimScene(Scene):
    def construct(self):
        # Generated from description: {description}
        
{content}
"""
    
    # Very simple keyword matching for the prototype
    content = []
    
    # Check for common elements in the description
    if "circle" in description.lower():
        content.append("        # Create a circle")
        content.append("        circle = Circle(color=BLUE)")
        content.append("        self.play(Create(circle))")
        content.append("        self.wait(1)")
    
    if "square" in description.lower():
        content.append("        # Create a square")
        content.append("        square = Square(color=RED)")
        content.append("        self.play(Create(square))")
        content.append("        self.wait(1)")
    
    if "text" in description.lower() or "write" in description.lower():
        # Extract text content if it's in quotes
        import re
        text_match = re.search(r'"([^"]*)"', description)
        text_content = text_match.group(1) if text_match else "Hello, Manim!"
        
        content.append(f"        # Add text: {text_content}")
        content.append(f'        text = Text("{text_content}", color=YELLOW)')
        content.append("        self.play(Write(text))")
        content.append("        self.wait(1)")
    
    if "transform" in description.lower():
        if "circle" in description.lower() and "square" in description.lower():
            content.append("        # Transform circle to square")
            content.append("        circle = Circle(color=BLUE)")
            content.append("        square = Square(color=RED)")
            content.append("        self.play(Create(circle))")
            content.append("        self.wait(1)")
            content.append("        self.play(Transform(circle, square))")
            content.append("        self.wait(1)")
    
    # If no specific elements were found, create a default animation
    if not content:
        content.append("        # Default animation")
        content.append("        text = Text(\"Generated Animation\", color=BLUE)")
        content.append("        self.play(Write(text))")
        content.append("        self.wait(1)")
        content.append("        circle = Circle(color=RED)")
        content.append("        circle.next_to(text, DOWN)")
        content.append("        self.play(Create(circle))")
        content.append("        self.wait(1)")
    
    # Join the content lines and format the template
    formatted_content = "\n".join(content)
    manim_code = template.format(description=description, content=formatted_content)
    
    return manim_code

def run_manim(script_path, job_id):
    """Run Manim to generate the animation"""
    try:
        # Get the directory containing the script
        script_dir = os.path.dirname(script_path)
        
        # Get the filename without extension
        script_name = os.path.basename(script_path).split('.')[0]
        
        # Run Manim command
        cmd = [
            "python3", "-m", "manim", 
            script_path, 
            "ManimScene",  # The class name in our generated code
            "-ql",  # Low quality for faster rendering
            "--media_dir", MEDIA_FOLDER
        ]
        
        # Execute the command
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(timeout=60)  # 60-second timeout
        
        if process.returncode != 0:
            raise Exception(f"Manim execution failed: {stderr}")
        
        # Expected output path based on Manim's conventions
        output_path = os.path.join(MEDIA_FOLDER, 'videos', script_name, '480p15', 'ManimScene.mp4')
        
        # Check if the file exists
        if not os.path.exists(output_path):
            raise Exception(f"Output video file not found at {output_path}")
        
        return output_path
        
    except subprocess.TimeoutExpired:
        raise Exception("Manim execution timed out")
    except Exception as e:
        raise Exception(f"Error running Manim: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
