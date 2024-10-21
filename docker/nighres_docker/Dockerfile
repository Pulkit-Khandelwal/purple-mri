FROM ubuntu:20.04

RUN apt update
RUN apt install -y openjdk-8-jdk

RUN apt install -y python3.8 wget git python3-setuptools python3-pip python3-venv
RUN python3 -m pip install --upgrade pip

RUN export JCC_JDK=/usr/lib/jvm/java-8-openjdk-amd64 && python3 -m pip install jcc
RUN ln -s /usr/bin/javac /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/javac

RUN git clone https://github.com/nighres/nighres
RUN cd nighres && ./build.sh
RUN cd nighres && python3 -m pip install .

RUN mkdir -p /data/cruise_files

COPY c3d /data
COPY prepare_cruise_files.sh /data
COPY nighres_topology_corection.py /data

RUN chmod +x data/c3d
