
from ..utils import load_entry_point, Configurable

ENTRYPOINT_GROUP_NAME = 'pydoc_markdown.preprocessors'


class Preprocessor(Configurable):

    options = []

    def preprocess_tree(self, root):
        root.visit(lambda x: self.preprocess(root, x))

    def preprocess(self, root, node):
        raise NotImplementedError


def load_preprocessor(name):
    return load_entry_point(ENTRYPOINT_GROUP_NAME, name).load()
