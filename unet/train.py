import os

import torch
from torch import nn
import wandb

from unet.utils import trim_from
from unet.config import BATCH_SIZE


def train_loop(dataloader, model: nn.Module, loss_fn, optimizer):
    for (i_batch, (X, y)) in enumerate(dataloader):
        _pred = model(X)
        pred = trim_from(y, _pred)
        loss = loss_fn(pred, y.to(torch.long).squeeze(1))

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        n = (i_batch + 1) * BATCH_SIZE
        if n % 10 == 0:
            loss_num = loss.item()
            if os.environ.get("EXP_WANDB_DO_LOG") == "true":
                wandb.log(data={"train_loss": loss_num})
            print(f"loss: {loss_num:>7f}  [{n:>5d}/{len(dataloader.dataset)}]")
