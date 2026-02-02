FROM nvidia/cuda:11.8.0-runtime-ubuntu20.04
ARG DEBIAN_FRONTEND=noninteractive

RUN rm /etc/apt/sources.list.d/cuda.list
RUN apt update \
    && apt install -y python3.8 wget git ffmpeg libsm6 libxext6

RUN apt install -y python3-pip
RUN python3.8 -m pip install --upgrade pip
RUN pip3 install virtualenv setuptools wheel
RUN virtualenv -p python3.8 ml
RUN mkdir -p /data/exvivo

COPY ./commands_nnunet_inference.sh src/
COPY ./requirements.txt src/

RUN /bin/bash -c "cd src \
    && source /ml/bin/activate \
    && pip3 install -r requirements.txt --use-pep517"

COPY sitecustomize.py /usr/lib/python3.8/sitecustomize.py
COPY ./network_architecture/* /ml/src/nnunet/nnunet/network_architecture/
COPY ./network_trainer/* /ml/src/nnunet/nnunet/training/network_training/
COPY ./nnunet_paths_that_it_requires/ /src/nnunet_paths_that_it_requires/
