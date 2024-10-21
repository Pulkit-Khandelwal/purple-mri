FROM nvidia/cuda:11.8.0-runtime-ubuntu20.04
ARG DEBIAN_FRONTEND=noninteractive

RUN apt update \
    && apt install -y htop python3.8 wget git ffmpeg libsm6 libxext6

RUN apt install -y python3-setuptools python3-pip python3-venv

RUN python3 -m pip install --upgrade pip
RUN pip3 install virtualenv
RUN virtualenv -p python3 ml
RUN mkdir -p /data/exvivo

COPY . src/

RUN /bin/bash -c "cd src \
    && source /ml/bin/activate \
    && pip3 install -r requirements.txt"

COPY ./network_architecture/* /ml/src/nnunet/nnunet/network_architecture/
COPY ./network_trainer/* /ml/src/nnunet/nnunet/training/network_training/