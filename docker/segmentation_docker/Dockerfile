FROM nvidia/cuda:11.8.0-runtime-ubuntu20.04
ARG DEBIAN_FRONTEND=noninteractive

RUN rm /etc/apt/sources.list.d/cuda.list
RUN apt update \
    && apt install -y python3.8 wget git ffmpeg libsm6 libxext6

RUN apt install -y python3-pip
RUN python3.8 -m pip install --upgrade pip
RUN pip3 install virtualenv setuptools wheel
RUN virtualenv -p python3.8 /ml
RUN mkdir -p /data/exvivo /src

# Install dependencies before copying scripts so script edits reuse this layer.
COPY ./requirements.txt /src/requirements.txt
RUN /bin/bash -c "source /ml/bin/activate \
    && python -m pip install -r /src/requirements.txt --use-pep517"

COPY sitecustomize.py /usr/lib/python3.8/sitecustomize.py
COPY ./network_architecture/* /ml/src/nnunet/nnunet/network_architecture/
COPY ./network_trainer/* /ml/src/nnunet/nnunet/training/network_training/
COPY ./nnunet_paths_that_it_requires/ /src/nnunet_paths_that_it_requires/

COPY ./commands_nnunet_inference.sh /src/
COPY ./merge_exvivo.py /src/merge_exvivo.py
