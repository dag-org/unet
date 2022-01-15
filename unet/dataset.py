import os
from os import path
import torch
import torchvision as tv

from semseg import utils


class BearDataset(torch.utils.data.IterableDataset):
    def __init__(self, model: torch.nn.Module):
        super(BearDataset).__init__()
        base_dir = path.join(
            path.expanduser("~"),
            "Projects/pytorch-playground/data/davis/", 
        )
        self.image_dir = path.join(base_dir, "JPEGImages/480p/bear")
        self.mask_dir = path.join(base_dir, "Annotations/480p/bear")
        filenames = [
            f for f in os.listdir(self.image_dir)
            if path.isfile(path.join(self.image_dir, f))
        ]
        self.n_images = len(filenames)

        x = tv.io.read_image(path.join(self.image_dir, "00000.jpg"))
        (_, h_0, w_0) = x.shape
        (h, w) = utils.min_required_shape((h_0, w_0), model)
        dim_max = max(h, w)
        self.pad_h = (dim_max - h_0) // 2
        self.pad_w = (dim_max - w_0) // 2
        

    def __len__(self):
        return self.n_images

    def __getitem__(self, i):
        f = str(i).rjust(5, "0")
        return (
            utils.pad_with_reflection(
                tv.io.read_image(path.join(self.image_dir, f) + ".jpg") / 255,
                (self.pad_h, self.pad_w)
            ),
            tv.io.read_image(path.join(self.mask_dir, f) + ".png").long()
        )

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i == len(self) - 1:
            raise StopIteration

        self.i += 1
        return self.__getitem__(self.i)
