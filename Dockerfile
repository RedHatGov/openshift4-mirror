FROM registry.access.redhat.com/ubi8/ubi:8.2

ENV PYCURL_SSL_LIBRARY=openssl

ENV LC_CTYPE=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

LABEL \
    name="openshift4-mirror" \
    description="Utility for mirroring OpenShift 4 content" \
    maintainer="RedHat4Gov Team"

USER root

RUN \
    yum install -y \
        python3 \
        python3-pip \
        vim \
        which \
    && yum clean all \
    && pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir pipenv==2018.11.26 \
    && echo 'export PS1="\n\[\e[34m\]\u\[\e[m\] at \[\e[32m\]\h\[\e[m\] in \[\e[33m\]\w\[\e[m\] \[\e[31m\]\n\\$\[\e[m\] "' >> /root/.bashrc \
    && mkdir -p /app/app

COPY app/* /app/app/

# Install Python dependencies
WORKDIR /app
COPY Pipfile Pipfile.lock entrypoint.sh openshift_mirror ./
RUN pipenv install --system --deploy

ENTRYPOINT ["/app/entrypoint.sh"]
