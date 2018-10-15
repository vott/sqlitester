FROM selenium/standalone-firefox

USER root
RUN apt-get update && apt-get install -y \
    python3-pip
RUN mkdir -p /var/src/app
RUN mkdir -p /var/log
WORKDIR /var/src/app
COPY ./requirements.txt .

RUN chown seluser /var/src/app
RUN chown seluser /var/log
USER seluser
RUN pip3 install -r requirements.txt
RUN python3 -m pip install motor


ENV PYTHONUNBUFFERED 1

COPY . .
