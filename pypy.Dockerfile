FROM pypy:3-slim-buster AS base

# Image to Build Dependencies
FROM base AS builder

WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app

# Build Dependencies
RUN apt-get update \
    && apt-get install -yq build-essential libssl-dev libffi-dev libxml2-dev libxslt-dev zlib1g-dev curl \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*

# install rust toolchain
RUN curl https://sh.rustup.rs -sSf | \
    sh -s -- --default-toolchain stable -y

ENV PATH=/root/.cargo/bin:$PATH

# Python Dependencies
RUN pip install --no-warn-script-location --ignore-installed --no-cache-dir --prefix=/install wheel cryptography gunicorn pymysql
RUN pip install --no-warn-script-location --ignore-installed --no-cache-dir --prefix=/install -r requirements.txt

# Runtime Environment Image
FROM base

WORKDIR /usr/src/app

COPY --from=builder /install/bin /usr/local/bin
COPY --from=builder /install/site-packages /opt/pypy/site-packages

RUN apt-get update && apt-get install -y \
    libxml2 libxslt1.1 \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*

COPY . .

RUN flask db init

CMD flask db stamp head \
    && flask db migrate \
    && flask db upgrade \
    && gunicorn -b 0.0.0.0:5000 -k gevent -w 4 yotter:app

EXPOSE 5000
