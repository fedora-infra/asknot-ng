FROM fedora:latest as builder

COPY . /code
WORKDIR /code

RUN dnf -y install gettext && dnf clean all && python3 setup.py install && ./build.sh

FROM fedora:latest

COPY --from=builder /code/build /var/www/html
RUN dnf -y install httpd && dnf clean all\
    && sed -i 's/Listen 80/Listen 8080/' /etc/httpd/conf/httpd.conf\
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
ADD container-entrypoint.sh /srv
ENTRYPOINT ["bash", "/srv/container-entrypoint.sh"]
