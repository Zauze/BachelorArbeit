
from tree_processor import *
import tree_processor as tp
import html_node
import copy
import data_region_processor
import preprocessor
import urllib.request
import urllib.error
from easyhtml import parser
import constants
from constants import *
from html_node import *


def combined_compare(parent, k):
    """
    Compares nodes and groupings of nodes with each other,
    saves the results in the data containers of the nodes
    :param int k: the maximum amount of nodes in a grouping
    :param HTMLNode parent: the parent node of the nodes on which the comparison
                            and grouping should be performed
    :return: dict: containing the calculated distances between nodes and
                   groupings
    """
    nodes = parent.get_children()
    distances = {}
    for i in range(1, k + 1):
        distances[i] = {}

    for i in range(1, k+1):
        for j in range(i, k+1):
            if len(nodes) >= ( i + 2*j - 1):
                start = i
                for l in range(i + j, len(nodes) + 1, j):
                    if len(nodes) >= l + j - 1:
                        if j is 1:
                           key = (start - 1, l - 1)
                        else:
                           key = (tuple(range(start-1, l-1)), tuple(range(l-1, l+j-1)))
                        if 'distances' in parent.data_container:
                            if key in parent.data_container['distances'][i]:
                                continue
                        parent1 = html_node.HTMLNode('div', {}, None, 0)
                        parent2 = html_node.HTMLNode('div', {}, None, 0)
                        parent1.children = parent.truncate_children(start-1, l-1)
                        parent2.children = parent.truncate_children(l-1, l+j-1)
                        result = tp.modified_norm_tree_dist(parent1, parent2, True)

                        distances[j][key] = result
                        start = l
            else:
                break
    return distances


def mdr_2(node, k):
    """
    The enhanced Mining Data Records algorithm developed by B. Liu, R. Grossman, and Y. Zhai
    :param HTMLNode node: the node for which subtree the mdr-2 algorithm should
                          be performed.
    :param int k: the maximum amount of nodes in a grouping
    :return: None
    """
    node.calculate_depth()
    if node.depth >= data_region_processor.MIN_REGION_DEPTH:
        if 'distances' not in node.data_container:
            node.data_container['distances'] = combined_compare(node, k)
        for child in node.get_children():
            if 'distances' not in child.data_container:
                mdr_2(child, k)


def distance(node, i, j, k):
    """
    A recursive distance calculating algorithm using mdr-2,
    checks whether distances already got calculated
    :param HTMLNode node: the node on which subtree the algorithm should be performed
    :param int i: the current grouping size
    :param int j: the start index
    :param int k: the maximum amount of nodes in a grouping
    :return: float : the result of the computation for grouping size i
                     starting at index j of node's children
    """
    if 'distances' not in node.data_container:
        mdr_2(node, k)
    distances = node.data_container['distances']
    if i == 1:
        if (j-1,j) not in distances[i]:
            return 1.0
        return distances[i][(j-1, j)]
    else:
        key = (tuple(range(j - 1, j + i - 1)), tuple(range(j + i - 1, j + 2*i - 1)))
        if key not in distances[i]:
            return 1.0
        return distances[i][key]


def valid(cur_dr):
    # TODO: finish this
    """
    In this function extra validation
    processes can be done to ensure
    that the data region given in cur_dr
    is proper
    :param HTMLNode cur_dr: current data record
    :return: bool
    """
    return True


def identify_data_regions(start, node, k, threshold):
    """
    Algorithm to identify data regions within a given node
    :param int start: start index
    :param HTMLNode node: the node to process
    :param k: the maximum grouping size
    :param float threshold: a value deciding up to which value,
           two nodes are can be seen as equal
    :return: list of dict : list containing id of a node and its data regions
    """
    max_dr = [0, 0, 0]
    cur_dr = [0, 0, 0]
    for combination in range(1, k):
        for f in range(start, start + combination + 1):
            flag = True
            for curr_st_node in range(f, len(node.get_children()) + 1, combination):
                res = distance(node, combination, curr_st_node, k)
                if res <= threshold:
                    if flag is True:
                        cur_dr = [combination, curr_st_node-1, 2 * combination]
                        flag = False
                    else:
                        cur_dr[2] += combination
                elif flag is False:
                    break
            if max_dr[2] < cur_dr[2] and (
                    max_dr[1] == 0 or
                    cur_dr[1] <= max_dr[1]) and valid(cur_dr):
                max_dr = cur_dr
    if max_dr[2] is not 0:
        if max_dr[1] + max_dr[2] is not len(node.get_children()):
            return [{node.identification: max_dr}] + identify_data_regions(max_dr[1] + max_dr[2], node, k, threshold)
        else:
            return [{node.identification: max_dr}]
    return []


def uncovered_data_regions(parent, child):
    """
    Identifies data regions of a child which are not contained in the
    parent's data regions
    :param HMLNode parent:
    :param HTMLNode child:
    :return: list of dict: the uncovered data regions if any
    """
    if 'data_regions' not in child.data_container:
        child.data_container['data_regions'] = []
    for dict in parent.data_container['data_regions']:
        data_region = dict[parent.identification]
        if parent.get_children().index(child) in range(data_region[1], data_region[1] + data_region[2]):
            return []
    return child.data_container['data_regions']


