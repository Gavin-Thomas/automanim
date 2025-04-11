import os
import sys
import re

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Gemini converter
from utils.gemini_converter import GeminiTextToManimConverter

# Get the API key from environment variable or use the provided one
api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyBqneZRu4sddzPHhuSS5Sj2qJ2D77HAPh8')

# Initialize the Gemini converter
gemini_converter = GeminiTextToManimConverter(api_key)

def text_to_manim_code(description, job_id):
    """
    Convert text description to Manim code using Gemini API
    
    Args:
        description (str): Text description of the animation
        job_id (str): Unique identifier for the job
        
    Returns:
        str: Generated Manim code
    """
    try:
        # Use Gemini API to convert text to Manim code
        print(f"Using Gemini API to generate Manim code for: '{description}'")
        manim_code = gemini_converter.convert_to_manim_code(description, job_id)
        print(f"Successfully generated Manim code using Gemini API")
        return manim_code
    except Exception as e:
        print(f"Error using Gemini API: {str(e)}")
        print(f"Falling back to template-based approach")
        # Fall back to template-based approach if Gemini fails
        return template_based_text_to_manim_code(description, job_id)

def template_based_text_to_manim_code(description, job_id):
    """
    Convert text description to Manim code using templates
    
    This is a simplified version that uses templates for common animations.
    Used as a fallback if the Gemini API fails.
    """
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
    
    if "triangle" in description.lower():
        content.append("        # Create a triangle")
        content.append("        triangle = Triangle(color=GREEN)")
        content.append("        self.play(Create(triangle))")
        content.append("        self.wait(1)")
    
    if "text" in description.lower() or "write" in description.lower():
        # Extract text content if it's in quotes
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
        elif "square" in description.lower() and "triangle" in description.lower():
            content.append("        # Transform square to triangle")
            content.append("        square = Square(color=RED)")
            content.append("        triangle = Triangle(color=GREEN)")
            content.append("        self.play(Create(square))")
            content.append("        self.wait(1)")
            content.append("        self.play(Transform(square, triangle))")
            content.append("        self.wait(1)")
    
    if "rotate" in description.lower():
        if "circle" in description.lower():
            content.append("        # Rotate a circle")
            content.append("        circle = Circle(color=BLUE)")
            content.append("        self.play(Create(circle))")
            content.append("        self.play(Rotate(circle, angle=PI), run_time=2)")
            content.append("        self.wait(1)")
        elif "square" in description.lower():
            content.append("        # Rotate a square")
            content.append("        square = Square(color=RED)")
            content.append("        self.play(Create(square))")
            content.append("        self.play(Rotate(square, angle=PI), run_time=2)")
            content.append("        self.wait(1)")
    
    if "fade" in description.lower():
        if "in" in description.lower():
            if "circle" in description.lower():
                content.append("        # Fade in a circle")
                content.append("        circle = Circle(color=BLUE)")
                content.append("        self.play(FadeIn(circle))")
                content.append("        self.wait(1)")
            elif "square" in description.lower():
                content.append("        # Fade in a square")
                content.append("        square = Square(color=RED)")
                content.append("        self.play(FadeIn(square))")
                content.append("        self.wait(1)")
        elif "out" in description.lower():
            if "circle" in description.lower():
                content.append("        # Fade out a circle")
                content.append("        circle = Circle(color=BLUE)")
                content.append("        self.play(Create(circle))")
                content.append("        self.wait(1)")
                content.append("        self.play(FadeOut(circle))")
                content.append("        self.wait(1)")
            elif "square" in description.lower():
                content.append("        # Fade out a square")
                content.append("        square = Square(color=RED)")
                content.append("        self.play(Create(square))")
                content.append("        self.wait(1)")
                content.append("        self.play(FadeOut(square))")
                content.append("        self.wait(1)")
    
    # If no specific animation was matched, create a default one
    if not content:
        content.append("        # Default animation")
        content.append("        text = Text(f\"Animation based on: {description}\", font_size=24)")
        content.append("        self.play(Write(text))")
        content.append("        self.wait(2)")
    
    # Format the content into the template
    formatted_content = "\n".join(content)
    
    manim_code = template.format(description=description, content=formatted_content)
    
    return manim_code
