import math
from typing import Union, Tuple, TypeVar

import torch


def trim_from(smaller, larger):
    # TODO: Assert smaller is smaller
    _, _, h_s, w_s = smaller.shape
    _, _, h_l, w_l = larger.shape
    pad_h = (h_l - h_s) / 2
    pad_w = (w_l - w_s) / 2
    return larger[
        :, :,
        math.floor(pad_h):h_l - math.ceil(pad_h),
        math.floor(pad_w):w_l - math.ceil(pad_w)
    ]


def min_required_shape_maxpool(h_w, kernel_size, stride, pad=0, dilation=1):
    h_w = tuplefy(h_w)
    kernel_size = tuplefy(kernel_size)
    stride = tuplefy(stride)
    pad = tuplefy(pad)
    dilation = tuplefy(dilation)
    return tuple(
        (h_w[i] - 1) * stride[i] + 1 - 2*pad[i] + dilation[i] * (kernel_size[i] - 1)
        for i in range(2)
    )


def output_shape_maxpool(h_w, kernel_size, stride, pad=0, dilation=1):
    h_w = tuplefy(h_w)
    kernel_size = tuplefy(kernel_size)
    stride = tuplefy(stride)
    pad = tuplefy(pad)
    dilation = tuplefy(dilation)

    return tuple(
        (h_w[i] + 2 * pad[i] - dilation[i] * (kernel_size[i] - 1) - 1) // stride[i] + 1
        for i in range(2)
    )


def min_required_shape_upsample(h_w, scale_factor) -> Tuple[int, int]:
    return tuple(
        h_w[i] // scale_factor for i in range(2)
    )


def output_shape_upsample(h_w, scale_factor) -> Tuple[int, int]:
    return tuple(scale_factor * h_w[i] for i in range(2))


T = TypeVar("T")
ScalarOrDuple = Union[T, Tuple[T, T]]

def tuplefy(x: ScalarOrDuple[int]) -> Tuple[int, int]:
    if not isinstance(x, tuple):
        return (x, x)
    return x


def min_required_shape_conv(hw_out, kernel_size, stride=1, pad=0, dilation=1):
    hw_out = tuplefy(hw_out)
    kernel_size = tuplefy(kernel_size)
    stride = tuplefy(stride)
    pad = tuplefy(pad)
    dilation = tuplefy(dilation)

    def _min_required_shape_conv(hw_out, kernel_size, stride, pad, dilation):
        res = (hw_out - 1)*stride + 1 + dilation*(kernel_size - 1) - 2*pad
        return res + (res % 2)

    return tuple(
        _min_required_shape_conv(hw_out[i], kernel_size[i], stride[i], pad[i], dilation[i])
        for i in range(2)
    )


def output_shape_conv(
    h_w: ScalarOrDuple[int],
    kernel_size: ScalarOrDuple[int] = 1,
    stride: ScalarOrDuple[int] = 1,
    pad: ScalarOrDuple[int] = 0,
    dilation: int = 1
):
    """
    Utility function for computing output of convolutions
    takes a tuple of (h,w) and returns a tuple of (h,w)
    """
    h_w = tuplefy(h_w)
    kernel_size = tuplefy(kernel_size)
    stride = tuplefy(stride)
    pad = tuplefy(pad)

    h = (h_w[0] + (2 * pad[0]) - (dilation * (kernel_size[0] - 1)) - 1) // stride[0] + 1
    w = (h_w[1] + (2 * pad[1]) - (dilation * (kernel_size[1] - 1)) - 1) // stride[1] + 1

    return h, w


def _pad_with_reflection(image: torch.Tensor, pad: Tuple[int, int]):
    _, h, w = image.size()
    (pad_x, pad_y) = pad
    if abs(pad_x) >= h or abs(pad_y) >= w:
        raise Exception("Reflection target cannot exceed image size")

    x_0 = 0 if pad_x > 0 else w + pad_x
    x_1 = pad_x if pad_x > 0 else w
    y_0 = 0 if pad_y > 0 else h + pad_y
    y_1 = pad_y if pad_y > 0 else h

    reflection_in_y = torch.flip(image[:, y_0:y_1, :], dims=[1])
    filled_in_y = torch.concat(
        [image, reflection_in_y] if pad_y < 0 else [reflection_in_y, image],
        dim=1
    )
    reflection_in_x = torch.flip(filled_in_y[:, :, x_0:x_1], dims=[2])
    return torch.concat(
        [reflection_in_x, filled_in_y] if pad_x > 0 else [filled_in_y, reflection_in_x],
        dim=2
    )


def pad_with_reflection(
    X: torch.Tensor, pad: Tuple[int, int]
) -> torch.Tensor:
    (pad_h, pad_w) = tuplefy(pad)
    return _pad_with_reflection(
        _pad_with_reflection(X, (pad_w, pad_h)),
        (-pad_w, -pad_h)
    )
