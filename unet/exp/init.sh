#!/usr/bin/env bash

set -Eeuxo pipefail

echo $WANDB_API_KEY
wandb login
EXP_WANDB_DO_LOG=true wandb agent davidgold/uncategorized/$1 --count 1
