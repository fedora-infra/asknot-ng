FROM fedora:latest as builder

COPY . /code
WORKDIR /code

RUN dnf -y install gettext python3-setuptools python3-pyyaml python3-mako python3-babel python3-pygraphviz && dnf clean all && python3 setup.py install && ./build.sh

FROM fedora:latest

COPY --from=builder /code/build /var/www/html/
COPY container/favicon.ico /var/www/html/static/image/favicon.ico
COPY container/whatcanidoforfedora-web.conf /etc/httpd/conf/httpd.conf
RUN dnf -y install httpd && dnf clean all\
    && chown apache:0 /etc/httpd/conf/httpd.conf \
    && chmod g+r /etc/httpd/conf/httpd.conf \
    && chown apache:0 /var/log/httpd  \
    && chmod g+rwX /var/log/httpd \
    && chown apache:0 /var/run/httpd \
    && chmod g+rwX /var/run/httpd\
    && chown -R apache:0 /var/www/html \
    && chmod -R g+rwX /var/www/html
EXPOSE 8080
USER apache
ADD container/container-entrypoint.sh /srv
ENTRYPOINT ["bash", "/srv/container-entrypoint.sh"]
