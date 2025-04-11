# Gemini API Integration for Manim Animation Generator

This document describes the integration of Google's Gemini 2.5 Pro API into the Manim Animation Generator application to enhance text-to-code conversion capabilities.

## Overview

The Manim Animation Generator now uses Google's Gemini 2.5 Pro API to convert natural language descriptions into Manim code. This significantly enhances the application's ability to generate complex animations and 3D scenes from simple text descriptions.

## Features Added

- **Advanced Text-to-Code Conversion**: Generate sophisticated Manim code from natural language descriptions
- **Support for Complex Animations**: Create intricate animations that weren't possible with the template-based approach
- **3D Scene Support**: Generate code for 3D scenes and objects with proper camera settings
- **Mathematical Equation Rendering**: Create animations with complex mathematical equations
- **Fallback Mechanism**: Automatically falls back to template-based approach if the Gemini API fails

## Implementation Details

The integration is implemented in two main components:

1. **GeminiTextToManimConverter Class** (`utils/gemini_converter.py`):
   - Handles communication with the Gemini API
   - Formats prompts to generate high-quality Manim code
   - Processes and cleans up the generated code
   - Provides fallback mechanisms for error handling

2. **Enhanced Backend Integration** (`backend/text_to_manim.py`):
   - Replaces the original template-based text_to_manim_code function
   - Uses the GeminiTextToManimConverter for text-to-code conversion
   - Falls back to the original template-based approach if needed

## Example Usage

The integration allows for much more complex animation descriptions, such as:

```
"Create a 3D torus that rotates while a mathematical equation appears"
```

Which generates sophisticated Manim code like:

```python
from manim import *
class ManimScene(ThreeDScene):
    def construct(self):
        # Set up 3D camera
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        self.begin_ambient_camera_rotation(rate=0.2)
        # Create a torus
        torus = Torus(major_radius=2, minor_radius=1, color=BLUE).set_gloss(1)
        # Create the mathematical equation
        equation = MathTex(r"\oint_C \vec{F} \cdot d\vec{r} = \iint_S (\nabla \times \vec{F}) \cdot d\vec{S}")\
            .set_color_by_gradient(RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE)\
            .scale(0.7)\
            .to_edge(UL)
        # Add torus and equation to the scene
        self.add(torus, equation)
        # Animate the rotation of the torus
        self.play(
            Rotate(torus, angle=2 * PI, axis=OUT, rate_func=smooth), # Rotate around Z-axis (OUT)
            run_time=5
        )
        self.wait(1)
```

## Configuration

The Gemini API integration uses the following configuration:

- **API Key**: Set via environment variable `GEMINI_API_KEY` or use the provided default key
- **Model**: Uses the `gemini-1.5-pro` model for high-quality code generation
- **Timeout**: 120 seconds for complex animations (increased from 60 seconds)

## Future Improvements

Potential future enhancements to the Gemini API integration:

1. **Fine-tuning**: Train the model specifically on Manim code for better results
2. **Interactive Refinement**: Allow users to refine the generated code through conversation
3. **Style Customization**: Let users specify animation style preferences
4. **Code Explanation**: Generate explanations of the code for educational purposes
5. **Performance Optimization**: Cache common animations to reduce API calls

## Conclusion

The integration of Google's Gemini 2.5 Pro API significantly enhances the Manim Animation Generator's capabilities, allowing for the creation of complex mathematical animations from simple text descriptions. This brings the application closer to its goal of making mathematical animation creation accessible to everyone, regardless of their programming experience.
