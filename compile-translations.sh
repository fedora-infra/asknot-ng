#!/bin/bash -x

ASKNOT_LOCALE_DIR=${ASKNOT_LOCALE_DIR:-l10n/fedora/locale}
rm -f container/l10n.conf

for locale in $(ls $ASKNOT_LOCALE_DIR/*.po); do
    echo $locale;
    locale=$(basename $locale)
    locale=${locale%.po};
    mkdir -p $ASKNOT_LOCALE_DIR/$locale/LC_MESSAGES/;
    msgfmt -o $ASKNOT_LOCALE_DIR/$locale/LC_MESSAGES/asknot-ng.mo $ASKNOT_LOCALE_DIR/$locale.po;

    printf "RewriteCond %%{HTTP:Accept-Language} ^${locale//_/$'-'} [NC]\n" >> container/l10n.conf
    printf "RewriteRule \"^/$\" \"/$locale/\" [L,R]\n\n" >> container/l10n.conf
done

