
class Preprocessor(object):

    def preprocess_tree(self, root):
        root.visit(lambda x: self.preprocess(root, x))

    def preprocess(self, root, node):
        raise NotImplementedError
