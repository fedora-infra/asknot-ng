#!/usr/bin/env python
""" asknot-ng.py [OPTIONS] template.html config.yml

Ask not what $ORG can do for you... but what can you do for $ORG.
"""

from __future__ import print_function

import argparse
import copy
import json
import hashlib
import os
import random

import mako.template
import yaml

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


def prepare_tree(data, node, parent_idx=None, seen=None):
    seen = seen or []
    node['id'] = slugify(node.get('title', 'foo'), seen)
    seen.append(node['id'])

    node['affirmative'] = random.choice(data['affirmatives'])
    node['negative'] = random.choice(data['negatives'])
    node['backlink'] = random.choice(data['backlinks'])

    for i, child in enumerate(node.get('children', [])):
        node['children'][i] = prepare_tree(data, child, node['id'], seen)

    return node


def gather_ids(node):
    yield node['id']
    for child in node.get('children', []):
        for idx in gather_ids(child):
            yield idx


def load_template(filename):
    return mako.template.Template(filename=filename, strict_undefined=True)


def main(config, template, outfile=None, **args):
    template = load_template(template)

    data = load_yaml(config)

    data['tree'] = prepare_tree(data, data['tree'])
    data['all_ids'] = list(gather_ids(data['tree']))
    data['all_ids_as_json'] = json.dumps(data['all_ids'], indent=4)
    data['tree_as_json'] = json.dumps(data['tree'], indent=4)

    kwargs = copy.copy(defaults)
    kwargs.update(data)
    kwargs.update(args)
    html = template.render(**kwargs)

    if outfile:
        with open(outfile, 'w') as f:
            f.write(html)
        print("Wrote", outfile)
    else:
        print(html)


def process_args():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("template", help="Path to a mako template "
                        "for the site.")
    parser.add_argument("config", help="Path to a .yaml file "
                        "containing the config and question tree.")
    parser.add_argument("-t", "--theme", default="default",
                        help="Theme name to use.")
    parser.add_argument("-o", "--outfile", default="asknot.html",
                        help="Where to write output.")
    return parser.parse_args()


if __name__ == '__main__':
    args = process_args()
    args = vars(args)
    main(**args)

