# FROM python:3.8-slim

# WORKDIR /usr/app

# RUN DEBIAN_FRONTEND=noninteractive pip3 install --upgrade pip && \
#     pip3 install --no-cache-dir \
#     torch==1.10.0 \
#     torchvision==0.11.1 \
#     -f https://download.pytorch.org/whl/torch_stable.html

FROM nvidia/cuda:10.2-runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    git \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools

RUN pip3 -q install pip --upgrade
COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN (tmp_dir=/tmp/aws && mkdir $tmp_dir && cd $tmp_dir && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip "awscliv2.zip" && ./aws/install)
RUN aws --version

ARG AWS_ACCESS_KEY_ID_DATASETS
ARG AWS_SECRET_ACCESS_KEY_DATASETS
RUN aws configure set aws_access_key_id ${AWS_ACCESS_KEY_ID_DATASETS}
RUN aws configure set aws_secret_access_key ${AWS_SECRET_ACCESS_KEY_DATASETS}

ARG AWS_ACCOUNT_ID
ARG S3_PREFIX=s3://${AWS_ACCOUNT_ID}-datasets/davis-2017
ARG DIR_DAVIS_2017="data/davis-2017"
RUN aws s3 cp --recursive ${S3_PREFIX}/Annotations/480p/bear \
    ${DIR_DAVIS_2017}/masks/bear
RUN aws s3 cp --recursive ${S3_PREFIX}/JPEGImages/480p/bear \
    ${DIR_DAVIS_2017}/images/bear

# COPY data/davis-2017/ ./data/davis-2017/

COPY unet ./unet
COPY run_exp.py .