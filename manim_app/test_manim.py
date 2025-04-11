from manim import *

class TestScene(Scene):
    def construct(self):
        # Create a circle
        circle = Circle(color=BLUE)
        
        # Create a square
        square = Square(color=RED)
        
        # Position the square
        square.next_to(circle, RIGHT)
        
        # Add both shapes to the scene
        self.play(Create(circle))
        self.wait(1)
        self.play(Create(square))
        self.wait(1)
        
        # Transform the circle into a triangle
        triangle = Triangle(color=GREEN)
        triangle.move_to(circle.get_center())
        self.play(Transform(circle, triangle))
        self.wait(1)
        
        # Add text
        text = Text("Manim is working!", color=YELLOW)
        text.scale(0.5)
        text.next_to(square, UP)
        self.play(Write(text))
        self.wait(2)
