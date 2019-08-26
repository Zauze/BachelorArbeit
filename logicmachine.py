# This module checks nodes for their identities
from enum import Enum
import validators
from validators.data_label import DataLabel
from validators.noise_validator import *
from validators.date_validator import *
from validators.data_validator import *
from validators.data_label import DataLabel
from validators.time_validator import *
from validators.location_validator import *
from validators.long_desc_validator import *
from validators.short_desc_validator import *
from validators.title_validator import *
from validators.link_validator import *
import re
from HTML_Tree import HTMLNode

# This constant decides at which modified depth a node is
# denoted as too high to contain a data item
# modified depth: depth counted up if the current node is not a simplified type
# (like strong etc.)
MAX_HEIGHT = 1
LABELS = [
        DataLabel.TIME,
        DataLabel.DATE,
        DataLabel.TITLE,
        DataLabel.SHORT_DESC,
        DataLabel.LINK,
        DataLabel.LOCATION,
    ]


def run_validation(node, n, label_dict):
    """
    This function runs all the validation process of
    each validator for a given node and saves the information
    in the data container of the node and in the given
    label_dict. The function is recursive, regarding the
    n number, which stands for the level in the tree of valid nodes.
    Here a valid node is a node, that is not a <p> or <strong> tag,
    but can contain those as children.

    :param HTMLNode node: the node to validate
    :param int n: the number of the valid node
    :param dict label_dict: the dict, where information about hits and
           scores will be stored for each label.
    :return: None
    """
    # If the height is too big
    if n > MAX_HEIGHT:
        return

    hit = False
    class_list = [
        NoiseValidator,
        DateValidator,
        TimeValidator,
        TitleValidator,
        ShortDescValidator,
        LocationValidator,
        LinkValidator
    ]
    node.data_container['label'] = {
        'hits': [],
        'scores': [],
        'not': []
    }
    for cl in class_list:
        obj = cl()
        if obj.get_label() not in label_dict:
            label_dict[obj.get_label()] = {
                'hits': [],
                'scores': []
            }

        ret = obj.run_checks(node)
        if isinstance(ret, tuple):
            node.data_container['label']['scores'].append(ret)
            if (ret[0], node) not in label_dict[ret[1]]['scores']:
                label_dict[ret[1]]['scores'].append((ret[0], node))
        else:
            if ret is not None:
                if ret is not DataLabel.UNKNOWN:
                    if node not in label_dict[ret]['hits']:
                        label_dict[ret]['hits'].append(node)
                    node.data_container['label']['hits'].append(ret)
                    if ret is DataLabel.NOISE:
                        break
                    hit = True
            else:
                node.data_container['label']['not'].append(obj.get_label())
    if node.parent is not None:
        if node.type in ['div', 'td', 'tr']:
            run_validation(node.parent, n + 1, label_dict)
        elif node.type in ['p', 'strong'] or estm.number_of_words(node.get_pure_text()) > 0:
            run_validation(node.parent, n, label_dict)
        else:
            run_validation(node.parent, n+1, label_dict)


def process_data_regions(data_regions):
    """
    Processes the data regions and returns a final data region,
    whose children(data records) contain validated label dicts.

    :param list of HTMLNode data_regions: the raw data regions
    :return: HTMLNode
    """
    main_region = None
    for region in data_regions:
        region.update()
        starters = region.find_nodes_with_depth(0)
        label_dict = {}
        for node in starters:
            run_validation(node, 0, label_dict)
        # Very important - removing redundant nodes, since we
        # are using the region with the most hits as main
        process_hits(label_dict)
        region.data_container['label_dict'] = label_dict

        # If a data region has no hits
        if count_hits(label_dict) == 0:
            continue

        # Only overwriting if region has more hits than the previous one
        if main_region is None:
            main_region = region
        else:
            if count_hits(label_dict) > count_hits(main_region.data_container['label_dict']):
                main_region = region
            elif count_hits(label_dict) == count_hits(main_region.data_container['label_dict']):
                main_region.children += region.children
                # merge_data_regions(main_region, region)
    # No hits found in any region
    if main_region is None:
        regions_list = get_main_region_by_points(data_regions)
        if len(regions_list) == 1:
            main_region = regions_list[0]
        else:
            # Creating a merged data_region
            try:
                main_region = regions_list[0]
            except:
                a = 10
            for index in range(1, len(regions_list)):
                main_region.children += regions_list[index].children
                # merge_data_regions(main_region, regions_list[index])

    main_region.update()
    for record in main_region.get_children():
        starters = record.find_nodes_with_depth(0)
        label_dict = {}
        for node in starters:
            run_validation(node, 0, label_dict)
        # Very important - removing redundant nodes, since we
        # are using the region with the most hits as main
        process_hits(label_dict)
        record.data_container['label_dict'] = label_dict
    return main_region


