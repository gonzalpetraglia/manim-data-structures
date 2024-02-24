from manim import Scene, Rectangle, Group, GrowArrow, Text, MarkupText, Arrow, LEFT, RIGHT, DOWN, FadeIn, AnimationGroup, MoveAlongPath, Line, BLUE_E, BLUE, DARK_BLUE, WHITE, FadeOut, BLACK, UP, MovingCameraScene, GREY, DARK_BROWN, GREY_BROWN, Circle
import math

SST_COLOR = DARK_BLUE
BORDERS_COLOR = BLUE

def draw_shorter_arrow(start, end, max_tip_length_to_length_ratio=0.25):
    shorter_start = start + (end - start) * 0.05
    shorter_end = start + (end - start) * 0.95
    return draw_shorter_arrow(shorter_start, shorter_end, max_tip_length_to_length_ratio=max_tip_length_to_length_ratio)

def draw_arrow(start, end,  max_tip_length_to_length_ratio=0.25):
    a = Arrow(start=start, end=end, max_tip_length_to_length_ratio=max_tip_length_to_length_ratio)
    # a.put_start_and_end_on(start, end)
    return a

def draw_array(array, length=None, width_of_cell=2):
    length_to_draw = length or len(array)
    r =  Rectangle(width=width_of_cell*length_to_draw, grid_xstep=width_of_cell, color=BORDERS_COLOR)

    return r


def scale_and_center(drawing, scene):
    width = max(drawing.height * 16/9, drawing.width) * 1.1
    scene.camera.frame.set(width=width).move_to(drawing)

def animated_scale_and_center(drawing, scene):
    width = max(drawing.height * 16/9, drawing.width) * 1.1
    return scene.camera.frame.animate.set(width=width).move_to(drawing)

def animated_scale_and_center_partial(drawing, whole, scene):
    width = max(drawing.height * 16/9, drawing.width) * 1.1
    return scene.camera.frame.animate.set(width=width).move_to(drawing)

def get_cell(rectangle, position, width_of_cell):
    return rectangle.get_left() + RIGHT * width_of_cell * (position + 0.5)
    

def get_bottom_cell(rectangle, position):
    return rectangle.get_corner(DOWN+LEFT) + RIGHT * width_of_cell * (position + 0.5)
    

def get_bottom_left_cell(rectangle, position):
    return rectangle.get_corner(DOWN+LEFT) + RIGHT * width_of_cell * position
    

def animated_move_to_next_cell(mobject):
    return mobject.animate.shift(RIGHT * 2)

used_level = 0

def merge_level(scene, level_nr, sstables_in_level, levels, sstables_per_level):
    global used_level
    g = Group(*sstables_in_level[level_nr])
    original_center = g.get_center()
    r = Rectangle(width = (level_nr + 1) * 2 + 1.5, height=1.5, color=SST_COLOR, fill_opacity=1, fill_color=BLACK).move_to(original_center)
    t = Text("SST").move_to(r)
    if (used_level < level_nr + 1):
        used_level = level_nr + 1
        scene.wait(2)
    scene.play(AnimationGroup(FadeOut(g), FadeIn(r), FadeIn(t), run_time=(level_nr + 1) / used_level))
    new_sstable = Group(r, t)
    if(len(sstables_in_level[level_nr + 1]) == sstables_per_level):
        merge_level(scene, level_nr + 1, sstables_in_level, levels, sstables_per_level)
    scene.play(MoveAlongPath(new_sstable, Line(start=original_center, end=get_cell(levels[level_nr + 1], len(sstables_in_level[level_nr + 1]), (level_nr + 2) * 2)), run_time=(level_nr + 1) / used_level))
    sstables_in_level[level_nr + 1].append(new_sstable)
    sstables_in_level[level_nr] = []

class AnimateMergeSSTable(MovingCameraScene):
    def construct(self):
        qty_levels = 3
        sstables_per_level = 3
        qty_tuples = 50
        tuples_per_mem_table = 3



        mem_tables = [Rectangle(color=BORDERS_COLOR, width=5, height=8, fill_opacity=1,z_index=-1).set_fill(BLACK).set_sheen_direction(UP) for i in range(2)]
        levels = [draw_array([], sstables_per_level, (i + 1) * 2) for i in range(qty_levels)]

        mem_group = Group(*mem_tables)
        disk_group = Group(*levels)

        mem_group.arrange(RIGHT, center=False, aligned_edge=UP)
        disk_group.arrange(DOWN, center=False, aligned_edge=LEFT)

        mem_labels = [MarkupText("M<sub>{}</sub>".format(str(i)), z_index=-0.5) for i in range(2)]
        disk_labels = [MarkupText("D<sub>{}</sub>".format(str(i + 1))) for i in range(qty_levels)]
        
        complete_drawing = Group(mem_group, disk_group)

        complete_drawing.arrange(DOWN, center=False, aligned_edge=LEFT)
        for (i, label) in enumerate(mem_labels):
            label.move_to(mem_tables[i])
        

        for (i, label) in enumerate(disk_labels):
            label.next_to(levels[i], LEFT)


        self.add(complete_drawing)
        self.add(Group(*(mem_labels + disk_labels)))

        scale_and_center(Group(complete_drawing, Text("r").move_to(mem_group.get_top() + UP)), self)


        active_mem_table = 0
        tuples_in_mem = 0
        sstables_in_level = [[] for l in range(qty_levels)]
        animation_time_mem_loading = 3
        for i in range(qty_tuples):
            new_tuple = Group(Circle(color=BLUE, stroke_width=5, fill_opacity=1, fill_color=BLACK), Text(str(i)))

            if i == 1:
                animation_time_mem_loading = 1
            if i == 3:
                animation_time_mem_loading = 0.5
            if i == 6:
                animation_time_mem_loading = 0.25
            if i == 12:
                animation_time_mem_loading = 0.1

            self.play(MoveAlongPath(new_tuple, Line(start=mem_group.get_top() + UP, end=mem_group[active_mem_table].get_top()), run_time=animation_time_mem_loading))
            tuples_in_mem += 1
            self.play(
                    FadeOut(new_tuple, run_time=animation_time_mem_loading),
                    mem_tables[active_mem_table].animate(run_time=animation_time_mem_loading).set_fill([SST_COLOR for i in range(tuples_in_mem * 8)] + [BLACK for i in range(tuples_per_mem_table * 8- tuples_in_mem * 8)])
            )

            if tuples_in_mem == tuples_per_mem_table:
                print(active_mem_table)
                sstable_rec = Rectangle(width = 1.5, height=1.5, color=SST_COLOR, fill_opacity=1, fill_color=BLACK).move_to(mem_tables[active_mem_table])
                t = Text("SST").move_to(sstable_rec)
                sstable = Group(sstable_rec, t)
                self.play(
                    AnimationGroup(
                        FadeIn(sstable_rec, scale=5/1.5),
                        mem_tables[active_mem_table].animate(run_time=animation_time_mem_loading).set_fill(BLACK),
                        FadeIn(t, run_time=animation_time_mem_loading)
                    )
                )
                active_mem_table = 1 - active_mem_table
                tuples_in_mem = 0
                if len(sstables_in_level[0]) == sstables_per_level:
                    merge_level(self, 0, sstables_in_level, levels, sstables_per_level)
                self.play(MoveAlongPath(sstable, Line(start=sstable_rec.get_center(), end=get_cell(levels[0], len(sstables_in_level[0]), 2)), run_time=animation_time_mem_loading))
                sstables_in_level[0].append(sstable)

        self.wait(5)