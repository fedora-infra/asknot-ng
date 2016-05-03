# asknot-ng

[![Build Status](https://travis-ci.org/fedora-infra/asknot-ng.svg)](https://travis-ci.org/fedora-infra/asknot-ng)

Ask not what `$ORG` can do for you, but what you can do for `$ORG`.

Written by [@ralphbean][threebean].  Inspired by [the original work][wcidfm] of
[Josh Matthews][jdm], [Henri Koivuneva][wham], and [others][asknot-contribs].

I stumbled upon and loved the original [whatcanidoformozilla.org][wcidfm] and
wanted to deploy it for the [Fedora Community][fedora] but I found that I
couldn’t easily change the questions and links that were presented.  A year
went by and in 2015 I wrote this:  “asknot-ng”.

The gist of this “next generation” rewrite is to make it as configurable as
possible.  There is a primary script, ``asknot-ng.py``
that works like a static-site generator.  It takes as input three things:

- A questions file, written in yaml (see the [example][example-questions] or
  [Fedora’s file][fedora-questions]).  You’ll have to write your own one of
  these.
- A template file, written in mako (the [default][default-template] should work
  for everybody).
- A ‘theme’ argument to specify what CSS to use.  The default is nice enough,
  but you’ll probably want to customize it to your own use case.

We have a [Fedora instance up and running][wcidff] if you’d like to poke it.

## Requirements

The site-generator script is written in Python, so you’ll need that.
Furthermore, see [requirements.txt][requirements] or just run::

    $ sudo yum install python-mako PyYAML python-virtualenv

The script can optionally generate an svg visualizing your question tree.  This
requires pygraphviz which you could install like so:

    $ sudo yum install python-pygraphviz

## Giving it a run

Install the requirements, first.

Clone the repo::

    $ git clone https://github.com/fedora-infra/asknot-ng.git
    $ cd asknot-ng

Create a virtualenv into which you can install the module.

    $ virtualenv --system-site-packages venv
    $ source venv/bin/activate
    $ python setup.py develop

Run the script with the Fedora configuration::

    $ ./asknot-ng.py templates/index.html questions/fedora.yml l10n/fedora/locale --theme fedora
    Wrote build/en/index.html

and open up `build/en/index.html` in your favorite browser.

## Preparing Translations

First, setup a virtualenv, install Babel, and build the egg info.

    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install Babel
    $ python setup.py develop

Then, extract the translatable strings:

    $ python setup.py extract_messages --output-file l10n/fedora/locale/asknot-ng.pot

## Deploying to OpenShift

This is a very easy way to bring ``asknot-ng`` to a production server using
OpenShift.

Just create a new application using RHC and set the environment variables to
your demands:

```
rhc app create askorg diy --from-code https://github.com/fedora-infra/asknot-ng#develop
rhc set-env ASKNOT_THEME=org -a askorg
rhc set-env ASKNOT_QUESTION_FILE=questions/org.yml -a askorg
rhc app restart askorg
```

## Contributing back

``asknot-ng`` is licensed GPLv3+ and we’d love to get patches back containing
even the things you might not think we want.  If you have a questions file for
your repo, a modified template, or a CSS theme for your use case, please
[send them to us][patches].  It would be nice to build a library of deployments
so we can all learn.

**Note**: While the application is licensed GPLv3+, The [Fedora 22 wallpaper](static/themes/fedora/img/background.png) used is licensed under a *Creative Commons Attribution 4 License*.

Of course, bug reports and patches to the main script are appreciated as
always.

Happy Hacking!

[threebean]: http://threebean.org
[fedora]: http://getfedora.org
[example-questions]: https://github.com/fedora-infra/asknot-ng/blob/develop/questions/example.yml
[fedora-questions]: https://github.com/fedora-infra/asknot-ng/blob/develop/questions/fedora.yml
[default-template]: https://github.com/fedora-infra/asknot-ng/blob/develop/templates/index.html
[requirements]: https://github.com/fedora-infra/asknot-ng/blob/develop/requirements.txt
[patches]: https://help.github.com/articles/editing-files-in-another-user-s-repository/
[wcidfm]: http://whatcanidoformozilla.org
[wcidff]: http://whatcanidoforfedora.org
[jdm]: http://www.joshmatthews.net
[wham]: http://wham.fi
[asknot-contribs]: https://github.com/jdm/asknot/contributors
