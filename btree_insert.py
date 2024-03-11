from manim import Scene, Rectangle, Group, GrowArrow, Text, MarkupText, Arrow, LEFT, RIGHT, DOWN, FadeIn, AnimationGroup, MoveAlongPath, Line, BLUE_E, BLUE, DARK_BLUE, WHITE, FadeOut, BLACK, UP, MovingCameraScene, GREY, DARK_BROWN, GREY_BROWN, Circle
import math
import random

BORDERS_COLOR = BLUE

tuples_per_leaf = 3
nodes_per_node = 3
root = None


def draw_shorter_arrow(start, end, max_tip_length_to_length_ratio=0.25):
    shorter_start = start + (end - start) * 0.05
    shorter_end = start + (end - start) * 0.95
    return draw_shorter_arrow(shorter_start, shorter_end, max_tip_length_to_length_ratio=max_tip_length_to_length_ratio)

def draw_arrow(start, end,  max_tip_length_to_length_ratio=0.25):
    a = Arrow(start=start, end=end, max_tip_length_to_length_ratio=max_tip_length_to_length_ratio)
    # a.put_start_and_end_on(start, end)
    return a

def draw_array(length, width_of_cell=2):
    r =  Rectangle(width=width_of_cell*length, grid_xstep=width_of_cell, color=BORDERS_COLOR)

    return r


def scale_and_center(scene):
    drawing = root.get_all_elements()
    
    width = max(drawing.height * 16/9, drawing.width + 4 * tuples_per_leaf)
    scene.camera.frame.set(width=width).move_to(drawing)

def animated_scale_and_center(scene, extra=None):
    drawing = root.get_all_elements()
    if extra:
        print(drawing.width)
        drawing = Group(drawing, extra)
    width = max(drawing.height * 16/9, drawing.width + 4 * tuples_per_leaf)
    return scene.camera.frame.animate.set(width=width).move_to(drawing)

def animated_scale_and_center_partial(whole, scene):
    drawing = root.get_all_elements()
    width = max(drawing.height * 16/9, drawing.width + 4 * tuples_per_leaf)
    return scene.camera.frame.animate.set(width=width).move_to(drawing)

def get_cell_custom_init(custom_init, position, width_of_cell=2):
    return custom_init + RIGHT * width_of_cell * (position + 0.5)
    
def get_cell(rectangle, position, width_of_cell=2):
    return get_cell_custom_init(rectangle.get_left(), position, width_of_cell)
    

def get_bottom_cell(rectangle, position, width_of_cell=2):
    return rectangle.get_corner(DOWN+LEFT) + RIGHT * width_of_cell * (position + 0.5)
    

def get_bottom_left_cell_custom_init(custom_init, position, width_of_cell=2):
    return custom_init + RIGHT * width_of_cell * position
    

def get_bottom_left_cell(rectangle, position, width_of_cell=2):
    return get_bottom_left_cell_custom_init(rectangle.get_corner(DOWN+LEFT), position, width_of_cell)

def animated_move_to_next_cell(mobject):
    return mobject.animate.shift(RIGHT * 2)

class Node():
    def __init__(self):
        self.inited = False
    

    def get_all_elements(self):
        return Group(self.drawing, *(self.drawn_keys))
    
    def find_position_to_insert(self, key):
        low = -1
        high = len(self.keys)

        while low + 1 < high:
            mid = low + (high - low) // 2
            if (key > self.keys[mid]):
                low = mid
            else:
                high = mid

        if high >= len(self.keys) or self.keys[high] != key:
            return -high - 1
        else:
            return high
    
    def _take_keys(self, avoided_position=None):
        return self._take_keys_custom_init(self.drawing.get_left(), avoided_position)

    def _take_keys_custom_init(self, custom_init, avoided_position=None):
        return [k.animate.move_to(get_cell_custom_init(custom_init, i)) for (i, k) in enumerate(self.drawn_keys) if i !=avoided_position]


