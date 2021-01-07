#!/usr/bin/env python
""" Utilities module used by the asknot-ng.py script. """

import hashlib
import os
import random
import subprocess as sp
import sys

import mako.template
import pkg_resources
import yaml

# Lists of translatable strings so we know what to extract at extraction time
# and so we know what to translate at render time.
translatable_collections = ['negatives', 'affirmatives', 'backlinks']
translatable_fields = ['title', 'description', 'segue1', 'segue2', 'subtitle']

if sys.version_info[0] == 2:
    string_types = (basestring,)
else:
    string_types = (str, bytes,)


def asknot_version():
    try:
        return pkg_resources.get_distribution('asknot-ng').version
    except pkg_resources.DistributionNotFound:
        try:
            stdout = sp.check_output(['git', 'rev-parse', 'HEAD'])
            return stdout[:8]  # Short hash
        except:
            return 'unknown'


defaults = {
    'title': 'asknot-ng',
    'author': 'Ralph Bean',
    'description': (
        'Ask not what $ORG can do for you, '
        'but what you can do for $ORG'
    ),
    'asknot_version': asknot_version(),
    'favicon': 'whatever',
    'googlesiteverification': 'n/a',
    'navlinks': [],
    'negatives': ['No, thanks'],
    'affirmatives': ['Yes, please'],
    'backlinks': ['I was wrong, take me back'],
    'SEP': '#',  # Make this '/' for cool prod environments
}


def load_yaml(filename):
    """ Simply load our yaml file from disk. """
    with open(filename, 'r') as f:
        data = yaml.load(f.read(), Loader=yaml.BaseLoader)

    basedir = os.path.dirname(filename)

    try:
        validate_yaml(data, basedir)
    except:
        print("Problem with %r due to..." % filename)
        raise

    return data


def validate_yaml(data, basedir):
    """ Sanity check used to make sure the root question file is valid. """
    assert 'tree' in data
    assert 'children' in data['tree']
    validate_tree(data['tree'], basedir)


def validate_tree(node, basedir):
    """ Sanity check used to make sure the question tree is valid. """
    if not 'children' in node:
        if not 'link' in node:
            raise ValueError('%r must have either a "href" value or '
                             'a "children" list' % node)
    else:
        # Handle recursive includes in yaml files. The children of a node
        # may be defined in a separate file
        if isinstance(node['children'], string_types):
            include_file = node['children']
            if not os.path.isabs(include_file):
                include_file = os.path.join(basedir, include_file)

            node['children'] = load_yaml(include_file)['tree']['children']

        # Finally, validate all the children whether they are from a separately
        # included file, or not.
        for child in node['children']:
            validate_tree(child, basedir)


def slugify(title, seen):
    """ Return a unique id for a node given its title. """
    idx = title.lower()
    replacements = {
        ' ': '-',
        '+': 'plus',
        '!': 'exclamation',
        ',': 'comma',
        '\'': 'apostrophe',
    }
    for left, right in replacements.items():
        idx = idx.replace(left, right)
    while idx in seen:
        idx = idx + hashlib.md5(idx.encode('utf-8')).hexdigest()[0]
    return idx


def prepare_tree(data, node, parent=None, seen=None, _=lambda x: x):
    """ Utility method for "enhancing" the data in the question tree.

    This is called typically before rendering the mako template with data.

    A few things happen here:
        - Translatable strings are marked up so they can be translated.
        - Unique ids are assigned to each node in the tree for use by JS.
        - Texts for 'yes', 'no', and 'go back' are assigned at random per node.
        - For each node that doesn't have an image defined, propagate the image
          defined by its parent node.

    """

    # Markup strings for translation
    if node is data.get('tree'):
        for collection in translatable_collections:
            if collection in data:
                data[collection] = [_(s) for s in data[collection]]

    for field in translatable_fields:
        if field in node:
            node[field] = _(node[field])

    # Assign a unique id to this node.
    seen = seen or []
    node['id'] = slugify(node.get('title', 'foo'), seen)
    seen.append(node['id'])

    # Choose random text for our navigation buttons for this node.
    node['affirmative'] = random.choice(data['affirmatives'])
    node['negative'] = random.choice(data['negatives'])
    node['backlink'] = random.choice(data['backlinks'])

    # Propagate parent images to children unless otherwise specified.
    if parent and not 'image' in node and 'image' in parent:
        node['image'] = parent['image']

    # Recursively apply this logic to all children of this node.
    for i, child in enumerate(node.get('children', [])):
        node['children'][i] = prepare_tree(data, child, parent=node, seen=seen, _=_)

    return node


def gather_ids(node):
    """ Yields all the unique ids in the question tree recursively. """
    yield node['id']
    for child in node.get('children', []):
        for idx in gather_ids(child):
            yield idx


def produce_graph(tree, dot=None):
    """ Given a question tree, returns a pygraphviz object
    for later rendering.
    """
    import pygraphviz
    dot = dot or pygraphviz.AGraph(directed=True)

    idx = tree.get('id', 'root')
    dot.add_node(idx, label=tree.get('title', 'Root'))

    for child in tree.get('children', []):
        dot = produce_graph(child, dot)
        dot.add_edge(idx, child['id'])

    return dot


def load_template(filename):
    """ Load a mako template and return it for later rendering. """
    return mako.template.Template(
        filename=filename,
        strict_undefined=True,
        output_encoding='utf-8',
    )


def translatable_strings(data):
    """ A generator that yields tuples containing translatable strings from a
    question tree.

    The yielded tuples are of the form (linenumber, string, comment).
    """
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
        for items in translatable_strings(data['tree']):
            yield items

    children = data.get('children', [])
    if isinstance(children, str):
        pass
    else:
        for child in children:
            for items in translatable_strings(child):
                yield items


def load_yaml_with_linenumbers(fileobj):
    """ Return yaml with line numbers included in the dict.

    This is similar to our mundane ``load_yaml`` function, except that it
    modifies the yaml loader to include line numbers in the data.  Our babel
    extension which is used to extract translatable strings from our yaml files
    uses those line numbers to make things easier on translators.
    """
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
    return loader.get_single_data()


def extract(fileobj, keywords, comment_tags, options):
    """ Babel entry-point for extracting translatable strings from our yaml.

    This gets called by 'python setup.py extract_messages' when it encounters a
    yaml file.  (See setup.py for where we declare the existence of this
    function for bable using setuptools 'entry-points').
    """
    data = load_yaml_with_linenumbers(fileobj)

    for lineno, string, comment in translatable_strings(data):
        yield lineno, None, [string], [comment]