def find_data_regions(node, k, threshold):
    """
    Finds recursively data region for the given sub tree
    with param node as root. Saves the regions in the data
    container of the node
    :param HTMLNode node: root
    :param k: the maximum amount of node grouping
    :param float threshold: a value deciding up to which value,
           two nodes are can be seen as equal
    :return: None
    """
    node.calculate_depth()
    node.data_container['data_regions'] = []
    if data_region_processor.MAX_REGION_DEPTH >= node.depth >= data_region_processor.MIN_REGION_DEPTH:
        node.data_container['data_regions'] = identify_data_regions(1, node, k, threshold)
    temp_regions = []
    for child in node.get_children():
        find_data_regions(child, k, threshold)
        temp_regions += uncovered_data_regions(node, child)
    node.data_container['data_regions'] += temp_regions


def extract_data_regions(node):
    """
    Finds and extracts data regions for given sub tree
    with param node as root. Return a list of data regions.
    :param HTMLNode node: root
    :return: list of HTMLNode : the data regions
    """
    data_regions = []
    for data_region in node.data_container['data_regions']:
        for iden in data_region:
            tmp = node.find_id(iden)
            data_region_node = copy(tmp)
            region_info = data_region[iden]
            if region_info[0] == 1:
                children = data_region_node.truncate_children(
                    region_info[1], region_info[1] + region_info[2]
                )

                data_region_node.children = children
            else:
                times = int(region_info[2]/region_info[0])
                children = []
                start = region_info[1]
                for i in range(times):
                    artifical_node = HTMLNode(
                        'li',
                        { 'class': "data_record" },
                        '',
                        1
                    )
                    artifical_node.children = data_region_node.truncate_children(start, start + region_info[0])
                    artifical_node.compute_text()
                    start += region_info[0]
                    children.append(artifical_node)
                data_region_node.children = children
            data_regions.append(data_region_node)
    return data_regions


def main_text_extraction(root):
    """
    Extracts the main text of a detailed page
    :param HTMLNode root:
    :return: list of HTMLNode: the main content area
    """
    main_content = []
    # Get the node with the most content
    ret_dict = find_most_text_node(root)
    main_node = root.find_id(ret_dict['id'])
    main_content.append(main_node)

    # Checking the neighbors of the main node
    parent = main_node.parent
    neighbors = parent.get_children()
    ind = neighbors.index(main_node)
    left_neighbors = neighbors[0:ind] or []
    left_neighbors = list(reversed(left_neighbors))
    right_neighbors = neighbors[ind + 1:-1] or []

    # The value of 10 is hardcoded and can be adjusted
    for l in left_neighbors:
        if tp.number_of_words(l.get_full_text()) >= 10:
            main_content.insert(0, l)
        elif l.type in HEADER:
            main_content.insert(0, l)
            break

    for r in right_neighbors:
        if tp.number_of_words(r.get_full_text()) >= 10:
            main_content.append(r)

    return main_content


def process_link(link):
    """
    Processes the given link, does some noise removal
    and return the detailed page in form of a HTMLNode object
    :param str link:
    :return: list of HTMLNode
    """
    website = constants.website

    # Build the right website link
    if link[0] == '/':
        if re.search('(^((http[s]{0,1}://)?www\.)?.+\.[a-z]+)/', website) is None:
            constants.logger.error('Unknown website link format')
            return None
        else:
            site_pref = re.findall('(^((http[s]{0,1}://)?www\.)?.+\.[a-z]+)/', website)[0][0]
            website = site_pref + link
    else:
        website = link

    # Launch website and get HTML code
    try:
        response = urllib.request.urlopen(website)
    except urllib.error.URLError:
        constants.logger.error('Page:"%s" was not able to launch' % website)
        return None
    source = response.read().decode('latin-1')

    # Transfer HTML code via easyhtml
    dom_parser = parser.DOMParser()
    dom_parser.feed(str(source))
    document = dom_parser.get_dom()

    # Finding the html node
    html_object = None
    for node in document.elements:
        if isinstance(node, easyhtml.dom.HTMLTag):
            if node.tag_name == 'html':
                html_object = node
                break
    if html_object is None:
        constants.logger.error('No html tag was found on detailed page')
        return None

    # Transforming the dom tree into the built in data objects
    # of HTMLNodes
    detailed_page = HTMLNode(html_object, 0)

    # preprocessing and noise removal
    preprocessor.preprocess(detailed_page)
    preprocessor.remove_noise_dp(detailed_page)

    # Finding and returning main text
    return detailed_page


def get_unformatted_text(node):
    """
    Returns the text of a node plus all text
    which is included into formatting children nodes
    :param HTMLNode node: the node to process
    :return: str
    """
    text = ''
    for child in node.children:
        if isinstance(child, str):
            text += child
        else:
            if child.type in FORMAT_TAGS:
                text += get_unformatted_text(child)
    return text


def find_most_text_node(node):
    """
    Finds recursively the node with the most word count
    :param HTMLNode node: the root node, where to start
    :return: dict : 'id' is the id of a node, 'words' is the word count
    """
    text = get_unformatted_text(node)
    word_count = tp.number_of_words(text)
    ret_dict = {
        'id': node.identification,
        'words': word_count
    }
    for child in node.get_children():
        ret_child = find_most_text_node(child)
        if ret_child['words'] > ret_dict['words']:
            ret_dict = ret_child
    return ret_dict

