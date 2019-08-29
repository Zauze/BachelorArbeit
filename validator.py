import enhanced_simple_tree_matching as estm
import validators.data_validator
from constants import *
"""
Module for noise detection and removal
"""


def validate_data_region(data_region_node):
    """
    Function validates data regions in their depth,
    removes noise
    :param HTMLNode data_region_node: the root of the region to analyse
    :return: bool
    """
    # Validating depth
    data_region_node.calculate_depth()
    if data_region_node.depth <= MIN_REGION_DEPTH or data_region_node.depth >= MAX_REGION_DEPTH:
        return False

    # Validating ids, classes and tags
    # Returning None if the current data region node is marked as noise
    if validators.data_validator.DataValidator.in_class_ids(data_region_node, NOISE_IDS_CLASSES):
        return False

    # Processing the children for noisy ids and classes
    for id_class in NOISE_IDS_CLASSES:
        data_region_node.remove_id(id_class)
        data_region_node.remove_class(id_class)

    # Information count check
    information_counts = []
    for child in data_region_node.get_children():
        information_counts.append(estm.terminal(child, False))
    if max(information_counts) < MIN_INFORMATION_COUNT:
        return False

    return True


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

