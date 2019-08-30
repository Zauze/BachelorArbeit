from constants import *
"""
Module for preprocessing and initial noise removal
"""


def remove_noise_dp(detailed_page):
    """
    Removes noise from detailed pages
    :param HTMLNode detailed_page: the root of the detailed page to process
    :return: None
    """
    # Removing noisy classes and ids
    for id_class in NOISE_IDS_CLASSES:
        detailed_page.remove_id(id_class)
        detailed_page.remove_class(id_class)


def preprocess(node):
    """
    Making an initial preprocess of a html node
    - Removing the highest level <head> tag (since containing only metas, scripts etc.)
    - Removing of irrelevant nodes
    :param HTMLNode node: the node to process
    :return: None
    """
    if isinstance(node, str) or node.is_leaf():
        return

    if node.type == 'html':
        delete = []
        for child in node.get_children():
            if child.type == 'head':
                delete.append(child)

        node.remove_children(delete)
    else:
        remove = []
        for child in node.get_children():
            if child.type in NOISE_TAGS:
                remove.append(child)

        node.remove_children(remove)

    for child in node.get_children():
        preprocess(child)
    node.update()