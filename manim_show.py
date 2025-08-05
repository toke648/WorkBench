from manim import *

"""
创建一个圆形，并将其转换为正方形，并旋转


manim -pql manim_show.py CircleToSquare

"""

class CircleToSquare(Scene):
    def construct(self):
        # 创建一个圆形
        circle = Circle(color=BLUE, fill_opacity=0.5)
        
        # 创建一个正方形
        square = Square(color=GREEN, fill_opacity=0.5)
        
        # 添加圆形到场景
        self.play(Create(circle))
        self.wait(0.5)
        
        # 将圆形转换为正方形
        self.play(Transform(circle, square))
        self.wait(1)
        
        # 旋转正方形
        self.play(Rotate(circle, angle=PI/4))
        self.wait(1)
    