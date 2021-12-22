#!/bin/bash

./compile-translations.sh

python3 asknot-ng.py \
	./templates/index.html \
	./questions/fedora.yml \
	./l10n/fedora/locale \
	--theme fedora