class IntermmediateNode(Node):
    def init_root(self, key, split_drawn_key, first_child, second_child, scene):
        self.keys = [key]
        self.parent = None
        self.childs = [first_child, second_child]

        self.drawing = draw_array(nodes_per_node - 1)
        self.drawing

        self._center_for_childs()

        self.drawn_keys = [split_drawn_key]
        self.left_sibling = None
        self.right_sibling = None
        self.drawn_child_links = [
            draw_arrow(
                get_bottom_left_cell(self.drawing, i),
                k.drawing.get_top()
            ) for (i,k) in enumerate(self.childs)]
        global root
        root = self
        scene.play(FadeIn(self.drawing))
        scene.play(self._take_keys())
        scene.play(AnimationGroup(*[GrowArrow(a) for a in self.drawn_child_links]))
        self.inited = True


    def init_split(self, scene, drawing, keys, childs, drawn_keys, drawn_child_links, parent, left_sibling, right_sibling, self_is_left):
        self.keys = keys
        self.parent = parent
        self.left_sibling = left_sibling
        self.right_sibling = right_sibling

        if self.right_sibling is not None:
            self.right_sibling.left_sibling = self
        if self.left_sibling is not None:
            self.left_sibling.right_sibling = self

        self.childs = childs
        self.drawn_keys = drawn_keys
        self.drawn_child_links = drawn_child_links

        self.drawing = drawing


        self._center_for_childs_animate(scene)
        
        for c in self.childs:
            c.parent = self

        scene.play(animated_scale_and_center(scene, self.drawing))
        
        self.inited = True

    def get_all_elements(self):
        return Group(super().get_all_elements(), *(self.drawn_child_links + [c.get_all_elements() for c in self.childs]))

    def insert_node(self, key, drawn_key, node, is_left_child, scene):
        if len(self.childs) < nodes_per_node:
            self._simple_insert(key, drawn_key, node, is_left_child, scene)
        else:
            self._non_simple_insert(key, drawn_key, node, is_left_child, scene)

        self._center_for_childs_animate(scene)

    def _simple_insert(self, key, drawn_key, new_child, is_left_child, scene):
        new_key_position = self.find_position_to_insert(key)
        
        new_key_position = - new_key_position - 1  

        new_child_position = new_key_position if is_left_child else new_key_position + 1

        self.keys = self.keys[0:new_key_position] + [key] + self.keys[new_key_position:]
        self.childs = self.childs[0:new_child_position] + [new_child] + self.childs[new_child_position:]

        # add new key and node stretching
        t = drawn_key
        a = draw_arrow(get_bottom_left_cell(self.drawing, new_child_position), new_child.drawing.get_top())
        self.drawn_keys = self.drawn_keys[0:new_key_position] + [t] + self.drawn_keys[new_key_position:]
        self.drawn_child_links = self.drawn_child_links[0:new_child_position] + [a] + self.drawn_child_links[new_child_position:]
        scene.play(self._take_keys(new_key_position))
        scene.play(self.__take_child_links(new_child_position))
        scene.play(t.animate.move_to(get_cell(self.drawing, new_key_position)))
        scene.play(GrowArrow(a))


    def _non_simple_insert(self, key, drawn_key, node, is_left_child, scene):

        must_init_parent = False
        if self.parent is None:
            self.parent = IntermmediateNode()
            must_init_parent = True
        new_sibling = IntermmediateNode()

        new_rectangle = draw_array(nodes_per_node - 1).move_to(self.drawing).shift(RIGHT * 2)
        scene.play(FadeIn(new_rectangle))

        self._simple_insert(key, drawn_key, node, is_left_child, scene)
        
        split_key_position = (len(self.keys) + 1) // 2 - 1# this is the last one of the left sibling
        childs_on_left = split_key_position + 1 # this will go for the parent

        split_key = self.keys[split_key_position]
        split_drawn_key = self.drawn_keys[split_key_position]
        
        new_sibling.init_split(scene, new_rectangle, self.keys[split_key_position + 1:], self.childs[childs_on_left:], self.drawn_keys[split_key_position + 1:], self.drawn_child_links[childs_on_left:],self.parent, self, self.right_sibling, True)
        self.keys = self.keys[0:split_key_position]
        self.drawn_keys = self.drawn_keys[0:split_key_position]
        self.drawn_child_links = self.drawn_child_links[0:childs_on_left]
        self.childs = self.childs[0:childs_on_left]
        self.right_sibling = new_sibling

        if must_init_parent:
            self.parent.init_root(split_key, split_drawn_key, self, new_sibling, scene)
        else:
            self.parent.insert_node(split_key, split_drawn_key, new_sibling, False, scene)

    def _center_for_childs_animate(self, scene):

        childs = Group(*[c.drawing for c in self.childs])
        new_center = childs.get_top() + UP * 5
        centering_animations = []
        if self.parent and self.parent.inited:
            centering_animations.append(
                self.parent.adjust_child_link(self, new_center + UP * self.drawing.height / 2)
            )

        centering_animations.append(self.drawing.animate.move_to(new_center))
        centering_animations.append(self._take_keys_custom_init(new_center + self.drawing.width * LEFT / 2))
        centering_animations.append(self.__take_child_links_custom_init(new_center + self.drawing.width * LEFT / 2 + self.drawing.height * DOWN / 2))
        scene.play(AnimationGroup(*centering_animations))

        if self.parent and self.parent.inited:
            self.parent._center_for_childs_animate(scene)

    def adjust_child_link(self, child, new_end):

        i = self.childs.index(child)
        return self._move_start_arrow(self.drawn_child_links[i], self.drawn_child_links[i].start, new_end)
    def _center_for_childs(self):
        childs = Group(*[c.drawing for c in self.childs])

        self.drawing.move_to(childs.get_top() + UP * 5)

    def _move_start_arrow(self, arrow, new_start, new_end):
        arrow.start = new_start
        arrow.end = new_end
        return arrow.animate.put_start_and_end_on(new_start, new_end)

    def insert(self, key, scene):

        position = self.find_position_to_insert(key)

        if position >= 0:
            position +=1
        else:
            position = - position - 1

        self.childs[position].insert(key, scene)
        return self.parent if self.parent is not None else self

    def __take_child_links(self, avoided_position=None):
        return self.__take_child_links_custom_init(self.drawing.get_corner(DOWN+LEFT), avoided_position)

    def __take_child_links_custom_init(self, custom_init, avoided_position=None):
        return AnimationGroup(*[self._move_start_arrow(a, get_bottom_left_cell_custom_init(custom_init, i), n.drawing.get_top()) for (i, (a, n)) in enumerate(zip(self.drawn_child_links, self.childs))  if i !=avoided_position])

