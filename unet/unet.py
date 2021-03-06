from math import prod, sqrt
from typing import Tuple

import torch
from torch import nn
from unet import utils


def conv_seq(c_high: int, c_low: int, down: bool = True):
    return nn.Sequential(
        nn.Conv2d(*([c_low, c_high] if down else [c_high, c_low]), 3),
        nn.ReLU(),
        nn.Conv2d(*([c_high]*2 if down else [c_low]*2), 3),
        nn.ReLU()
    )


def layer(c, depth, down=True, max_depth=3, n_channel_base=3):
    depth = depth if down else max_depth - depth
    c_high = (2 ** depth) * c
    c_low = int(
        (n_channel_base if down else c) if depth == 0
        else c_high / 2
    )

    conv = conv_seq(c_high, c_low, down=down)
    if down:
        return nn.ModuleDict({
            "conv": conv,
            "maxpool": nn.MaxPool2d(2, 2)
        })
    return nn.ModuleDict({
        "upconv": nn.Sequential(
            nn.Upsample(scale_factor=2),
            nn.Conv2d(c_high, c_low, 2, padding="same")
        ),
        "conv": conv
    })


class UNet(nn.Module):
    def __init__(self, n_channel=8, max_depth=4):
        super(UNet, self).__init__()
        self.max_depth = max_depth
        max_channels = (2 ** max_depth) * n_channel

        self.down = nn.ModuleList([
            layer(n_channel, d, down=True)
            for d in range(0, max_depth)
        ])
        self.bottom = conv_seq(max_channels, int(max_channels / 2), 3)
        self.up = nn.ModuleList([
            layer(n_channel, d, down=False, max_depth=max_depth)
            for d in range(0, max_depth)
        ])
        self.final = nn.Conv2d(n_channel, 2, 1)
        self.reset_weights()

    def forward(self, x):
        to_concat = []
        for d in range(self.max_depth):
            x = self.down[d].conv(x)
            to_concat.append(x)
            x = self.down[d].maxpool(x)

        x = self.bottom(x)

        for d in range(self.max_depth):
            x = self.up[d].upconv(x)
            x = self.up[d].conv(torch.concat(
                [utils.trim_from(x, to_concat.pop()), x], dim=1
            ))

        return self.final(x)

    def reset_weights(self):
        for layer in self.down:
            for i in (0, 2):    # Conv2d layers
                N = layer.conv[i].in_channels * prod(layer.conv[i].kernel_size)
                layer.conv[i].weight.data.normal_(0, sqrt(2 / N))

        for i in (0, 2):
            N = self.bottom[i].in_channels * prod(self.bottom[i].kernel_size)
            self.bottom[i].weight.data.normal_(0, sqrt(2 / N))

        for layer in self.up:
            for i in (0, 2):    # Conv2d layers
                N = layer.conv[i].in_channels * prod(layer.conv[i].kernel_size)
                layer.conv[i].weight.data.normal_(0, sqrt(2 / N))

        # self.final.weight.data.normal_(0, sqrt(2/self.final.))

    def min_required_shape(self, h_w) -> Tuple[int, int]:
        for _ in self.up:
            for _ in range(2):
                h_w = utils.min_required_shape_conv(h_w, 3)
            h_w = utils.min_required_shape_upsample(h_w, scale_factor=2)

        for _ in range(2):
            h_w = utils.min_required_shape_conv(h_w, 3)

        for _ in self.down:
            h_w = utils.min_required_shape_maxpool(h_w, kernel_size=2, stride=2)
            for _ in range(2):
                h_w = utils.min_required_shape_conv(h_w, 3)

        return h_w

    def output_shape(self, h_w) -> Tuple[int, int]:
        for _ in range(len(self.down)):
            for _ in range(2):
                h_w = utils.output_shape_conv(h_w, 3)

            h_w = utils.output_shape_maxpool(h_w, kernel_size=2, stride=2)

        for _ in range(2):
            h_w = utils.output_shape_conv(h_w, 3)

        for _ in range(len(self.up)):
            h_w = utils.output_shape_upsample(h_w, scale_factor=2)
            for _ in range(2):
                h_w = utils.output_shape_conv(h_w, 3)

        return h_w
