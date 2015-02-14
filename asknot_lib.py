#!/usr/bin/env python
""" Utilities module used by asknot scripts. """

import argparse
import copy
import json
import hashlib
import os
import random
import sys

import mako.template
import yaml

import gettext
t = gettext.translation('asknot-ng', 'locale', fallback=True)

if sys.version_info[0] == 3:
    _ = t.gettext
else:
    _ = t.ugettext


VERSION = "0.0"


def asknot_version():
    return VERSION


defaults = {
    'title': 'asknot-ng',
    'author': 'Ralph Bean',
    'description': (
        'Ask not what $ORG can do for you, '
        'but what you can do for $ORG'
    ),
    'asknot_version': asknot_version(),
    'icon': 'whatever',
    'navlinks': [],
    'negatives': ['No, thanks'],
    'affirmatives': ['Yes, please'],
    'backlinks': ['I was wrong, take me back'],
    'SEP': '#',  # Make this '/' for cool prod environments
}


def load_yaml(filename):
    with open(filename, 'r') as f:
        data = yaml.load(f.read())

    basedir = os.path.dirname(filename)

    try:
        validate_yaml(data, basedir)
    except:
        print("Problem with %r due to..." % filename)
        raise

    return data


def validate_yaml(data, basedir):
    assert 'tree' in data
    assert 'children' in data['tree']
    validate_tree(data['tree'], basedir)


def validate_tree(node, basedir):
    if not 'children' in node:
        if not 'href' in node:
            raise ValueError('%r must have either a "href" value or '
                             'a "children" list' % node)
    else:
        # Handle recursive includes in yaml files. The children of a node
        # may be defined in a separate file
        if isinstance(node['children'], basestring):
            include_file = node['children']
            if not os.path.isabs(include_file):
                include_file = os.path.join(basedir, include_file)

            node['children'] = load_yaml(include_file)['tree']['children']

        # Finally, validate all the children whether they are from a separately
        # included file, or not.
        for child in node['children']:
            validate_tree(child, basedir)


def slugify(title, seen):
    idx = title.replace(' ', '-').lower()
    while idx in seen:
        idx = idx + hashlib.md5(idx).hexdigest()[0]
    return idx


def prepare_tree(data, node, parent=None, seen=None):
    seen = seen or []
    node['id'] = slugify(node.get('title', 'foo'), seen)
    seen.append(node['id'])

    node['affirmative'] = random.choice(data['affirmatives'])
    node['negative'] = random.choice(data['negatives'])
    node['backlink'] = random.choice(data['backlinks'])

    # Markup strings for translation
    if 'title' in node:
        node['title'] = _(node['title'])

    # Propagate parent images to children unless otherwise specified.
    if parent and not 'image' in node and 'image' in parent:
        node['image'] = parent['image']

    for i, child in enumerate(node.get('children', [])):
        node['children'][i] = prepare_tree(data, child, parent=node, seen=seen)

    return node


def gather_ids(node):
    yield node['id']
    for child in node.get('children', []):
        for idx in gather_ids(child):
            yield idx


def produce_graph(tree, dot=None):
    import pygraphviz
    dot = dot or pygraphviz.AGraph(directed=True)

    idx = tree.get('id', 'root')
    dot.add_node(idx, label=tree.get('title', 'Root'))

    for child in tree.get('children', []):
        dot = produce_graph(child, dot)
        dot.add_edge(idx, child['id'])

    return dot


def load_template(filename):
    return mako.template.Template(filename=filename, strict_undefined=True)
