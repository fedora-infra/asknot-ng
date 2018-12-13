FROM fedora:latest as builder

COPY . /code
WORKDIR /code

RUN dnf -y install gettext && dnf clean all && python3 setup.py install && ./build.sh

FROM registry.fedoraproject.org/fedora-minimal:latest

RUN microdnf -y install httpd && microdnf clean all

WORKDIR /var/www/html
COPY --from=builder /code/build .
EXPOSE 80
CMD ["httpd", "-DFOREGROUND"]
