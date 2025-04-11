import requests
import json
import time
import os
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    
    if response.status_code == 200:
        print("✅ Health endpoint is working")
        print(f"Response: {response.json()}")
        return True
    else:
        print(f"❌ Health endpoint failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_generate_animation(description):
    """Test the animation generation endpoint"""
    print(f"\nTesting animation generation with description: '{description}'")
    
    payload = {"description": description}
    
    try:
        response = requests.post(
            f"{API_URL}/generate", 
            json=payload,
            timeout=60  # 60-second timeout for animation generation
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Animation generation successful")
            print(f"Job ID: {result.get('job_id')}")
            print(f"Video URL: {result.get('video_url')}")
            
            # Check if the video is accessible
            video_url = f"{BASE_URL}{result.get('video_url')}"
            print(f"Checking video accessibility at: {video_url}")
            
            video_response = requests.get(video_url)
            if video_response.status_code == 200:
                print("✅ Video is accessible")
            else:
                print(f"❌ Video is not accessible, status code: {video_response.status_code}")
            
            return result
        else:
            print(f"❌ Animation generation failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Animation generation is taking too long.")
        return None
    except Exception as e:
        print(f"❌ Error during animation generation: {str(e)}")
        return None

def run_tests():
    """Run all tests"""
    print("=== Starting Manim App API Tests ===\n")
    
    # Test health endpoint
    if not test_health_endpoint():
        print("\n❌ Health endpoint test failed. Aborting further tests.")
        return
    
    # Test simple animation generation
    simple_descriptions = [
        "Create a blue circle",
        "Draw a red square",
        "Write the text \"Hello, Manim!\"",
    ]
    
    for description in simple_descriptions:
        result = test_generate_animation(description)
        if not result:
            print(f"\n❌ Simple animation test failed for: '{description}'")
        time.sleep(1)  # Brief pause between tests
    
    # Test more complex animation generation
    complex_descriptions = [
        "Create a blue circle and transform it into a red square",
        "Write the text \"Animation\" and fade in a green triangle below it",
        "Draw a square, rotate it, and then fade it out"
    ]
    
    for description in complex_descriptions:
        result = test_generate_animation(description)
        if not result:
            print(f"\n❌ Complex animation test failed for: '{description}'")
        time.sleep(1)  # Brief pause between tests
    
    print("\n=== Manim App API Tests Completed ===")

if __name__ == "__main__":
    run_tests()
