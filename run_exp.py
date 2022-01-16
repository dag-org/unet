from typing import Dict

import torch
import wandb

from unet import unet, dataset, train
from unet.config import BATCH_SIZE


device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")

wandb.init()
config: Dict = wandb.config

model = unet.UNet().to(device)

bear = dataset.BearDataset(model)
dataloader = torch.utils.data.DataLoader(bear, batch_size=BATCH_SIZE)

optimizer = torch.optim.SGD(
    model.parameters(), lr=config["learning_rate"], momentum=config["momentum"]
)
loss_fn = torch.nn.CrossEntropyLoss()


# for t in range(1):
for t in range(config["n_epochs"]):
    print(f"Epoch {t+1}\n-------------------------------")
    train.train_loop(dataloader, model, loss_fn, optimizer)
