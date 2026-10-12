# syntax=docker/dockerfile:1
FROM ubuntu:20.04 AS builder
ARG DEBIAN_FRONTEND=noninteractive
ARG BUILD_JOBS=4
ENV LC_ALL=C
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates git build-essential gfortran cmake ninja-build xxd python3 \
    zlib1g-dev libtiff-dev libinsighttoolkit4-dev libcrypt-dev binutils \
    && rm -rf /var/lib/apt/lists/*
# Fetch only source directories used by this target, at the identified revision.
RUN git init /build/fs && git -C /build/fs remote add origin https://github.com/freesurfer/freesurfer.git \
    && git -C /build/fs -c protocol.version=2 fetch --depth=1 origin 80ec14cb8c3ce78d700d269e942c55ccaa09b343 \
    && git -C /build/fs sparse-checkout init --cone \
    && git -C /build/fs sparse-checkout set include utils cmake packages mris_make_surfaces resurf \
    && git -C /build/fs checkout --detach FETCH_HEAD \
    && test "$(git -C /build/fs rev-parse HEAD)" = 80ec14cb8c3ce78d700d269e942c55ccaa09b343
COPY purple-pial.patch /build/purple-pial.patch
RUN git -C /build/fs apply --check /build/purple-pial.patch \
    && git -C /build/fs apply /build/purple-pial.patch \
    && test "$(git -C /build/fs hash-object mris_make_surfaces/mris_place_surface.cpp)" = 95236b5d7cd99364f88541769a152f2ae5ca8766 \
    && test "$(git -C /build/fs hash-object mris_make_surfaces/mris_place_surface.help.xml)" = 009a0439ce6839693e7cbfafb4050967e9c156c4
COPY PialOnly.cmake /build/fs/CMakeLists.txt
RUN cmake -S /build/fs -B /build/obj -G Ninja -DCMAKE_BUILD_TYPE=Release \
    && cmake --build /build/obj --target mris_place_surface --parallel "${BUILD_JOBS}"
COPY collect_runtime.py /build/collect_runtime.py
COPY validate.sh run-pial.sh /build/
RUN python3 /build/collect_runtime.py /build/obj/mris_place_surface /opt/purple_pial \
    && install -m 755 /build/run-pial.sh /opt/purple_pial/run-pial.sh \
    && mkdir -p /opt/purple_pial/reports \
    && dpkg-query -W > /opt/purple_pial/reports/build-packages.tsv \
    && cp /build/obj/CMakeCache.txt /opt/purple_pial/reports/CMakeCache.txt \
    && cp /build/purple-pial.patch /opt/purple_pial/reports/ \
    && cp /build/fs/LICENSE.txt /opt/purple_pial/reports/FreeSurfer-LICENSE \
    && printf '%s\n' 80ec14cb8c3ce78d700d269e942c55ccaa09b343 > /opt/purple_pial/reports/source-commit.txt
# Validate again in a clean focal runtime, without any compiler/development packages.
FROM ubuntu:20.04 AS runtime
ENV LC_ALL=C
RUN apt-get update && apt-get install -y --no-install-recommends binutils \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/purple_pial /opt/purple_pial
COPY validate.sh /usr/local/bin/validate-purple-pial
RUN chmod +x /usr/local/bin/validate-purple-pial \
    && /usr/local/bin/validate-purple-pial /opt/purple_pial
WORKDIR /data
ENTRYPOINT ["/opt/purple_pial/run-pial.sh"]
CMD ["--help"]
