import hashlib
import manim
from merkle_tree_model import MerkleTree


def create_connecting_line(object_1, object_2):
    return manim.Line(
                object_1.get_center(), 
                object_2.get_center(),
                stroke_width=0.5*3,
                z_index=-10
            )

class MerkleTreeViewModel:
    def __init__(self, data, hash_function_leaves=hashlib.sha256, hash_function_nodes=None):
        self.model = MerkleTree(data, hash_function_leaves, hash_function_nodes) 
        self.viewModel = NodeViewModel(self.model.root)

    # if path and data are None, the real one will be used, the verification will succeed
    def animated_verification(self, data_index, scene, data=None, path=None): 
        static_tree = self.viewModel.drawing

        path = [int(d) for d in str(bin(data_index))[2:].zfill(self.model.root.layers)]
        
        proof_nodes = self.viewModel.paint_path_and_copy(path)
        group_proof_nodes = manim.Group(*[p.root_view for p in proof_nodes])
        print(len(group_proof_nodes))
        proof_nodes.reverse()
        for node in proof_nodes:
            node.root_view.align_to(static_tree, manim.LEFT)
            node.root_view.shift(manim.LEFT * 3 / 2)
        
        init_node = LeafNode(self.model.hash_function_leaves, self.model.data[data_index], "D<sub>0</sub>")
        init_node_vm = NodeViewModel(init_node, True) 
        
        init_node_vm.root_view.next_to(proof_nodes[0].root_view, manim.LEFT * 2)

        standard_distance = proof_nodes[1].root_view.get_center() - proof_nodes[0].root_view.get_center()
        current_hash_value = init_node_vm.value
        generated_path = [init_node_vm]
        lines = []
        for i, proof_node in enumerate(proof_nodes):
            inode = IntermediaryNode(self.model.hash_function_nodes, "D<sub>{}</sub>".format(i + 1), lambda x: 1, generated_path[-1].model, proof_node.model)
            nvm = NodeViewModel(inode, True)
            nvm.root_view.move_to(generated_path[-1].root_view)
            nvm.root_view.shift(standard_distance)
            lines.append(create_connecting_line(nvm.root_view, generated_path[-1].root_view))
            lines.append(create_connecting_line(nvm.root_view, proof_nodes[i].root_view))
            generated_path.append(nvm)
             
        # for node in proof_nodes:
        #     node.next_to(static_tree, manim.DL)
        
        # for (i, node) in enumerate(proof_nodes):
        #     node.shift(manim.UP * (i + 1))

        return manim.Group(static_tree, group_proof_nodes, *[p.root_view for p in generated_path], *lines)

    def complete_drawing(self):
        return self.viewModel.complete_drawing()
        

class NodeViewModel:
    def __init__(self, model, stand_alone=False):
        self.circle = manim.Circle(radius=0.5, color=manim.BLUE, stroke_width=0.5*3).set_fill(manim.BLACK, opacity=1)
        self.name = manim.MarkupText(model.name, font_size=0.5*20)
        self.exp = manim.MarkupText(model.display, font_size=0.5*20)
        self.value = manim.MarkupText(model.value[0:6], font_size=0.5*20)

        self.exp.move_to(self.circle.get_center())
        self.name.next_to(self.exp, manim.UP / 2)
        self.value.next_to(self.exp, manim.DOWN / 2)

        self.root_view = manim.Group(self.circle, self.name, self.exp, self.value)
        self.model = model
        
        self.left = not stand_alone and model.left and NodeViewModel(model.left)
        self.right = not stand_alone and model.right and NodeViewModel(model.right)

        self.drawing = self._draw()

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



    def animate(self):
        drawing = self.drawing
        resize_factor = max(drawing.height / 8, drawing.width / (8*16/9))
        drawing.center().scale(1/resize_factor)
        
        layered_nodes, layered_lines = self.get_layered_nodes_and_lines()
        
        animations = []
        for (nodes, lines) in zip(layered_nodes[:-1], layered_lines):

            appear_nodes = manim.FadeIn(manim.Group(*[n.root_view for n in nodes]))
            animations.append(appear_nodes)
            
            copies = [n.root_view.copy() for n in nodes]

            appear_copies = manim.FadeIn(manim.Group(*[copy for copy in copies]), run_time=0.001)
            animations.append(appear_copies)
            # animations.append(manim.Wait())

            animations_lines = [manim.GrowFromPoint(line, line.start) for line in lines]
            move_copies = [manim.MoveAlongPath(copy, line) for (copy, line) in zip(copies, lines)]
            # fade_out_copies = [manim.FadeOut(copy) for copy in copies]

            animations.append(manim.AnimationGroup(*( animations_lines + move_copies )))

        animations.append(manim.FadeIn( layered_nodes[-1][0].root_view)) # root
        # layered_copies = [[n.root_view.copy() for n in layer] for layer in layered_nodes]

        # appear_copies = [manim.FadeIn(manim.Group(*[copy for copy in layer])) for layer in layered_copies]
        # move_copies = [manim.MoveAlongPath(manim.Group(*[copy for copy in layer])) for layer in layered_copies]
        # animations_nodes = [manim.FadeIn(manim.Group(*[n.root_view for n in layer])) for layer in layered_nodes]
        # animations_lines = [manim.FadeIn(manim.Group(*[line for line in layer])) for layer in layered_lines]
        # animations = [val for pair in zip(animations_nodes[:-1], animations_lines, appear_copies, move_copies, remove_copies[:-1]) for val in pair] + [animations_nodes[-1]]

        return manim.AnimationGroup(animations, lag_ratio=1.1)

    def paint_root(self, color):
        self.circle.set_fill(color=color)

    def paint_path_and_copy(self, path):

        self.paint_root(manim.ORANGE)

        if not self.left or not self.right:
            return []

        next_node = self.left if path[0] == 0 else self.right
        proof_node = self.right if path[0] == 0 else self.left
        
        proof_node_copy = NodeViewModel(proof_node.model, True)

        proof_node_copy.root_view = proof_node.root_view.copy()

        proof_node.paint_root(manim.GREEN)
        
        partial_proof_nodes = next_node.paint_path_and_copy(path[1:]) 
        return [proof_node_copy] + partial_proof_nodes



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
        n = MerkleTreeViewModel(["1","2","3","4","1","2","3","4"]).viewModel
        complete_animation = n.animate()
        
        self.play(complete_animation)
        self.wait()


class AnimateVerifiaction(manim.Scene):
    def construct(self):
        merkle_tree_vm = MerkleTreeViewModel(["1","2","3","4","5","6","7","8"])
        complete_drawing = merkle_tree_vm.animated_verification(3, self)
        resize_factor = max(complete_drawing.height / 6, complete_drawing.width / (6*16/9))
        complete_drawing.center().scale(1/resize_factor)
        self.add(complete_drawing)
