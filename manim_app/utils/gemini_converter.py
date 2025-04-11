import google.generativeai as genai
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiTextToManimConverter:
    """
    A class to convert natural language descriptions to Manim code using Google's Gemini 1.5 Pro API.
    """
    
    def __init__(self, api_key):
        """
        Initialize the converter with the Google API key.
        
        Args:
            api_key (str): Google API key for Gemini
        """
        self.api_key = api_key
        self._configure_api()
        
    def _configure_api(self):
        """Configure the Gemini API with the provided key."""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Error configuring Gemini API: {str(e)}")
            raise
    
    def convert_to_manim_code(self, description, job_id=None):
        """
        Convert a natural language description to Manim code using Gemini.
        
        Args:
            description (str): Natural language description of the animation
            job_id (str, optional): Unique identifier for the job
            
        Returns:
            str: Generated Manim code
        """
        try:
            # Create a prompt that instructs Gemini to generate Manim code
            prompt = self._create_prompt(description)
            
            # Generate the code using Gemini
            response = self.model.generate_content(prompt)
            
            # Extract and format the Manim code
            manim_code = self._extract_code(response.text)
            
            logger.info(f"Successfully generated Manim code for description: '{description}'")
            return manim_code
            
        except Exception as e:
            logger.error(f"Error generating Manim code: {str(e)}")
            # Fall back to a simple template if Gemini fails
            return self._fallback_template(description)
    
    def _create_prompt(self, description):
        """
        Create a detailed prompt for Gemini to generate Manim code.
        
        Args:
            description (str): Natural language description of the animation
            
        Returns:
            str: Formatted prompt for Gemini
        """
        return f"""
        You are an expert in creating mathematical animations using the Manim library.
        
        Please generate Python code using Manim to create the following animation:
        
        "{description}"
        
        Requirements:
        1. Use the latest Manim Community version syntax
        2. Create a single Scene class named "ManimScene" that inherits from Scene
        3. Include all necessary imports at the top
        4. Add detailed comments explaining the code
        5. Make the animation visually appealing with appropriate colors and timing
        6. Ensure the code is complete and ready to run
        7. If the description mentions 3D, use appropriate 3D objects and camera settings
        
        Return ONLY the Python code without any additional text or explanations.
        The code should start with imports and be fully functional when executed.
        """
    
    def _extract_code(self, response_text):
        """
        Extract the code from the Gemini response.
        
        Args:
            response_text (str): Raw text response from Gemini
            
        Returns:
            str: Cleaned Manim code
        """
        # Remove any markdown code block indicators if present
        code = response_text.replace("```python", "").replace("```", "").strip()
        
        # Ensure the code has the necessary imports
        if "from manim import" not in code:
            code = "from manim import *\n\n" + code
        
        # Ensure the code has a ManimScene class
        if "class ManimScene" not in code:
            # This is a fallback if the model didn't follow instructions
            code = code.replace("class ", "class ManimScene(Scene):\n    def construct(self):\n        # ")
        
        return code
    
    def _fallback_template(self, description):
        """
        Provide a simple fallback template if Gemini fails.
        
        Args:
            description (str): Natural language description of the animation
            
        Returns:
            str: Basic Manim code template
        """
        return f"""
from manim import *

class ManimScene(Scene):
    def construct(self):
        # Animation based on: {description}
        text = Text("Animation description:", font_size=36)
        desc = Text("{description}", font_size=24)
        desc.next_to(text, DOWN)
        
        self.play(Write(text))
        self.wait(0.5)
        self.play(FadeIn(desc))
        self.wait(2)
        """
