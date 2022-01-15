FROM python:3.8-slim

WORKDIR /usr/app

RUN DEBIAN_FRONTEND=noninteractive apt-get update
    # apt install -y git curl build-essential binutils

RUN DEBIAN_FRONTEND=noninteractive pip3 install --upgrade pip && \
    pip3 install --no-cache-dir \
    torch==1.10.0 \
    torchvision==0.11.1 \
    -f https://download.pytorch.org/whl/torch_stable.html

RUN pip3 --no-cache-dir install --upgrade awscli
RUN pip3 install wandb

COPY init.sh .
CMD [ "/bin/bash", "init.sh" ]
