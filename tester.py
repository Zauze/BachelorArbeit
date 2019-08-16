import HTML_Tree
import partial_tree_alignment as pta
from easyhtml import parser
from easyhtml import dom

class TestFailure(Exception):
    pass

def get_node_info(node):
    node_class = node.attributes['class'] if 'class' in node.attributes else None
    if isinstance(node_class, list):
        node_class = node_class[0]
    return node.type, node_class

def partial_tree_alignment_test():
    insert_into_test()

def insert_into_test():
    test1 = open('test1.html', 'r')
    test2 = open('test2.html', 'r')
    test3 = open('test4.html', 'r')
    test4 = open('test3.html', 'r')
    dom_parser = parser.DOMParser()
    dom_parser.feed(test1.read())
    document = dom_parser.get_dom()
    node1 = HTML_Tree.HTMLNode(document.elements[0], 0)
    dom_parser.feed(test2.read())
    document = dom_parser.get_dom()
    node2 = HTML_Tree.HTMLNode(document.elements[0], 0)
    dom_parser.feed(test3.read())
    document = dom_parser.get_dom()
    node3 = HTML_Tree.HTMLNode(document.elements[0], 0)
    dom_parser.feed(test4.read())
    document = dom_parser.get_dom()
    node4 = HTML_Tree.HTMLNode(document.elements[0], 0)

    aligned, rest = pta.partial_tree_alignment([node1, node2])
    if len(rest) > 0:
        raise TestFailure('No rest expected after alignment')
    else:
        print("Test passed")
    if aligned.get_children()[0].text != "This is a test\nThis is a test\n":
        raise TestFailure('Texts must have been merged after alignment')
    else:
        print("Test passed")
    if len(aligned.get_children()[1].get_children()) is not 8:
        raise TestFailure('Children must have been merged after alignment')
    else:
        print("Test passed")
    if aligned.get_children()[1].get_children()[6].text != "\n            Test\n        \n\n            Test\n        \n":
        raise TestFailure('No proper merge of children')
    else:
        print("Test passed")
    if aligned.get_children()[1].get_children()[7].text != "\n            Another test\n        \n":
        raise TestFailure('Child was not properly added')
    else:
        print("Test passed")
    aligned, rest = pta.partial_tree_alignment([aligned, node3, node4])
    if len(rest) > 0:
        raise TestFailure('A full alignment without rest was expected')
    else:
        print("Test passed")
    children_level_1 = list(map(get_node_info, aligned.get_children()))

    if children_level_1.sort() != [('p', None), ('div', None)].sort():
        raise TestFailure('Wrong merge of element level 1')
    else:
        print("Test passed")
    if aligned.get_children()[0].get_children()[0].type != 'strong':
        raise TestFailure('Extra children were not appended')
    else:
        print("Test passed")
    children_level_2 = list(map(get_node_info, aligned.get_children()[1].get_children()))
    if children_level_2.sort() != [
        ('div', 'ignore1'),
        ('div', 'ignore2'),
        ('div', 'ignore3'),
        ('div', 'ignore4'),
        ('div', 'ignore5'),
        ('div', 'ignore6'),
        ('div', 'this is there'),
        ('div', 'Matching after one pass'),
        ('div', 'In-between'),
        ('div', 'this not')
    ].sort():
        raise TestFailure('Wrong alignment of children level 2')
    else:
        print("Test passed")



partial_tree_alignment_test()