#!/usr/bin/env bash

set -Eeuxo pipefail


wandb login
# wandb agent $1 --count 10
echo $1
