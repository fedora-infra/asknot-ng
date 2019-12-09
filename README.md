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

## Container

Asknot can be build and released as a container, to do so you can use the provided Dockerfile.


```
podman build -t asknot .
```

The Dockerfile makes use of multistage container build, meaning that in a first stage a container is used to prepare the translations and build the static pages then the static content is copied to a second container which is used to serve this content.


#### Running Container

```
podman run --name=asknot -d -p 8080:80 --net=host localhost/asknot
```

#### Composing Container

Asknot can be build and released as a container, in other similar way to do so you can use the provided Dockerfile-compose file.

```
podman-compose up -d
```

#### Verifiying

In your Favorite Browser Just type:

```
localhost:8080
```

#### Down Container

Asknot can be stop it and released the container when  finish it.

```
podman-compose down
```

#### Make Changes

build stack images again

```
podman-compose build
```

and then:

```
podman-compose up -d
```

## Application Deployment

``asknot-ng`` currently runs on Fedora infrastructure Openshift instance. There are 2 deployments one in [staging] and one in [production].

The deployment of new version to these environment is managed from the github repository, thanks to the following 2 branches ``staging`` and ``production``.

### Staging

To deploy a change to the staging environment you need to push the commits to the ``staging`` branch, then Openshift will trigger a build using the Dockerfile located
in this repository and deploy the new application.

### Production

To deploy a change in the production environment you need to push the commits to the ``production`` branch, then Openshift will trigger a build using the Dockerfile located
in this repository and deploy the new application.

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
[staging]: https://stg.whatcanidoforfedora.org/
[production]: https://whatcanidoforfedora.org/
