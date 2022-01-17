#!/usr/bin/env bash

set -Eeuxo pipefail


wandb login --relogin
EXP_WANDB_DO_LOG=true wandb agent davidgold/uncategorized/$1 --count 1
