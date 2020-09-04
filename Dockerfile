FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN flask db init
RUN flask db migrate
RUN flask db upgrade

CMD flask run --host 0.0.0.0
EXPOSE 5000
