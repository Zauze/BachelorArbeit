import HTML_Tree


class Preprocessor:
    """
    This class pre-processes the extraction task
    by removing all the unnecessary tasks
    """
    @staticmethod
    def run(root):
        # TODO: enhance, move the removal of nodes here (instead of marking them as Noise) or
        #       remove this function completely
        """
        Runs validation and modifies the given tree
        :param root:
        :return: None
        """
        for child in root.get_children():
            if child.type == 'head':
                root.remove_children(child)

        for type in ['script', 'meta']:
            root.remove_type(type)
