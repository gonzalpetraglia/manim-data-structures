from manim import *


class UnionExample(Scene):
    def construct(self):
        sq = Square(color=RED, fill_opacity=1)
        sq.move_to([-2, 0, 0])
        cr = Circle(color=BLUE, fill_opacity=1)
        cr.move_to([-1.3, 0.7, 0])
        un = Union(sq, cr, color=GREEN, fill_opacity=1).set_fill(BLACK, opacity=1)
        self.add(sq, cr, un)
        un.add_updater(lambda x: x.become(Union(sq, cr, color=GREEN, fill_opacity=1).set_fill(BLACK, opacity=1)))
        self.play(cr.animate(run_time=5).move_to([-2.5, 0.7, 0]))
        self.wait()