def merge_data_regions(region1, region2):
    """
    Merges two data regions together
    :param HTMLNode region1:
    :param HTMLNode region2:
    :return: HTMLNode
    """
    # Finding the region with the lower amount of records
    if len(region1.get_children()) > len(region2.get_children()):
        smaller = region2
        bigger = region1
    else:
        smaller = region1
        bigger = region2

    children = []
    for index in range(len(smaller.get_children())):
        # Creating an new artificial root node for the records
        rec_root = HTMLNode('div', None, '', 0)
        rec_root.children = [smaller.get_children()[index], bigger.get_children()[index]]
        rec_root.update()
        children.append(rec_root)

    region1.children = children
    region1.update()
    return region1


def get_main_region_by_points(regions):
    """
    Finds the region with the biggest amount of highest points
    in labels, if there are several, returns a list of regions
    :param list of HTMLNode regions: the regions to inspect
    :return: list of HTMLNode
    """
    points = [0] * len(regions)
    for label in LABELS:
        max_values = []
        for region in regions:
            if label in region.data_container['label_dict'] and len(region.data_container['label_dict'][label]['scores']) > 0:
                max_values.append(max(list(map(lambda x: x[0], region.data_container['label_dict'][label]['scores']))))
            else:
                max_values.append(0)

        if len(max_values) == 0:
            max_value = 0
        else:
            max_value = max(max_values)
        for index in range(0, len(max_values)):
            if max_values[index] == max_value:
                points[index] += 1

    ret_list = []
    if len(points) == 0:
        max_value = 0
    else:
        max_value = max(points)
    for index in range(len(points)):
        if points[index] == max_value:
            ret_list.append(regions[index])
    return ret_list


def count_hits(label_dict):
    """
    Counts how many hits are in the given label_dict

    :param dict label_dict: the dict with the hit information
    :return: int: number of hits
    """
    count = 0
    for label in label_dict:
        if label == DataLabel.NOISE:
            continue
        count += len(label_dict[label]['hits'])
    return count


def process_hits(label_dict):
    """
    This function processes the label_dict (the dict containing all the label hits and scores
    and removes redundant nodes, in detail:
    - If in a hit list parent and child are present - the child will be removed
    :param dict label_dict: the dict containing all hits and node scores.
    :return: None
    """
    for label in label_dict:
        # Skipping the noise data since we won't use it
        if label == DataLabel.NOISE:
            continue
        # If we have only one hit or None we skip the execution
        if len(label_dict[label]['hits']) > 1:
            remove_list = []
            for node in label_dict[label]['hits']:
                if node.parent in label_dict[label]['hits']:
                    remove_list.append(node)
            for el in remove_list:
                label_dict[label]['hits'].remove(el)


def check_paths(main_region, label):
    """
    Collects paths from data record root to information node based on their
    hits or scores and check for similarities. The combination of path and label
    which is the highest for each label will be granted with a score of 2 (therefore
    later will be prefered for extraction).
    :param main_region:
    :return: None
    """
    paths = dict()
    candidates = []
    for record in main_region.get_children():
        # Retrieving the candidate nodes - those are either the hits or
        # the ones with highest score for the given label
        if len(record.data_container['label_dict'][label]['hits']) > 0:
            candidates += record.data_container['label_dict'][label]['hits']
        else:
            val_list = list(map(lambda x: x[0], record.data_container['label_dict'][label]['scores']))
            if len(val_list) == 0:
                continue
            max_val = max(val_list)
            for tup in record.data_container['label_dict'][label]['scores']:
                if tup[0] is not max_val:
                    continue
                else:
                    candidates.append(tup[1])

    # Getting paths and counting their occurrences
    for candidate in candidates:
        path = candidate.get_path(main_region.identification)
        path_str = str(path)
        if path_str in paths.keys():
            paths[path_str] += 1
        else:
            paths[path_str] = 1

    # Checking if there are multiple elements with maximum value
    val_list = list(map(lambda x: x, paths.values()))
    if len(val_list) > 0:
        max_val = max(val_list)
    else:
        max_val = 0
    found = False
    max_path = None
    for path in paths:
        if paths[path] == max_val and not found:
            found = True
            max_path = path
        elif paths[path] == max_val:
            max_path = None
            break

    # Adjusting values of score nodes if max_path is not None
    # Else doing nothing
    if max_path is not None:
        for record in main_region.get_children():
            ind = 0
            matching_ind = []
            for tp in record.data_container['label_dict'][label]['scores']:
                if str(tp[1].get_path(main_region.identification)) == max_path:
                    matching_ind.append(ind)
                ind += 1
            for i in matching_ind:
                node = record.data_container['label_dict'][label]['scores'][i][1]
                record.data_container['label_dict'][label]['scores'][i] = (2, node)











