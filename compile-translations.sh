#!/bin/bash -x

ASKNOT_LOCALE_DIR=${ASKNOT_LOCALE_DIR:-locale}

for locale in $(ls $ASKNOT_LOCALE_DIR/*.po); do
    echo $locale;
    locale=$(basename $locale)
    locale=${locale%.po};
    mkdir -p $ASKNOT_LOCALE_DIR/$locale/LC_MESSAGES/;
    msgfmt -o $ASKNOT_LOCALE_DIR/$locale/LC_MESSAGES/asknot-ng.mo $ASKNOT_LOCALE_DIR/$locale.po;
done

