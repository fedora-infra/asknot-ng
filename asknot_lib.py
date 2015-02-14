#!/usr/bin/env python
""" Utilities module used by asknot scripts. """

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

translatable_collections = ['negatives', 'affirmatives', 'backlinks']
translatable_fields = ['title', 'description', 'segue1', 'segue2', 'subtitle']


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
    # Markup strings for translation
    for field in translatable_fields:
        if field in node:
            node[field] = _(node[field])

    for collection in translatable_collections:
        if collection in data:
            data[collection] = [_(s) for s in data[collection]]

    seen = seen or []
    node['id'] = slugify(node.get('title', 'foo'), seen)
    seen.append(node['id'])

    node['affirmative'] = random.choice(data['affirmatives'])
    node['negative'] = random.choice(data['negatives'])
    node['backlink'] = random.choice(data['backlinks'])


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


def translatable_strings(data, content):
    """ A generator that yields tuples containing translatable strings. """
    for key in translatable_fields:
        if key in data:
            yield data['__line__'], data[key], key

    for key in translatable_collections:
        if key in data:
            for string in data[key]:
                yield data['__line__'], string, key[:-1]

    for item in data.get('navlinks', []):
        yield data['__line__'], item['name'], 'navlink'

    if 'tree' in data:
        for items in translatable_strings(data['tree'], content):
            yield items

    children = data.get('children', [])
    if isinstance(children, basestring):
        pass
    else:
        for child in children:
            for items in translatable_strings(child, content):
                yield items


def extract(fileobj, keywords, comment_tags, options):
    """ Babel entry-point for extracting translatable strings from our yaml """
    loader = yaml.Loader(fileobj.read())
    def compose_node(parent, index):
        # the line number where the previous token has ended (plus empty lines)
        line = loader.line
        node = yaml.composer.Composer.compose_node(loader, parent, index)
        node.__line__ = line + 1
        return node

    def construct_mapping(node, deep=False):
        constructor = yaml.constructor.Constructor.construct_mapping
        mapping = constructor(loader, node, deep=deep)
        mapping['__line__'] = node.__line__
        return mapping

    loader.compose_node = compose_node
    loader.construct_mapping = construct_mapping
    data = loader.get_single_data()

    for lineno, string, comment in translatable_strings(data, content):
        yield lineno, None, [string], [comment]
