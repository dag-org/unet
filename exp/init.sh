#!/usr/bin/env bash

set -Eeuxo pipefail


echo "Starting sweep agent task..."

wandb login

EXP_WANDB_DO_LOG=true wandb agent davidgold/uncategorized/$1 --count $2
