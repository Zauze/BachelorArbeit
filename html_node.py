from easyhtml import dom
import sys
import re
import numpy as np
from numpy import *
from copy import *
import functools
import easyhtml
import errors.errors


class HTMLNode:
    """
    Data structure to collect information from HTML nodes
    and additionally provide a data container to save operations
    done on this node (like distance calculations)
    """
    id = 0

    @staticmethod
    def identification():
        """
        Function to assign an identification number
        to each creates node, for simpler search and extraction
        :return: None
        """
        id_copy = HTMLNode.id
        HTMLNode.id += 1
        return id_copy

    def __init__(self, *args):
        """
        The normal initializing function, which provides
        multiple init options:
        1.) Allows to create a HTMLNode by hand using 4 arguments
            (type, attributes, text, level)
        2.) Create HTMLNode using the easyhtml data structure using 2 arguments
            (object, level)
        :param args:
        """
        self.parent = None
        self.children = []
        self.depth = 0
        self.type = None
        self.attributes = {}
        self.text = ''
        self.level = 0
        self.data_container = {}
        self.identification = HTMLNode.identification()
        if len(args) is 4:
            self.create_manual(*args)
        elif len(args) is 2:
            self.create_with_object(*args)

    def create_manual(self, type, attributes, text, level):
        self.type = type
        self.attributes = attributes or {}
        self.text = text or ''
        self.level = level

    def create_with_object(self, html_object, level):
        not_allowed_classes = [
            dom.HTMLComment
        ]

        self.text = html_object.inner_html
        # Sometimes non closing nodes are not recognized and just included as text
        self.text = re.sub('\<[a-z]+[^<>]*\>', '', self.text)
        self.type = html_object.tag_name
        self.attributes = html_object.attrs or {}
        self.level = level
        for el in html_object.elements:
            if type(el) not in not_allowed_classes:
                # Appending the string of simple text nodes
                # without creating a HTMLNode object
                if type(el) in [dom.PlainText, dom.TextNode]:
                    self.children.append(
                        str(el.raw_html).replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
                    )
                else:
                    if el.tag_name == 'br':
                        continue
                    child = HTMLNode(el, self.level + 1)
                    self.add_child(child)
        self.calculate_depth()

    def calculate_depth(self):
        """
        Calculates the maximum depth of the node
        :return: None
        """
        self.depth = 0
        for child in self.get_children():
            child.calculate_depth()
            if child.depth > self.depth - 1:
                self.depth = child.depth + 1

    def add_child(self, child):
        """
        Adds and adjusts parent of child
        :param HTMLNode child:
        :return: None
        """
        self.children.append(child)
        child.parent = self

    def get_children(self):
        """
        Returns all non-string object from children list
        :return: list
        """
        children = []
        for child in self.children:
            if isinstance(child, HTMLNode):
                children.append(child)
        return children

    def remove_children(self, children):
        """
        Removes elements from children list
        :param HTMLNode/list of HTMLNode children: objects to remove from children list
        :return: None
        """
        if isinstance(children, list):
            for child in children:
                self.children.remove(child)
        else:
            self.children.remove(children)

    def get_pure_text(self):
        pure_text = ""
        for child in self.children:
            if isinstance(child, str):
                pure_text += child
        return pure_text

    def truncate_children(self, start_index, end_index):
        """
        Returns a sublist of the children list, based on the
        indexes of children if all text nodes are removed
        :param int start_index: index of start HTMLNode in the list returned by function get_children()
        :param end_index: index of end HTMLNode in the list returned by function get_children()
        :return: list
        """
        start = self.children.index(self.get_children()[start_index])
        end = self.children.index(self.get_children()[end_index - 1])
        return self.children[start:end + 1]

    def is_root(self):
        """
        Returns whether node is root (no parent)
        :return: bool
        """
        return True if self.level is 0 else False

    def is_leaf(self):
        """
        Returns whether node is leaf (no HTMLNode children)
        :return: bool
        """
        return True if len(self.get_children()) is 0 else False

    def remove_type(self, type):
        """
        Removes nodes with specific types in the whole subtree
        of the current node
        :param str type: the type/tag to remove
        :return: None
        """
        remove_list = []
        for child in self.get_children():
            if child.type == type:
                remove_list.append(child)
        self.remove_children(remove_list)
        for child in self.get_children():
            child.remove_type(type)

    def remove_id(self, id):
        """
        Removes nodes with the given id, searches subtree,
        if current node has a different id
        :param int id: the oid to remove
        :return: None
        """
        remove_list = []
        for child in self.get_children():
            if 'id' in child.attributes and id in child.attributes['id']:
                remove_list.append(child)
        self.remove_children(remove_list)
        for child in self.get_children():
            child.remove_id(id)

    def remove_class(self, bad_class):
        """
        Removes nodes with the given class attribute, from the
        whole sub tree
        :param str bad_class: the class string
        :return: None
        """
        remove_list = []
        for child in self.get_children():
            if 'class' in child.attributes and bad_class in child.attributes['class']:
                remove_list.append(child)
        self.remove_children(remove_list)
        for child in self.get_children():
            child.remove_id(bad_class)

    def find_id(self, iden):
        """
        Finds and return node with the given id,
        else None when not found
        :param int iden:
        :return: HTMLNode
        """
        if self.identification == iden:
            return self
        for child in self.get_children():
            res = child.find_id(iden)
            if res is not None:
                return res
        return None

    def has_tag(self, tag):
        """
        Checks whether subtree contains
        a given tag
        :param str tag:
        :return: bool
        """
        if self.type == tag:
            return True
        else:
            for child in self.get_children():
                if child.has_tag(tag):
                    return True
        return False

    def has_text(self):
        """
        Returns whether node contains loose text
        :return: bool
        """
        for child in self.children:
            if isinstance(child, str):
                return True
        return False

    def get_element_count(self):
        """
        Return the amount of elements, contained
        in the subtree
        :return: int
        """
        count = 1
        for child in self.get_children():
            count += child.get_element_count()
        return count

    def compute_text(self, indentation =""):
        """
        Computes recursively the raw text for the given node, using
        indentation for better layout
        :param str indentation: str containing '\t' characters
        :return: None
        """
        if self.is_leaf():
            if self.text is None:
                self.text = ""
            self.text = self.text.strip()
            return None
        else:
            st = ""
            for child in self.children:
                if isinstance(child, str):
                    st += "%s%s" % (indentation, child.strip())
                    st += "\n"
                else:
                    attributes_str = ""
                    children_str = ""
                    for attr in child.attributes:
                        attributes_str += " %s=\"%s\"" % (str(attr), str(child.attributes[attr]))
                    child.compute_text(indentation + "\t")
                    children_str += child.text
                    st += ("%s<%s%s >\n" % (indentation, child.type, attributes_str)
                                + "\t%s%s\n" % (indentation, children_str.strip())
                                + "%s</%s>\n" % (indentation, child.type))
                self.text = st

    def find_nodes_with_depth(self, depth):
        """
        Searches recursively the sub tree for nodes with the given depth
        and returns them
        :param int depth:
        :return: list of HTMLNode
        """
        self.calculate_depth()
        if self.depth == depth:
            return [self]
        else:
            ret = []
            for child in self.get_children():
                ret += child.find_nodes_with_depth(depth)
        return ret

    def update(self):
        """
        Updates the flexible parameters of the node and the
        node's subtree
        :return: None
        """
        self.calculate_depth()
        self.compute_text()
        for child in self.get_children():
            child.parent = self
            child.update()

    def get_path(self, stop=None):
        """
        Function that retrieves the path from this node to the node with the ID stop.
        If stop not specified, the root node will be used, if stop not found, None will be
        returned
        :param stop: id of the wanted root (else as root will be regarded the
                     node which does not have a parent)
        :return: str or None
        """
        # Getting the class
        node_class = None
        if 'class' in self.attributes:
            node_class = self.attributes['class']

        # Path is calculated with tag and class if any
        path = [(self.type, node_class)]

        if self.identification == stop or (self.parent is None and stop is None):
            return path
        elif self.parent is None:
            return None
        else:
            ret = self.parent.get_path(stop)
            if ret is None:
                return None
            else:
                return ret + path

    def get_full_text(self):
        """
        This function returns the full text
        of a subtree with the current object
        as root node
        :return: str
        """
        full_text = ""

        for child in self.children:
            if isinstance(child, str):
                full_text += child
            else:
                full_text += child.get_full_text()

        return full_text
