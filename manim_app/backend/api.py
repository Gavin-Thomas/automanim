from flask import Blueprint, request, jsonify, send_file
import os
import subprocess
import uuid
import time
import json
import re
from werkzeug.utils import secure_filename

# Create a Blueprint for the backend API
api = Blueprint('api', __name__)

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

# Import the enhanced text_to_manim_code function
from backend.text_to_manim import text_to_manim_code

@api.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok", "message": "Manim app backend is running"})

@api.route('/generate', methods=['POST'])
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
        # Log the incoming request
        print(f"Received animation request with description: '{description}'")
        print(f"Generated job ID: {job_id}")
        
        # Step 1: Convert description to Manim code
        manim_code = text_to_manim_code(description, job_id)
        print(f"Generated Manim code for job {job_id}")
        
        # Step 2: Save the code to a temporary Python file
        script_path = os.path.join(TEMP_FOLDER, f"{job_id}.py")
        with open(script_path, 'w') as f:
            f.write(manim_code)
        print(f"Saved Manim code to {script_path}")
        
        # Step 3: Run Manim to generate the animation
        print(f"Starting Manim execution for job {job_id}")
        output_path = run_manim(script_path, job_id)
        
        if not output_path or not os.path.exists(output_path):
            error_msg = f"Failed to generate animation for job {job_id}: Output file not found"
            print(error_msg)
            return jsonify({"error": error_msg}), 500
        
        # Step 4: Return the path to the generated video
        video_url = f"/api/video/{job_id}"
        print(f"Animation generated successfully for job {job_id}")
        print(f"Video URL: {video_url}")
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "video_url": video_url,
            "code": manim_code
        })
        
    except Exception as e:
        error_msg = f"Error generating animation for job {job_id}: {str(e)}"
        print(error_msg)
        return jsonify({"error": error_msg}), 500

@api.route('/video/<job_id>', methods=['GET'])
def get_video(job_id):
    """Serve the generated video file"""
    # Sanitize job_id to prevent directory traversal
    job_id = secure_filename(job_id)
    
    # Look for the video file
    video_path = os.path.join(MEDIA_FOLDER, 'videos', job_id, '480p15', 'ManimScene.mp4')
    
    if not os.path.exists(video_path):
        return jsonify({"error": "Video not found"}), 404
    
    return send_file(video_path, mimetype='video/mp4')

@api.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Check the status of a job"""
    # Sanitize job_id to prevent directory traversal
    job_id = secure_filename(job_id)
    
    # Check if the video file exists
    video_path = os.path.join(MEDIA_FOLDER, 'videos', job_id, '480p15', 'ManimScene.mp4')
    
    if os.path.exists(video_path):
        return jsonify({
            "status": "completed",
            "video_url": f"/api/video/{job_id}"
        })
    
    # Check if the script file exists
    script_path = os.path.join(TEMP_FOLDER, f"{job_id}.py")
    
    if os.path.exists(script_path):
        return jsonify({
            "status": "processing"
        })
    
    return jsonify({
        "status": "not_found"
    }), 404

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
        
        # Log the command being executed
        print(f"Executing command: {' '.join(cmd)}")
        
        # Execute the command with a longer timeout for complex animations
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            stdout, stderr = process.communicate(timeout=120)  # 120-second timeout for more complex animations
            
            if process.returncode != 0:
                error_msg = f"Manim execution failed with return code {process.returncode}: {stderr}"
                print(error_msg)
                raise Exception(error_msg)
            
            # Expected output path based on Manim's conventions
            output_path = os.path.join(MEDIA_FOLDER, 'videos', script_name, '480p15', 'ManimScene.mp4')
            
            # Check if the file exists
            if not os.path.exists(output_path):
                # Try to find the video file in case the path convention changed
                possible_paths = []
                for root, dirs, files in os.walk(os.path.join(MEDIA_FOLDER, 'videos', script_name)):
                    for file in files:
                        if file.endswith('.mp4'):
                            possible_paths.append(os.path.join(root, file))
                
                if possible_paths:
                    # Use the first found video file
                    output_path = possible_paths[0]
                    print(f"Found video at alternative path: {output_path}")
                else:
                    error_msg = f"Output video file not found at {output_path} or any subdirectory"
                    print(error_msg)
                    raise Exception(error_msg)
            
            print(f"Manim execution successful. Output at: {output_path}")
            return output_path
            
        except subprocess.TimeoutExpired:
            # Kill the process if it times out
            process.kill()
            error_msg = "Manim execution timed out after 120 seconds"
            print(error_msg)
            raise Exception(error_msg)
            
    except Exception as e:
        error_msg = f"Error running Manim: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)
