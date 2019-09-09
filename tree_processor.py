from numpy import *
import numpy as numpy
import re
import sys
import copy
import logging
import datetime
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
    :return: str : longest common sub sequence
    """
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
    """
    for start in range(len(text1)):
        check = ''
        for i in range(start, len(text1)):
            check += text1[i]
            if check in text2:
                if len(check) > len(sequence):
                    sequence = check
            else:
                break
        if len(sequence) > (len(text1) - start):
            return sequence
    return sequence


def content_similarity(node1, node2):
    """
    Calculates the content similarity value of node1 and node2
    :param HTLMNode node1:
    :param HTMLNode node2:
    :return: float
    """
    if not node1.is_leaf() or not node2.is_leaf():
        return 0.0
    else:
        cs = lcs(node1.get_pure_text(), node2.get_pure_text())
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
                    matrix[i-1, j],
                    matrix[i-1, j-1] + 1 + estm(node1.get_children()[i-1], node2.get_children()[j-1]))

        if 'weight_matrices' not in node1.data_container:
            node1.data_container['weight_matrices'] = {}

        if 'm_matrices' not in node1.data_container:
            node1.data_container['m_matrices'] = {}

        node1.data_container['weight_matrices'][node2.identification] = wmatrix
        node1.data_container['m_matrices'][node2.identification] = matrix

    return matrix[m][n] + 1 + content_similarity(node1, node2)


def get_max_string(tree1, tree2):
    if number_of_words(tree1.get_pure_text()) > number_of_words(tree2.get_pure_text()):
        tmp = tree1.children
    else:
        tmp = tree2.children
    ret = []
    for child in tmp:
        if isinstance(child, str):
            ret.append(child)
    return ret


def create_matched_tree(tree_one, tree_two, calculate_estm = False, string_function=get_max_string):
    """
    Computes the intersection of two trees
    :param HTMLNode tree_one:
    :param HTMLNode tree_two:
    :param bool calculate_estm: Calculates the score for enhanced simple
                                tree matching algorithm if set to True
    :return: HTMLNode : the aligned tree
    """
    tree1 = copy.copy(tree_one)
    tree2 = copy.copy(tree_two)
    if tree1.type != tree2.type:
        return None
    if 'class' in tree1.attributes and 'class' in tree2.attributes:
        if tree1.attributes['class'] != tree2.attributes['class']:
            return None
    if ('class' not in tree1.attributes and 'class' in tree2.attributes) \
        or ('class' in tree1.attributes and 'class' not in tree2.attributes):
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

    # Gets the alignment instructions
    alignments = assign_alignment(tree1.get_children(), tree2.get_children(), wmatrix)

    children = []
    for pair in alignments:
        # Performs alignments
        alignment = create_matched_tree(pair[0], pair[1])
        if alignment is not None:
            children.append(alignment)
    # Aligns strings using the specific string alignment function provided
    str_list = string_function(tree1, tree2)
    tree1.children = children + str_list
    return tree1


def assign_alignment(children1, children2, wmatrix):
    """
    Assigns the best match of children nodes from one tree to
    the children nodes from another tree. Uses the before calculated
    wmatrix and performs the match recursively.
    :param list of HTMLNode children1: the children nodes from the first tree
    :param list of HTMLNode children2: the children nodes from the second tree
    :param array wmatrix:
    :return: list of tuple : the alignment instructions
    """
    alignments = []
    max_indices = list()
    m = len(children1)
    n = len(children2)
    # Firstly, getting the coordinates of the maximum
    # numbers in the wmatrix.
    # To find the best choices of children,
    # the algorithm will be oriented on the tree with lesser children
    # else if both children size is equal, the tree is regarded main, which
    # has a higher count of maximum coordinates
    if m < n:
        indices = numpy.argmax(wmatrix, axis=1)
        for i in range(m):
            max_indices.append((indices[i], i, wmatrix[i][indices[i]]))
    elif m == n:
        tmp_y = numpy.argmax(wmatrix, axis=1)
        ind_y = []
        y = 0
        for x in tmp_y:
            ind_y.append((x, y, wmatrix[y][x]))
            y += 1
        score_y = 0
        for i in ind_y:
            score_y += wmatrix[i[1]][i[0]]
        tmp_x = numpy.argmax(wmatrix, axis=0)
        ind_x = []
        x = 0
        for y in tmp_x:
            ind_x.append((x, y, wmatrix[y][x]))
            x += 1
        score_x = 0
        for i in ind_x:
            score_x += wmatrix[i[1]][i[0]]

        if score_y > score_x:
            max_indices = ind_y
        else:
            max_indices = ind_x
    else:
        indices = numpy.argmax(wmatrix, axis=0)
        for i in range(n):
            max_indices.append((i, indices[i], wmatrix[indices[i]][i]))
    # Getting a list of all values from the maximum coordinates
    value_list = list(map(lambda x: x[2], max_indices))
    # Getting the highest value of all max values
    index = value_list.index(max(value_list))
    tup = max_indices[index]
    # append the alignment instruction to the list
    alignments.append((children1[tup[1]], children2[tup[0]]))
    # The two children won't be considered anymore since,
    # it can be that multiple children maximally match to one children
    # from the other tree
    children1.remove(children1[tup[1]])
    children2.remove(children2[tup[0]])
    # Deleting the row and column from the wmatrix
    if len(value_list) > 1:
        wmatrix = numpy.delete(wmatrix, tup[0], 1)
        wmatrix = numpy.delete(wmatrix, tup[1], 0)
        # Running the algorithm recursively
        alignments += assign_alignment(children1, children2, wmatrix)
    return alignments


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
    if tree.has_text() is not None and re.search('\w+', tree.get_pure_text()) is not None:
        for child in tree.children:
            if isinstance(child, str):
                count += 1
                break
    for child in tree.get_children():
        count += terminal(child)
    return count


def tree_structure_points(node, n=0):
    """
    A self developed structure analysis algorithm.
    Returns the subtree score of a given root
    :param HTMLNode node:
    :param int n: the exponent
    :return: float
    """
    # Those are tags will not be counted
    ignore_tags = [
        'p',
        'strong',
        'abbr',
        'b',
        'i',
        'em',
        'mark',
        'small',
        'del',
        'ins',
        'sub',
        'sup',
        'img'
    ]

    score = 0.0
    if node.type not in ignore_tags:
        score += 2**n
        n -= 1

    for child in node.get_children():
        score += tree_structure_points(child, n)

    return score


def modified_norm_tree_dist(tree1, tree2, artificial_root=False):
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
    aligned_tree = create_matched_tree(tree1, tree2)
    if artificial_root:
        if aligned_tree.is_leaf():
            return 1.0
    aligned_tree.compute_text()
    # Computing scores for aligned tree and the two given trees
    aligned_score = tree_structure_points(aligned_tree, 1) - 2
    max_score = max(tree_structure_points(tree1, 1) - 2, tree_structure_points(tree2, 1) - 2)
    if max_score == 0:
        structure_val = 1.0
    else:
        structure_val = 1.0 - (aligned_score/max_score)
    return structure_val

