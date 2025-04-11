import os
import sys
sys.path.append('/home/ubuntu/manim_app')
from utils.gemini_converter import GeminiTextToManimConverter

# Add the Gemini API integration to the backend API
def update_backend_api():
    """
    Update the backend API to use the Gemini converter for text-to-code conversion.
    """
    # Get the API key from environment variable or use the provided one
    api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyBqneZRu4sddzPHhuSS5Sj2qJ2D77HAPh8')
    
    # Initialize the Gemini converter
    gemini_converter = GeminiTextToManimConverter(api_key)
    
    # Test the converter with a simple description
    test_description = "Create a blue circle that transforms into a red square"
    try:
        manim_code = gemini_converter.convert_to_manim_code(test_description)
        print("Successfully generated Manim code using Gemini API:")
        print(manim_code)
        return True
    except Exception as e:
        print(f"Error testing Gemini API: {str(e)}")
        return False

if __name__ == "__main__":
    success = update_backend_api()
    sys.exit(0 if success else 1)
