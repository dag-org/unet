import torch
from torch import nn

from semseg.utils import trim_from
from semseg.config import LEARNING_RATE, BATCH_SIZE, MOMENTUM


def train_loop(dataloader, model: nn.Module, loss_fn, optimizer):
    for (i_batch, (X, y)) in enumerate(dataloader):
        if len(X) % BATCH_SIZE > 0:
            return
        _pred = model(X)
        pred = trim_from(y, _pred)
        loss = loss_fn(pred, y.to(torch.long).squeeze(1))

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        n = (i_batch + 1) * BATCH_SIZE
        if n % 10 == 0:
            print(f"loss: {loss.item():>7f}  [{n:>5d}/{len(dataloader.dataset)}]")
