import hashlib
import manim
from merkle_tree_model import MerkleTree, LeafNode, IntermediaryNode


def create_connecting_line(object_1, object_2):
    return manim.Line(
                object_1.get_center(), 
                object_2.get_center(),
                stroke_width=2.5,
                z_index=-10
            )

class MerkleTreeViewModel:
    def __init__(self, data, hash_function_leaves=hashlib.sha256, hash_function_nodes=None):
        self.model = MerkleTree(data, hash_function_leaves, hash_function_nodes) 
        self.viewModel = NodeViewModel(self.model.root)

    def animate_verification(self, data_index, scene):
        return self.viewModel.animate_verification(data_index, scene)

    def draw_verification(self, data_index, scene):
        return self.viewModel.draw_verification(data_index, scene)

    def complete_drawing(self):
        return self.viewModel.complete_drawing()
        

class NodeViewModel:
    def __init__(self, model, stand_alone=False):
        self.circle = manim.Circle(radius=0.5, color=manim.BLUE, stroke_width=2.5, z_index=-1).set_fill(manim.BLACK, opacity=1)
        self.name = manim.MarkupText(model.name, z_index=1, font_size=0.5*20)
        self.exp = manim.MarkupText(model.display, z_index=1, font_size=0.5*20)
        self.value = manim.MarkupText(model.value[0:6], z_index=1, font_size=0.5*20)

        self.exp.move_to(self.circle.get_center())
        self.name.next_to(self.exp, manim.UP / 2)
        self.value.next_to(self.exp, manim.DOWN / 2)

        self.root_view = manim.Group(self.circle, self.name, self.exp, self.value)
        self.model = model
        
        self.left = not stand_alone and model.left and NodeViewModel(model.left)
        self.right = not stand_alone and model.right and NodeViewModel(model.right)

        self.drawing = not stand_alone and self._draw()

    def _draw(self):
        
        if (self.model.left and self.model.right):
            l = self.left.drawing
            r = self.right.drawing
            l.next_to(r, manim.LEFT)
            aux_point = manim.Line(l.get_top(), r.get_top()).get_center()
            self.root_view.move_to(aux_point)
            self.root_view.shift(manim.UP)
            
            g = manim.Group(
                self.root_view, l, r
            )
        else:  # Leaf
            g = self.root_view

        return g

    def complete_drawing(self):
        if (self.model.left == None and self.model.right == None): # Leaf
            return self.root_view
        ll = create_connecting_line(self.root_view, self.left.root_view)
        lr = create_connecting_line(self.root_view, self.right.root_view)
        return manim.Group(self.root_view, ll, lr, self.right.complete_drawing(), self.left.complete_drawing()) 

    def __merge_layers(self, layers_left, layers_right):
        return [ layer_left + layer_right for (layer_left, layer_right) in zip(layers_left, layers_right)]

    def get_layered_nodes_and_lines(self):
        if (self.left == None and self.right == None ):
            return [[self]], []
        left_nodes, left_lines = self.left.get_layered_nodes_and_lines()
        right_nodes, right_lines = self.right.get_layered_nodes_and_lines()
        nodes = self.__merge_layers(left_nodes, right_nodes) + [[self]]
        lines = self.__merge_layers(left_lines, right_lines) + [[create_connecting_line(self.left.root_view, self.root_view), create_connecting_line(self.right.root_view, self.root_view, )]]
        return nodes, lines

    def animate_change_path_color(self, path):
        
        if not self.left or not self.right:
            return [], [self.animate_paint_root(manim.GREEN)]

        next_node = self.left if path[0] == 0 else self.right
        proof_node = self.right if path[0] == 0 else self.left

        proof_nodes_animations, main_path_animations = next_node.animate_change_path_color(path[1:]) 
        return proof_nodes_animations + [proof_node.animate_paint_root(manim.ORANGE)], main_path_animations + [self.animate_paint_root(manim.GREEN)]

    def __create_stand_alone_copy(self):

        copy = NodeViewModel(self.model, True)

        copy.circle = self.circle.copy()

        copy.circle.set_z_index(10)
        copy.name = self.name.copy()
        copy.name.set_z_index(11)
        copy.exp = self.exp.copy()
        copy.exp.set_z_index(11)
        copy.value = self.value.copy()
        copy.value.set_z_index(11)
        copy.root_view = manim.Group(copy.circle, copy.name, copy.exp, copy.value)
        return copy

    def animated_copy_and_move_proof_nodes(self, path, static_tree):

        if not self.left or not self.right:
            return [self], [], []

        next_node = self.left if path[0] == 0 else self.right
        proof_node = self.right if path[0] == 0 else self.left
        
        proof_node_copy = proof_node.__create_stand_alone_copy()
        main_path_nodes, proof_nodes, animations = next_node.animated_copy_and_move_proof_nodes(path[1:], static_tree) 

        return [self] + main_path_nodes, [proof_node_copy] + proof_nodes, [proof_node_copy.root_view.animate.align_to(static_tree, manim.LEFT).shift(manim.LEFT)] + animations

    def animated_generate_main_path(self, main_path_nodes, proof_nodes, scene):

        init_node_vm = main_path_nodes[0].__create_stand_alone_copy()
        init_node_vm.root_view.next_to(proof_nodes[0].root_view, manim.LEFT * 2)

        animations = []
        standard_distance = proof_nodes[1].root_view.get_center() - proof_nodes[0].root_view.get_center()
        generated_path = [init_node_vm]
        lines = []
        for i, main_path_node in enumerate(main_path_nodes[1:]):
            

            proof_node_copy = proof_nodes[i].circle.copy()
            proof_node_copy.set_z_index(3)
            generated_path_copy = generated_path[-1].circle.copy()
            generated_path_copy.set_z_index(3)

            appearance = manim.AnimationGroup(
                manim.FadeIn(generated_path[-1].root_view),
                manim.FadeIn(generated_path_copy),
                manim.FadeIn(proof_node_copy),
            )

            nvm = main_path_node.__create_stand_alone_copy()
            
            nvm.root_view.move_to(generated_path[-1].root_view)
            nvm.root_view.shift(standard_distance)

            line_main_path = create_connecting_line(generated_path[-1].root_view, nvm.root_view)
            line_proof_path = create_connecting_line(proof_nodes[i].root_view, nvm.root_view)
            
            scene.play(appearance)
            scene.wait()
            scene.play(
                manim.GrowFromPoint(line_proof_path, line_proof_path.start),
                manim.GrowFromPoint(line_main_path, line_main_path.start),
                manim.MoveAlongPath(generated_path_copy, line_main_path.copy()),
                manim.MoveAlongPath(proof_node_copy, line_proof_path.copy())
            )
            generated_path.append(nvm)
        
        scene.play(manim.FadeIn(generated_path[-1].root_view))


        return generated_path[-1].root_view

    
    def animated_compare_roots(self, root, verification_root, scene):
        aux_point = manim.Dot(manim.Line(root.get_center(), verification_root.get_center()).get_center())
        l = create_connecting_line(root, aux_point)
        lv =create_connecting_line(verification_root, aux_point)

        scene.play(
                manim.GrowFromPoint(l, l.start),
                manim.GrowFromPoint(lv, lv.start)
        )
        scene.wait()

        scene.play(
            manim.FadeIn(manim.Text("OK", stroke_width=3).scale(1/2).move_to(aux_point)),
            lag_ratio=1
        )
        scene.wait()
        
    def animate_verification(self, data_index, scene):
        drawing = self.complete_drawing()

        scene.add(drawing)
        resize_factor = max(drawing.height / 4, drawing.width / (4*16/9))
        drawing.center().scale(1/resize_factor)
        
        path = [int(d) for d in str(bin(data_index))[2:].zfill(self.model.layers - 1)]

        partial_proof_nodes_animations, main_path_animations = self.animate_change_path_color(path)

        scene.play(manim.AnimationGroup(*main_path_animations, lag_ratio=0.5))
        scene.wait()
        scene.play(manim.AnimationGroup(*partial_proof_nodes_animations, lag_ratio=0.5))
        scene.wait()
        main_path_nodes, proof_nodes, animations = self.animated_copy_and_move_proof_nodes(path, drawing)
        proof_nodes.reverse()
        animations.reverse()
        main_path_nodes.reverse()
        scene.play(manim.AnimationGroup(*animations, lag_ratio=0.1))
        scene.wait()
        root_verification = self.animated_generate_main_path(main_path_nodes, proof_nodes, scene)
        self.animated_compare_roots(self.root_view, root_verification, scene)


    # if path and data are None, the real one will be used, the verification will succeed
    def draw_verification(self, data_index, scene, data=None, path=None): 
        static_tree = self.complete_drawing()

        path = [int(d) for d in str(bin(data_index))[2:].zfill(self.model.layers - 1)]
        
        proof_nodes = self.paint_path_and_copy(path)
        proof_nodes.reverse()
        for node in proof_nodes:
            node.root_view.align_to(static_tree, manim.LEFT)
            node.root_view.shift(manim.LEFT * 3 / 2)
            node.circle.set_color(color=manim.ORANGE).set_fill(color=manim.BLACK, opacity=1)
        group_proof_nodes = manim.Group(*[p.root_view for p in proof_nodes])
        
        init_node = LeafNode(self.model.hash_function_leaves, self.model.data[data_index], None, None, complete_name="D<sub>0</sub>")
        init_node_vm = NodeViewModel(init_node, True) 

        init_node_vm.root_view.next_to(proof_nodes[0].root_view, manim.LEFT * 2)
        init_node_vm.circle.set_color(color=manim.GREEN).set_fill(color=manim.BLACK, opacity=1)
        

        standard_distance = proof_nodes[1].root_view.get_center() - proof_nodes[0].root_view.get_center()
        generated_path = [init_node_vm]
        lines = []
        for i, proof_node in enumerate(proof_nodes):
            inode = IntermediaryNode(None, None, None, self.model.hash_function_leaves, self.model.hash_function_nodes, left=generated_path[-1].model, right=proof_node.model, complete_name="D<sub>{}</sub>".format(i + 1))
            nvm = NodeViewModel(inode, True)
            nvm.circle.set_color(color=manim.GREEN).set_fill(color=manim.BLACK, opacity=1)
            nvm.root_view.move_to(generated_path[-1].root_view)
            nvm.root_view.shift(standard_distance)
            lines.append(create_connecting_line(nvm.root_view, generated_path[-1].root_view))
            lines.append(create_connecting_line(nvm.root_view, proof_nodes[i].root_view))
            generated_path.append(nvm)
             
        return manim.Group(static_tree, group_proof_nodes, *[p.root_view for p in generated_path], *lines)

    def animate(self):
        drawing = self.drawing
        resize_factor = max(drawing.height / 7.5, drawing.width / (7.5*16/9))
        drawing.center().scale(1/resize_factor)
        
        layered_nodes, layered_lines = self.get_layered_nodes_and_lines()
        
        animations = []

        appear_nodes = manim.FadeIn(manim.Group(*[n.root_view for n in layered_nodes[0]]))
        copies_previous_nodes = [manim.Circle(radius=0.5, color=manim.BLUE, stroke_width=2.5,z_index=-5).set_fill(manim.BLACK, opacity=1).scale(1/resize_factor).move_to(n.root_view.get_center()) for n in layered_nodes[0]]

        animations.append(manim.AnimationGroup(*([appear_nodes] + [manim.FadeIn(manim.Group(*[copy for copy in copies_previous_nodes]))])))

        for (nodes, lines) in zip(layered_nodes[1:], layered_lines):


            animations_lines = [manim.GrowFromPoint(line, line.start) for line in lines]
            move_previous_copies = [manim.MoveAlongPath(copy, line) for (copy, line) in zip(copies_previous_nodes, lines)]


            copies_previous_nodes = [manim.Circle(radius=0.5, color=manim.BLUE, stroke_width=2.5,z_index=-5).set_fill(manim.BLACK, opacity=1).scale(1/resize_factor).move_to(n.root_view.get_center()) for n in nodes]
            appear_nodes = [manim.FadeIn(manim.Group(*[n.root_view for n in nodes]))]
            appear_copies = [manim.FadeIn(manim.Group(*[copy for copy in copies_previous_nodes]))]


            animations.append(manim.AnimationGroup(
                manim.AnimationGroup(*(animations_lines + move_previous_copies)),
                manim.AnimationGroup(*(appear_nodes + appear_copies)),
                lag_ratio=1))

        return manim.AnimationGroup(animations, lag_ratio=1.5)

    def paint_root(self, color):
        self.circle.set_color(color=color).set_fill(color=manim.BLACK, opacity=1)

    def animate_paint_root(self, color):
        return self.circle.animate.set_color(color=color).set_fill(color=manim.DARK_GREY, opacity=1).set_stroke_width(4)

    def paint_path_and_copy(self, path):

        self.paint_root(manim.GREEN)

        if not self.left or not self.right:
            return []

        next_node = self.left if path[0] == 0 else self.right
        proof_node = self.right if path[0] == 0 else self.left
        
        proof_node_copy = NodeViewModel(proof_node.model, True)

        proof_node_copy.circle = proof_node.circle.copy()
        proof_node_copy.name = proof_node.name.copy()
        proof_node_copy.exp = proof_node.exp.copy()
        proof_node_copy.value = proof_node.value.copy()
        proof_node_copy.root_view = manim.Group(proof_node_copy.circle, proof_node_copy.name, proof_node_copy.exp, proof_node_copy.value)

        proof_node.paint_root(manim.ORANGE)
        
        partial_proof_nodes = next_node.paint_path_and_copy(path[1:]) 
        return [proof_node_copy] + partial_proof_nodes
    
    def get_node(self, path):
        if len(path) == 0:
            return self

        next_node = self.left if path[0] == 0 else self.right
        return next_node.get_node(path[1:])


