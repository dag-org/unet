FROM nvidia/cuda:10.2-runtime

WORKDIR /usr/app

ENV LANG=C.UTF-8
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update && apt -y upgrade && apt install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt install -y \
    iputils-ping \
    curl \
    unzip \
    git \
    build-essential \
    python3.9 python3.9-dev python3.9-venv
RUN update-ca-certificates


RUN apt install -y python3-pip
RUN python3.9 -m ensurepip --default-pip --user
RUN python3.9 -m pip install --upgrade pip --user

RUN python3.9 -m pip install --upgrade pip setuptools
RUN python3.9 -m pip install torch==1.10.0+cu102 \
    -f https://download.pytorch.org/whl/torch_stable.html
COPY requirements.txt .
RUN python3.9 -m pip install -r requirements.txt


RUN (tmp_dir=/tmp/aws && mkdir $tmp_dir && cd $tmp_dir && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip "awscliv2.zip" && ./aws/install)
RUN aws --version

ARG S3_PREFIX=s3://510666016636-datasets/davis-2017
ARG DIR_DAVIS_2017="data/davis-2017"
RUN aws s3 cp ${S3_PREFIX}/Annotations/480p/bear ${DIR_DAVIS_2017}/masks/bear \
    --recursive --no-sign-request
RUN aws s3 cp ${S3_PREFIX}/JPEGImages/480p/bear ${DIR_DAVIS_2017}/images/bear \
    --recursive --no-sign-request


COPY unet ./unet
COPY exp ./exp
COPY run_exp.py .
