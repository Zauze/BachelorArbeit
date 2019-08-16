from numpy import *
import numpy as numpy
import re
import sys
import copy
import logging
from copy import deepcopy


def number_of_words(text):
    """
    Returns number of words from text
    :param str text:
    :return: int
    """
    return len(re.findall('[^\s]+', text))


def lcs(text1, text2, sequence = ''):
    """
    Longest common subsequence algorithm
    :param str text1:
    :param str text2:
    :param str sequence: previously found longest sequence
    :return: str : longest common subsequence
    """
    check = ''
    for i in range(len(text1)):
        check += text1[i]
        if check in text2:
            if len(check) > len(sequence):
                sequence = check
        else:
            break
    if len(sequence) > len(text1) - 1:
        return sequence
    else:
        return lcs(text1[1:len(text1)], text2, sequence)


def content_similarity(node1, node2):
    """
    Calculates the content similarity value of node1 and node2
    :param HTLMNode node1:
    :param HTMLNode node2:
    :return: float
    """
    if not node1.is_leaf() or not node2.is_leaf():
        return 0
    else:
        cs = lcs(node1.text, node2.text)
        w = number_of_words(cs)
        m = max(
            number_of_words(node1.text),
            number_of_words(node2.text)
        )
        return 1.0 if w == m else float(w)/float(m)


def estm(node1, node2):
    """
    Performs the enhanced simple tree matching algorithm
    on node1 and node2
    :param HTMLNode node1:
    :param HTMLNode node2:
    :return: int : the computed score
    """

    if node1.type != node2.type:
        return 0
    if 'class' in node1.attributes and 'class' in node2.attributes:
        if node1.attributes['class'] != node2.attributes['class']:
            return 0
    m = len(node1.get_children())
    n = len(node2.get_children())
    # To avoid redundant computations
    if 'm_matrices' in node1.data_container and node2.identification in node1.data_container['m_matrices']:
        matrix = node1.data_container['m_matrices'][node2.identification]
    else:
        matrix = numpy.zeros((m + 1,n + 1))
        wmatrix = numpy.zeros((m,n))

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                wmatrix[i-1][j-1] = estm(node1.get_children()[i-1], node2.get_children()[j-1])
                matrix[i][j] = max(
                    matrix[i, j-1],
                    matrix[i-1][j],
                    matrix[i-1][j-1] + 1 + estm(node1.get_children()[i-1], node2.get_children()[j-1]))

        if 'weight_matrices' not in node1.data_container:
            node1.data_container['weight_matrices'] = {}

        if 'm_matrices' not in node1.data_container:
            node1.data_container['m_matrices'] = {}

        node1.data_container['weight_matrices'][node2.identification] = wmatrix
        node1.data_container['m_matrices'][node2.identification] = matrix

    return matrix[m][n] + 1 + content_similarity(node1, node2)


def tree_alignment(tree1, tree2, calculate_estm = False):
    """
    Computes the intersection of two trees
    :param HTMLNode tree1:
    :param HTMLNode tree2:
    :param bool calculate_estm: Calculates the score for enhanced simple
                                tree matching algorithm if set to True
    :return: HTMLNode : the aligned tree
    """
    tree1 = copy.copy(tree1)
    tree2 = copy.copy(tree2)
    if tree1.type != tree2.type:
        return None
    if 'class' in tree1.attributes and 'class' in tree2.attributes:
        if tree1.attributes['class'] != tree2.attributes['class']:
            return None
    if len(tree1.get_children()) == 0 and len(tree2.get_children()) == 0:
        return tree1
    if len(tree1.get_children()) == 0 or len(tree2.get_children()) == 0:
        tree1.parent = None
        tree1.children = []
        tree1.text = ''
        return tree1

    m = len(tree1.get_children())
    n = len(tree2.get_children())

    if 'weight_matrices' in tree1.data_container \
            and tree2.identification in tree1.data_container['weight_matrices'] \
            and not calculate_estm:
        wmatrix = tree1.data_container['weight_matrices'][tree2.identification]
    else:
        estm(tree1, tree2)
        wmatrix = tree1.data_container['weight_matrices'][tree2.identification]

    max_indices = list()
    if m < n:
        indices = numpy.argmax(wmatrix, axis=0)
        for i in range(m):
            max_indices.append((i, indices[i]))
    else:
        indices = numpy.argmax(wmatrix, axis=1)
        for i in range(n):
            max_indices.append((indices[i], i))

    children = []
    for t in max_indices:
        x = t[0]
        y = t[1]
        if wmatrix[x][y] == 0:
            continue
        if m < n:
            alignment = tree_alignment(tree1.get_children()[x], tree2.get_children()[y])
        else:
            alignment = tree_alignment(tree1.get_children()[y], tree2.get_children()[x])

        if alignment is not None:
            children.append(alignment)
    # Adding text nodes if included in the other tree
    if number_of_words(tree1.get_pure_text()) > number_of_words(tree2.get_pure_text()):
        tmp = tree1.children
    else:
        tmp = tree2.children
    for child in tmp:
        if isinstance(child, str):
            children.append(child)
    tree1.children = children
    return tree1


def terminal(tree, count_pictures=True):
    """
    Counts terminals (text nodes) of the subtree which root is param tree
    :param HTMLNode tree: root
    :param bool count_pictures: If True counts pictures as terminals
    :return: int : amount of terminals
    """
    count = 0
    if count_pictures and tree.type == 'picture' or tree.type == 'img':
        count += 1
    if tree.has_text() is not None and len(tree.text) > 0:
        for child in tree.children:
            if isinstance(child, str):
                count += 1
                break
    for child in tree.get_children():
        count += terminal(child)
    return count


def normalized_tree_distance(tree1, tree2, artificial_root=False):
    """
    Calculating the normalized tree distance of tree1 and tree2
    :param HTMLNode tree1:
    :param HTMLNode tree2:
    :param bool artificial_root: if True, the root of tree1 and tree2 will be
                                 considered as artifical_node -that means it was
                                 created extra to bind its children
                                 will be ignored in calculation
    :return: float : the normalized value
    """
    tree1.update()
    tree2.update()
    aligned_tree = tree_alignment(tree1, tree2)
    if artificial_root:
        if aligned_tree.is_leaf():
            return 1.0
    aligned_tree.compute_text()
    matched = terminal(aligned_tree)
    max_val = max(terminal(tree1), terminal(tree2))

    # TODO: what if matched = 0 and max_val = 0 although aligned tree is not only the artifical?
    if max_val == 0:
        return 1.0
    return 1.0 - (float(matched)/float(max_val))
