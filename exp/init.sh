#!/usr/bin/env bash

set -Eeuxo pipefail


echo "Starting sweep agent task..."

wandb login $1

EXP_WANDB_DO_LOG=true wandb agent davidgold/uncategorized/$2 --count 1
