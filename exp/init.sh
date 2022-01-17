#!/usr/bin/env bash

set -Eeuxo pipefail


wandb login --relogin $WANDB_API_KEY
EXP_WANDB_DO_LOG=true wandb agent davidgold/uncategorized/$1 --count 1
