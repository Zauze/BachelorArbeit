import enhanced_simple_tree_matching as estm
import validators.data_validator
# This module's function is to
# validate various conditions set on data regions and records
unallowed_tags = [
    'script',
    'footer',
    'meta',
    'noscript',
    'nav',
    'select',
    'option',
    'input',
    'img',
    'figure',
    'form'
]

unallowed_ids_classes = [
    'footer',
    'menu',
    'option'
]

MIN_REGION_DEPTH = 2
MAX_REGION_DEPTH = 10
MIN_INFORMATION_COUNT = 2

# Function for validating data_regions
def validate_data_region(data_region_node):
    # Validating depth
    data_region_node.calculate_depth()
    if data_region_node.depth <= MIN_REGION_DEPTH or data_region_node.depth >= MAX_REGION_DEPTH:
        return None

    # Validating ids, classes and tags
    if data_region_node.type in unallowed_tags:
        return None

    if validators.data_validator.DataValidator.in_class_ids(data_region_node, unallowed_ids_classes):
        return None

    # Cleaning children
    for child in data_region_node.get_children():
        for tag in unallowed_tags:
            child.remove_type(tag)
        for id_class in unallowed_ids_classes:
            child.remove_id(id_class)
            child.remove_class(id_class)

    # Information count check
    information_counts = []
    for child in data_region_node.get_children():
        information_counts.append(estm.terminal(child, False))
    if max(information_counts) < MIN_INFORMATION_COUNT:
        return None

    return True


# Function to preprocess dom trees
def preprocess(node):
    if isinstance(node, str) or node.is_leaf():
        return node

    if node.type == 'html':
        delete = []
        for child in node.get_children():
            if child.type == 'head':
                delete.append(child)

        node.remove_children(delete)
    else:
        remove = []
        for child in node.get_children():
            if child.type in unallowed_tags:
                remove.append(child)

        node.remove_children(remove)

    node.children = list(map(preprocess, node.children))
    return node
