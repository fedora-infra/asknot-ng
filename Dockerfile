FROM python:3 AS builder

WORKDIR /code

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN ./build.sh

FROM httpd:2.4

COPY --from=builder /code/build /usr/local/apache2/htdocs/
COPY --from=builder /code/container/l10n.conf /usr/local/apache2/conf/l10n.conf
COPY container/favicon.xpm /usr/local/apache2/htdocs/static/image/favicon.xpm
COPY container/whatcanidoforfedora-web.conf /usr/local/apache2/conf/httpd.conf
