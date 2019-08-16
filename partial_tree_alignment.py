import enhanced_simple_tree_matching as estm
import copy


def nodes_equal(node1, node2):
    if node1.type != node2.type:
        return False
    if 'class' in node1.attributes and 'class' in node2.attributes:
        if isinstance(node1.attributes['class'], list) and not isinstance(node2.attributes['class'], list):
            if node2.attributes['class'] not in node1.attributes['class']:
                return False
        elif isinstance(node2.attributes['class'], list) and not isinstance(node1.attributes['class'], list):
            if node1.attributes['class'] not in node2.attributes['class']:
                return False
        else:
            if node1.attributes['class'] != node2.attributes['class']:
                return False
    elif 'class' in node1.attributes and 'class' not in node2.attributes:
        return False
    elif 'class' not in node1.attributes and 'class' in node2.attributes:
        return False
    return True


def shift_groups(group, amount):
    for el in group:
        if el['start'] is not None:
            el['start'] += amount
        if el['end'] is not None:
            el['end'] += amount
    return group


def insert_into(s, t):
    # Not merging if the root nodes are not equal in
    # type and class
    if not nodes_equal(s, t):
        return [t], False
    # If both are leafs we merge the attributes and
    # texts
    if t.is_leaf():
        s.text += t.text
        # Making each attributes a list
        for key in s.attributes:
            if not isinstance(s.attributes[key], list):
                s.attributes[key] = [s.attributes[key]]
        for attr in t.attributes:
            if attr is s.attributes:
                if not isinstance(t.attributes[attr], list):
                    s.attributes[attr].append(t.attributes[attr])
                else:
                    s.attributes[attr] += t.attributes[attr]
            else:
                if not isinstance(t.attributes[attr], list):
                    s.attributes[attr] = [t.attributes[attr]]
                else:
                    s.attributes[attr] = t.attributes[attr]
        return [], False
    elif s.is_leaf():
        s.children = t.children
        return [], True
    else:
        groups_list = []
        start = None
        group = []
        changed = False
        # Calculating the nodes which match and those that not
        for child in t.get_children():
            # This variable is set when child of t and of s
            # are matching
            flag = False
            for i in range(len(s.get_children())):
                if flag:
                    break
                s_child = s.get_children()[i]

                if nodes_equal(s_child, child):
                    flag = True
                    groups_list.append({
                        'equal': True,
                        'nodes': [child],
                        'start': i,
                        'end': None
                    })
                    if len(group) > 0:
                        groups_list.append({
                            'equal': False,
                            'nodes': group,
                            'start': start,
                            'end': i
                        })
                        group = []
                    start = i
            if not flag:
                group.append(child)
        rest_children = []
        if len(group) > 0:
                groups_list.append({
                    'equal': False,
                    'nodes': group,
                    'start': start,
                    'end': None
                })

        for group in groups_list:
            if group['equal']:
                r, changed = insert_into(s.get_children()[group['start']], group['nodes'][0])
                if len(r) > 0:
                    child_copy = copy.copy(group['nodes'][0])
                    child_copy.children = r
                    rest_children.append(child_copy)
            else:
                if group['start'] is None and group['end'] is None:
                    rest_children += group['nodes']
                elif group['start'] is None:
                    if group['end'] is 0:
                        for i in range(len(group['nodes']) - 1, -1, -1):
                            s.children.insert(0, group['nodes'][i])
                        groups_list = shift_groups(groups_list, len(group['nodes']))
                        changed = True
                    else:
                        end = copy.copy(s.get_children()[group['end']])
                        end.text = ''
                        end.children = []
                        group['nodes'].append(end)
                        rest_children += group['nodes']
                elif group['end'] is None:
                    if group['start'] == len(s.get_children()) - 1:
                        s.children += group['nodes']
                        changed = True
                    else:
                        start = copy.copy(s.get_children()[group['start']])
                        start.text = ''
                        start.children = []
                        group['nodes'].insert(0, start)
                        rest_children += group['nodes']
                else:
                    for i in range(len(group['nodes']) - 1, -1, -1):
                        s.children.insert(group['start'] + 1, group['nodes'][i])
                    groups_list = shift_groups(groups_list, len(group['nodes']))
                    changed = True
        return rest_children, changed



def partial_tree_alignment(data_records):
    s = sorted(data_records, key =(lambda rec: rec.get_element_count()))
    t_s = s.pop()
    r = []
    while len(s) > 0:
        t_i = s.pop()
        rest, i = insert_into(t_s, t_i)
        if len(rest) > 0:
            t_i.text = ''
            t_i.children = rest
            r.append(t_i)
        if len(s) is 0 and i:
            s = r
            r = []
            i = False
    return t_s, r
