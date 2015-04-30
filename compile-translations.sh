#!/bin/bash -x

for locale in $(ls locale/*.po); do
    echo $locale;
    locale=${locale#*/};
    locale=${locale%.po};
    mkdir -p locale/$locale/LC_MESSAGES/;
    msgfmt -o locale/$locale/LC_MESSAGES/asknot-ng.mo locale/$locale.po;
done

