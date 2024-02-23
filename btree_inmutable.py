from manim import Scene, Rectangle, Group, GrowArrow, Text,Arrow, LEFT, RIGHT, DOWN, FadeIn, AnimationGroup, MoveAlongPath, Line, BLUE, WHITE, FadeOut, BLACK, UP, MovingCameraScene
import math

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

MAX = 9999999
class MergeIterator:

  def __init__(self, input_arrays):
    self.input_arrays = input_arrays
    self.pointers = [0 for _ in input_arrays]

  def __get_heads(self):
    return [((i, array[pointer]) if len(array) > pointer else (i, MAX)) for (i, (pointer, array)) in enumerate(zip(self.pointers, self.input_arrays))]

  def __iter__(self):
    return self

  def __next__(self):
    n = min(self.__get_heads(), key=lambda t: t[1])    

    if n[1] != MAX:
        self.pointers[n[0]] += 1
        return (n[0], n[1], self.pointers[n[0]] - 1)
    else:
        raise StopIteration

def draw_shorter_arrow(start, end, max_tip_length_to_length_ratio=0.25):
    shorter_start = start + (end - start) * 0.05
    shorter_end = start + (end - start) * 0.95
    return draw_shorter_arrow(shorter_start, shorter_end, max_tip_length_to_length_ratio=max_tip_length_to_length_ratio)

def draw_arrow(start, end,  max_tip_length_to_length_ratio=0.25):
    a = Arrow(start=start, end=end, max_tip_length_to_length_ratio=max_tip_length_to_length_ratio)
    # a.put_start_and_end_on(start, end)
    return a

def draw_array(array, length=None):
    length_to_draw = length or len(array)
    texts = [Text(str(k)) for k in array]
    r =  Rectangle(width=2*length_to_draw, grid_xstep=2.0, color=BLUE)

    for (i, t) in enumerate(texts):
        t.shift(get_cell(r, i))
    g =  Group(
        r,
        *texts
    )
    return g


def scale_and_center(drawing, scene):
    width = max(drawing.height * 16/9, drawing.width) * 1.1
    scene.camera.frame.set(width=width).move_to(drawing)

def animated_scale_and_center(drawing, scene):
    width = max(drawing.height * 16/9, drawing.width) * 1.1
    return scene.camera.frame.animate.set(width=width).move_to(drawing)

def animated_scale_and_center_partial(drawing, whole, scene):
    width = max(drawing.height * 16/9, drawing.width) * 1.1
    return scene.camera.frame.animate.set(width=width).move_to(drawing)

def get_cell(rectangle, position):
    return rectangle.get_left() + RIGHT * (2 * position + 1)
    

def get_bottom_cell(rectangle, position):
    return rectangle.get_corner(DOWN+LEFT) + RIGHT * (2 * position + 1)
    

def get_bottom_left_cell(rectangle, position):
    return rectangle.get_corner(DOWN+LEFT) + RIGHT * 2 * position
    

def animated_move_to_next_cell(mobject):
    return mobject.animate.shift(RIGHT * 2)

class AnimateMergeSSTable(MovingCameraScene):
    def construct(self):
        input_arrays = [
            [
                1,5,6
            ],
            [
                3,8,9,12
            ],
            [
                7,10,11
            ]
        ]
        
        output_arrays_length = 3

        # Create rectangles
        rs = [draw_array(a) for a in input_arrays]
        
        # Create pointers in array

        arrows = [draw_arrow(get_bottom_cell(r, 0) + DOWN * 1.2, get_bottom_cell(r, 0), max_tip_length_to_length_ratio=300) for r in rs]

        for a in arrows:
            a.tip_length = 0.6
        pointed_arrays = [Group(r, a) for (r, a) in zip(rs, arrows)]

        # Order rectangles
        # for (i, r) in enumerate(pointed_arrays[1:]):
        #     r.next_to(pointed_arrays[i], DOWN * 10)

        # Scale and center
        input_group = Group(*pointed_arrays)
        input_group.arrange(DOWN, center=False, aligned_edge=LEFT)
        scale_and_center(input_group, self)

        # Add to scene
        self.add(input_group)

        m = MergeIterator(input_arrays)
        position = 0
        output_array = None
        complete_drawing = input_group

        output_rectangles = []
        texts = []
        keys = []
        output_arrows = []

        for (array_number, value, index) in m:
            if position % output_arrays_length == 0:
                texts.append([])
                keys.append([])
                new_output_array = draw_array([], output_arrays_length)
                new_output_array.next_to(complete_drawing, RIGHT * 10)

                new_elements = [new_output_array]
                output_rectangles.append(new_output_array)
                if output_array is not None:
                    a = draw_arrow(output_array.get_right(),new_output_array.get_left())
                    new_elements.append(a)
                    output_arrows.append(a)
                output_array = new_output_array
                complete_drawing = Group(complete_drawing, *new_elements)
                self.play(FadeIn(Group(*new_elements)))
                self.play(animated_scale_and_center(complete_drawing, self))

                
            self.play(arrows[array_number].animate.set_color(BLUE))
            t = Text(str(value))
            texts[-1].append(t)
            keys[-1].append(value)

            self.play(MoveAlongPath(t, Line(get_cell(rs[array_number], index), get_cell(output_array, position%output_arrays_length))))
            complete_drawing = Group(complete_drawing, t)
            if index == len(input_arrays[array_number]) - 1:
                self.play(arrows[array_number].animate.set_color(BLACK)) # Instead of fadeout in order for it to not reappear
            else:
                self.play(arrows[array_number].animate.set_color(WHITE))
                self.play(animated_move_to_next_cell(arrows[array_number]))
            position += 1

        flattened_text = [t
                            for ts in texts
                            for t in ts
                        ]
        btree_group = Group(*(flattened_text + output_rectangles + output_arrows))
        self.play(animated_scale_and_center_partial(btree_group, complete_drawing, self))
        self.play(FadeOut(input_group))
        self.wait()

        qty_values = output_arrays_length
        previous_layer_rectangles = output_rectangles
        last_layer_keys = keys
        while len(previous_layer_rectangles) != 1:
            intermmediate_nodes = []
            intermmediate_keys = []
            qty_new_nodes = math.ceil(len(previous_layer_rectangles) / qty_values)
            for (nodes, tex) in zip(chunks(previous_layer_rectangles, qty_values), chunks(last_layer_keys, qty_values)):
                new_intermmediate_node = draw_array([], output_arrays_length)
                new_intermmediate_node.move_to(Group(*nodes).get_top()).shift(UP * 4)
                intermmediate_nodes.append(new_intermmediate_node)
                intermmediate_keys.append([tex[0][0],tex[-1][-1]])
                self.play(FadeIn(new_intermmediate_node))
                btree_group = Group(btree_group, new_intermmediate_node)
                self.play(animated_scale_and_center(btree_group, self))

                arrows = [draw_arrow(get_bottom_cell(new_intermmediate_node, i), n.get_top()) for (i, n) in enumerate(nodes)]
                self.play(AnimationGroup(*[GrowArrow(a) for a in arrows], lag_ratio=0.5))
                keys = [(Text("{}-{}".format(t[0], t[-1])), node.get_center(), get_cell(new_intermmediate_node, i)) for (i, (node,t)) in enumerate(zip(nodes, tex))]
                self.play(AnimationGroup(*[MoveAlongPath(k, Line(start=start, end=end)) for (k, start, end) in keys]))
                btree_group = Group(btree_group, *(arrows + [k[0] for k in keys]))
            
            previous_layer_rectangles = intermmediate_nodes
            last_layer_keys = intermmediate_keys
        
        self.wait(5)
        

