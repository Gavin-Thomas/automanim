from manim import *

class ManimScene(Scene):
    def construct(self):
        # Generated from description: Create a blue circle
        
        # Create a circle
        circle = Circle(color=BLUE)
        self.play(Create(circle))
        self.wait(1)
