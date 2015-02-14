#!/usr/bin/env python
""" asknot-ng.py [OPTIONS] template.html config.yml

Ask not what $ORG can do for you... but what can you do for $ORG.
"""

from __future__ import print_function

import argparse
import copy
import json

from asknot_lib import (
    defaults,
    load_template,
    load_yaml,
    prepare_tree,
    gather_ids,
    produce_graph,
)


def main(config, template, graph, outfile=None, **args):
    template = load_template(template)

    data = load_yaml(config)

    data['tree'] = prepare_tree(data, data['tree'])
    data['all_ids'] = list(gather_ids(data['tree']))
    data['all_ids_as_json'] = json.dumps(data['all_ids'], indent=4)
    data['tree_as_json'] = json.dumps(data['tree'], indent=4)

    kwargs = copy.copy(defaults)
    kwargs.update(data)
    kwargs.update(args)

    if graph:
        dot = produce_graph(kwargs['tree'])
        dot.layout()#prog='dot')
        filename = '%s.svg' % kwargs.get('theme', 'asknot')
        dot.draw(filename)
        print("Wrote", filename)

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
    parser.add_argument("-g", "--graph", default=False, action="store_true",
                        help="Also generate a graph of the question tree.")
    return parser.parse_args()


if __name__ == '__main__':
    args = process_args()
    args = vars(args)
    main(**args)