def drawMerkleTree(data, scene):
    m = MerkleTreeViewModel(data)
    d = m.complete_drawing()
    resize_factor = max(d.height / 8, d.width / (8*16/9))
    d.center().scale(1/resize_factor)
    scene.add(d)


class DrawSmallMerkleTree(manim.Scene):
    def construct(self):
        drawMerkleTree(["1", "2"], self)
    
class DrawMediumMerkleTree(manim.Scene):
    def construct(self):
        drawMerkleTree(["1", "2", "3", "4"], self)


class DrawBigMerkleTree(manim.Scene):
    def construct(self):
        drawMerkleTree(["1", "2", "3", "4", "5", "6", "7", "8"], self)

class AnimateMerkleTree(manim.Scene):
    def construct(self):
        n = MerkleTreeViewModel(["1","2","3","4","5","6","7","8"]).viewModel
        complete_animation = n.animate()
        
        self.play(complete_animation)
        self.wait()


class DrawVerifiaction(manim.Scene):
    def construct(self):
        merkle_tree_vm = MerkleTreeViewModel(["1","2","3","4","5","6","7","8"])
        complete_drawing = merkle_tree_vm.draw_verification(3, self)
        resize_factor = max(complete_drawing.height / 6, complete_drawing.width / (6*16/9))
        complete_drawing.center().scale(1/resize_factor)
        self.add(complete_drawing)


class AnimateVerification(manim.Scene):
    def construct(self):
        merkle_tree_vm = MerkleTreeViewModel(["1","2","3","4","5","6","7","8"])
        merkle_tree_vm.animate_verification(3, self)
