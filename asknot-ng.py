#!/usr/bin/env python
""" asknot-ng.py [OPTIONS] template.html config.yml

Ask not what $ORG can do for you... but what can you do for $ORG.
"""

from __future__ import print_function

import argparse
import copy
import json
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
    'theme': 'default',
    'navlinks': [],
    'negatives': ['No, thanks'],
    'affirmatives': ['Yes, please'],
    'backlinks': ['I was wrong, take me back'],
    'SEP': '#',  # Make this '/' for cool prod environments
}

def load_yaml(config):
    with open(config, 'r') as f:
        return yaml.load(f.read())


def validate_yaml(data):
    assert 'tree' in data
    validate_tree(data['tree'])


def validate_tree(node):
    if not 'children' in node:
        if not 'href' in node:
            raise ValueError('%r must have either a "href" value or '
                             'a "children" list' % node)
    else:
        for child in node['children']:
            validate_tree(child)


def slugify(title):
    return title.replace(' ', '-').lower()


def prepare_tree(data, node, parent_idx=None):
    node['id'] = slugify(node.get('title', 'foo'))
    node['affirmative'] = random.choice(data['affirmatives'])
    node['negative'] = random.choice(data['negatives'])
    node['backlink'] = random.choice(data['backlinks'])

    for i, child in enumerate(node.get('children', [])):
        node['children'][i] = prepare_tree(data, child, node['id'])

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
    validate_yaml(data)
    data['tree'] = prepare_tree(data, data['tree'])
    data['all_ids'] = list(gather_ids(data['tree']))
    data['all_ids_as_json'] = json.dumps(data['all_ids'], indent=4)
    data['tree_as_json'] = json.dumps(data['tree'], indent=4)

    kwargs = copy.copy(defaults)
    kwargs.update(data)
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
    parser.add_argument("-o", "--outfile", default="asknot.html",
                        help="Where to write output.")
    return parser.parse_args()


if __name__ == '__main__':
    args = process_args()
    args = vars(args)
    main(**args)

