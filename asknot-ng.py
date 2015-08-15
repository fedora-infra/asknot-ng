#!/usr/bin/env python
""" asknot-ng.py [OPTIONS] template.html questions.yml path/to/locale

Ask not what $ORG can do for you... but what can you do for $ORG.
"""

from __future__ import print_function

import argparse
import copy
import gettext
import json
import os
import shutil
import sys
import traceback

from asknot_lib import (
    defaults,
    load_template,
    load_yaml,
    prepare_tree,
    gather_ids,
    produce_graph,
)


def work(question_filename, template, lang, languages,
         graph, build, static, _, **kw):
    """ Main work function.  Called once per 'lang' from ``main``.

    The function does all the things needed to build a copy of the site.
    Shortly, it:
        - loads the template used to render the html
        - loads the tree of questions from a questions file
        - recursively pulls in any other included questions files
        - prepares the tree by adding unique ids to each node
        - renders the template using the in-memory copy of the questions
        - writes out a copy of the rendered html to disk
    """

    template = load_template(template)

    data = load_yaml(question_filename)

    data['tree'] = prepare_tree(data, data['tree'], _=_)
    data['all_ids'] = list(gather_ids(data['tree']))
    data['all_ids_as_json'] = json.dumps(data['all_ids'], indent=4)
    data['tree_as_json'] = json.dumps(data['tree'], indent=4)

    kwargs = copy.copy(defaults)
    kwargs.update(data)
    kwargs.update(kw)
    kwargs['lang'] = lang
    kwargs['languages'] = languages

    if graph:
        dot = produce_graph(kwargs['tree'])
        dot.layout()#prog='dot')
        filename = '%s.svg' % kwargs.get('theme', 'asknot')
        dot.draw(filename)
        print("Wrote", filename)

    html = template.render(**kwargs)

    outdir = os.path.join(build, lang)
    global_staticdir = os.path.join(build, "static")
    global_staticdir_nb = os.path.abspath(static+"/global")

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    if not os.path.exists(global_staticdir):
        os.makedirs(global_staticdir)

    outfile = os.path.join(outdir, 'index.html')
    with open(outfile, 'wb') as f:
        f.write(html)
    print("Wrote", outfile)

    staticdir = os.path.abspath(static)
    statictarget = os.path.join(outdir, 'static')
    for tree in [statictarget, global_staticdir]:
        if os.path.exists(tree):
            shutil.rmtree(tree)
    shutil.copytree(staticdir, statictarget, symlinks=True)

    shutil.copytree(global_staticdir_nb, global_staticdir, symlinks=True)
    print("Copied %s to %s" % (staticdir, statictarget))


def main(localedir, languages, strict, **kw):
    """ Main entry point for for the command line tool.

    This function loops over all translated copies of the site that it can find
    and renders a copy of the site for each language by calling ``work``.
    """
    if languages is None:
        languages = [
            d for d in os.listdir(localedir)
            if os.path.isdir(os.path.join(localedir, d))]

        # Default to english..
        if 'en' not in languages and not strict:
            languages = languages + ['en']
    else:
        languages = languages.split(',')

    if not languages:
        print("No languages found.")

    fallback = not strict
    for lang in languages:
        try:
            translation = gettext.translation(
                'asknot-ng', localedir, languages=[lang], fallback=fallback)
        except IOError:
            traceback.print_exc()
            raise IOError("No translation found for %r" % lang)
        translation.install()


        if sys.version_info[0] == 3:
            _ = translation.gettext
        else:
            _ = translation.ugettext

        work(_=_, lang=lang, languages=languages, **kw)


def process_args():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("template", help="Path to a mako template "
                        "for the site.")
    parser.add_argument("question_filename", help="Path to a .yaml file "
                        "containing the config and question tree.")
    parser.add_argument("localedir", help="Location of the locale directory.")
    parser.add_argument("-t", "--theme", default="default",
                        help="Theme name to use.")
    parser.add_argument("-s", "--static", default="static",
                        help="Directory of static files (js, css..).")
    parser.add_argument("-b", "--build", default="build",
                        help="Directory to write output.")
    parser.add_argument("-l", "--languages", default=None,
                        help="List of languages to use.  Defaults to all.")
    parser.add_argument("-S", "--strict", default=False, action="store_true",
                        help="Fail if no translation is found.")
    parser.add_argument("-g", "--graph", default=False, action="store_true",
                        help="Also generate a graph of the question tree.")
    parser.add_argument('--fedmenu-url',
                        help="URL of the fedmenu resources (optional)")
    parser.add_argument('--fedmenu-data-url',
                        help="URL of the fedmenu data source (optional)")
    return parser.parse_args()


if __name__ == '__main__':
    args = process_args()
    args = vars(args)
    main(**args)
