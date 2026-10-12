# syntax=docker/dockerfile:1
ARG PIAL_BASE_IMAGE=purple-pial:ubuntu20-test
FROM ${PIAL_BASE_IMAGE} AS pial_runtime

FROM ubuntu:20.04 AS surface_resources
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates wget python3 \
    && rm -rf /var/lib/apt/lists/*
ARG FREESURFER_URL=https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.4.0/freesurfer-linux-ubuntu20_amd64-7.4.0.tar.gz
RUN wget --https-only --tries=3 \
      -O /tmp/freesurfer.tar.gz "$FREESURFER_URL" \
    && echo "301bf34eb65532aa8824da48cc13c956  /tmp/freesurfer.tar.gz" | md5sum -c - \
    && mkdir -p /opt \
    && tar -xzf /tmp/freesurfer.tar.gz -C /opt \
    && rm /tmp/freesurfer.tar.gz \
    && test -x /opt/freesurfer/bin/mris_place_surface \
    && test -f /opt/freesurfer/subjects/fsaverage/surf/lh.sphere.reg
ARG C3D_URL=https://downloads.sourceforge.net/project/c3d/c3d/1.0.0/c3d-1.0.0-Linux-x86_64.tar.gz
RUN wget --tries=3 -O /tmp/c3d.tar.gz "$C3D_URL" \
    && echo "2e0551fddb8a9306800f780a08d80873b955536ec65959fa1123ea473e12d77b  /tmp/c3d.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/c3d \
    && tar -xzf /tmp/c3d.tar.gz -C /opt/c3d --strip-components=1 \
    && rm /tmp/c3d.tar.gz \
    && test -x /opt/c3d/bin/c3d
COPY fetch_surface_resources.py resource_manifest.json /tmp/resources/
RUN python3 /tmp/resources/fetch_surface_resources.py /tmp/resources/resource_manifest.json /opt/purple-mri


FROM nvidia/cuda:11.8.0-runtime-ubuntu20.04 AS dl
ARG DEBIAN_FRONTEND=noninteractive
RUN rm -f /etc/apt/sources.list.d/cuda.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends python3.8 python3-pip python3-venv \
       wget git ffmpeg libsm6 libxext6 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN python3.8 -m pip install --upgrade pip \
    && pip3 install virtualenv setuptools wheel \
    && virtualenv -p python3.8 /ml \
    && mkdir -p /data/exvivo /src
COPY requirements.txt /src/requirements.txt
RUN /ml/bin/python -m pip install -r /src/requirements.txt --use-pep517
COPY sitecustomize.py /usr/lib/python3.8/sitecustomize.py
COPY network_architecture/*.py /ml/src/nnunet/nnunet/network_architecture/
COPY network_trainer/*.py /ml/src/nnunet/nnunet/training/network_training/

FROM dl AS runtime
USER root
ARG DEBIAN_FRONTEND=noninteractive
# Remove the retired CUDA apt repository; CUDA itself remains in the base image.
RUN rm -f /etc/apt/sources.list.d/cuda.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       python3-venv tcsh bc perl ca-certificates tcl tk \
       libgomp1 libstdc++6 libgcc-s1 libcrypt1 libgfortran5 libquadmath0 \
       libjpeg62 libtiff5 libgsl23 libfftw3-double3 libopenblas0 \
       libglu1-mesa libgl1 libsm6 libice6 libxext6 libxrender1 libxt6 libxmu6 \
       libxm4 libxpm4 libxft2 libxss1 libstdc++5 libgslcblas0 libpng16-16 \
       libx11-6 libxfixes3 libxi6 libxkbcommon0 libxkbcommon-x11-0 libxcb-xinerama0 \
       libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 \
       libfontconfig1 libfreetype6 libnss3 zlib1g \
    && rm -rf /var/lib/apt/lists/*
# Isolate mesh dependencies from the existing DL environment and its version pins.
COPY surface_requirements.txt /src/surface_requirements.txt
RUN python3.8 -m venv /surface_env \
    && /surface_env/bin/python -m pip install --no-cache-dir pip==25.0.1 \
    && /surface_env/bin/python -m pip install --no-cache-dir -r /src/surface_requirements.txt
COPY --from=surface_resources /opt/freesurfer/ /opt/freesurfer/
COPY --from=surface_resources /opt/c3d/ /opt/c3d/
COPY --from=surface_resources /opt/purple-mri/ /opt/purple-mri/
# Pial is compiled from source by pial/build.sh.
COPY --from=pial_runtime /opt/purple_pial/ /opt/purple_pial/
ENV FREESURFER_HOME=/opt/freesurfer \
    FS_LICENSE=/opt/freesurfer/license.txt \
    EXVIVO_THREADS=8 \
    NO_FSFAST=1 \
    QT_QPA_PLATFORM=offscreen
COPY surface/ /opt/purple-mri/purple_mri/
COPY merge_exvivo.py /src/merge_exvivo.py
COPY commands_nnunet_inference.sh run_exvivo_surface.sh surface_inputs.py exvivo_timing.sh /src/
RUN chmod +x /src/commands_nnunet_inference.sh /src/run_exvivo_surface.sh \
      /opt/purple_pial/run-pial.sh /opt/purple_pial/bin/mris_place_surface \
    && test -f /src/merge_exvivo.py \
    && test -f /opt/purple-mri/purple_mri/autodet.gw.stats.binary.dat \
    && /surface_env/bin/python -c "import numpy, nibabel, vtk, pymeshlab; assert 'meshing_decimation_quadric_edge_collapse' in pymeshlab.filter_list()"
COPY assets/nnunet_paths_that_it_requires/ /src/nnunet_paths_that_it_requires/
WORKDIR /data/exvivo
# Keep compatibility with existing commands that explicitly invoke /bin/bash.
ENTRYPOINT []
CMD ["/bin/bash", "/src/commands_nnunet_inference.sh", "--help"]
