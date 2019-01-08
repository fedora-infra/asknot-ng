#!/bin/bash

./compile-translations.sh

python3 asknot-ng.py \
	./templates/index.html \
	./questions/fedora.yml \
	./l10n/fedora/locale \
	-s ./static \
	-t fedora \
	--fedmenu-url="https://apps.fedoraproject.org/fedmenu" \
	--fedmenu-data-url="https://apps.fedoraproject.org/js/data.js"
