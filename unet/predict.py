from os import path

import torch
import torchvision


def predict(model, dataset):
    target_dir = path.join(
        path.expanduser("~"),
        "Projects/pytorch-playground/data/results/semseg/bear"
    )
    with torch.no_grad():
        for (i, (X, y)) in enumerate(dataset):
            pred = model(X.unsqueeze(0)).argmax(1).to(torch.uint8)
            torchvision.io.write_png(pred, path.join(target_dir, f"{i}.png"))
