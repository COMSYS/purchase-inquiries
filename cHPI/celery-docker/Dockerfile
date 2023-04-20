FROM python:3
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1
ENV PYTHONPATH /
RUN apt-get update -qq && \
apt-get install -y --no-install-recommends \
libmpc-dev \
libgmp-dev \
libmpfr-dev


WORKDIR /

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade memprof
RUN rm requirements.txt

COPY . /
WORKDIR /app

#tiangolo flask docker