FROM python:3-alpine

WORKDIR /usr/src/app

RUN apk --no-cache add gcc musl-dev libffi-dev openssl-dev libxml2-dev libxslt-dev file llvm-dev make g++

COPY requirements.txt ./

RUN pip install --no-cache-dir wheel cryptography gunicorn pymysql
RUN pip install --no-cache-dir -r requirements.txt

RUN apk del gcc musl-dev libffi-dev openssl-dev file llvm-dev make g++

COPY . .

RUN flask db init \
  && flask db migrate \
  && flask db upgrade

CMD flask db upgrade \
  && gunicorn -b 0.0.0.0:5000 -w 4 yotter:app

EXPOSE 5000
