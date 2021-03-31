ARG FUNCTION_DIR="/var/task"

FROM ubuntu:20.04 as build-image

ARG FUNCTION_DIR
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    apt-utils \
    g++ \
    make \
    cmake \
    unzip \
    python3 \
    python3-pip \
    libcurl4-openssl-dev

RUN mkdir -p ${FUNCTION_DIR}

WORKDIR ${FUNCTION_DIR}

RUN pip3 install -U pip

RUN pip3 install awslambdaric

COPY requirements.txt ${FUNCTION_DIR}
RUN pip3 install -r requirements.txt

COPY src/ ${FUNCTION_DIR}/src

ENTRYPOINT ["/usr/bin/python3", "-m", "awslambdaric"]
CMD ["src.main.handler"]