class Leaf(Node):

    def init_first(self, scene):
        self.keys = []
        self.parent = None
        self.drawn_keys = []
        self.left_sibling = None
        self.right_sibling = None

        self.drawing = draw_array(tuples_per_leaf)
        scene.add(self.drawing)

        self.inited = True

    def init_split(self, scene, drawing, keys, drawn_keys, parent, left_sibling, right_sibling, is_sibling_left):
        
        self.keys = keys
        self.parent = parent
        self.drawn_keys = drawn_keys
        self.right_sibling = right_sibling
        self.left_sibling = left_sibling

        self.left_sibling.right_sibling = self
        if self.right_sibling is not None:
            self.right_sibling.left_sibling = self

        self.drawing = drawing

        if self.right_sibling is not None:
            print('has something to the right')
            old_center = self.right_sibling.drawing.get_center() 

            scene.play(self.right_sibling.move_to_right(RIGHT * (self.drawing.width + 3)))
        
        new_center = self.left_sibling.drawing.get_center() + RIGHT * (self.drawing.width + 3)
        scene.play(
            self.drawing.animate.move_to(self.left_sibling.drawing.get_center() + RIGHT * (self.drawing.width + 3)),
            self._take_keys_custom_init(new_center +  LEFT * self.drawing.width / 2)
        )
        scene.play(animated_scale_and_center(scene, self.drawing))
        
        self.inited = True

    def move_to_right(self, amount):

        if self.right_sibling is not None:
            return AnimationGroup(
                self.drawing.animate.shift(amount),
                Group(*[d for d in self.drawn_keys]).animate.shift(amount),
                self.right_sibling.move_to_right(amount)
            )

        return AnimationGroup(
            self.drawing.animate.shift(amount),
            Group(*[d for d in self.drawn_keys]).animate.shift(amount)
        )

    def insert(self, key, scene):

        if len(self.keys) < tuples_per_leaf:
            self.simple_insert(key, scene)
        else:
            self._non_simple_insert(key, scene)

        return self.parent if self.parent is not None else self

    def _non_simple_insert(self, key, scene):
        
        must_init_parent = False
        if self.parent is None:
            self.parent = IntermmediateNode()
            must_init_parent = True
        new_sibling = Leaf()
        split_position = (len(self.keys ) + 1) // 2

        new_rectangle = draw_array(tuples_per_leaf).move_to(self.drawing).shift(RIGHT * 2)
        scene.play(FadeIn(new_rectangle))

        self.simple_insert(key, scene)

        new_sibling.init_split(scene, new_rectangle, self.keys[split_position:], self.drawn_keys[split_position:], self.parent, self, self.right_sibling, True)
        self.keys = self.keys[0:split_position]
        self.drawn_keys = self.drawn_keys[0:split_position]
        self.right_sibling = new_sibling

        if must_init_parent:
            self.parent.init_root(new_sibling.get_limit(), new_sibling.drawn_keys[0].copy(), self, new_sibling, scene)
        else:
            self.parent.insert_node(new_sibling.get_limit(), new_sibling.drawn_keys[0].copy(), new_sibling, False, scene)
        

    def simple_insert(self, key, scene):
        position = self.find_position_to_insert(key)
        if position >= 0:
            raise Exception("Already exists")
        position = - position - 1
        self.keys = self.keys[0:position] + [key] + self.keys[position:]
        new_text = Text(str(key)).move_to(get_cell(self.drawing, position))
        if len(self.drawn_keys[position:]) != 0:
            scene.play(AnimationGroup(*[t.animate.shift(2 * RIGHT) for t in self.drawn_keys[position:]]))
        self.drawn_keys = self.drawn_keys[0:position] + [new_text] + self.drawn_keys[position:]
        scene.play(FadeIn(new_text))

    def get_limit(self):
        return self.keys[0]

class AnimateMergeSSTable(MovingCameraScene):
    def construct(self):
        tuples_to_insert = tuples_per_leaf * 2 -1
        global root
        root = Leaf()
        root.init_first(self)
        scale_and_center(self)

        insert_list = list(range(tuples_to_insert))
        random.shuffle(insert_list)
        # insert_list = [1,4,7,8,2,3,12,5,11,13, 9,6,10,15,14, 18, 20, 2.5, 3.5, 1.5, 3.3, 6.7, 38]
        insert_list = [1,4,7,8,2,3,12,5,11]
        for i in insert_list:
            root = root.insert(i, self)
            self.play(animated_scale_and_center(self))            

        