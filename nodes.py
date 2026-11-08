# SPDX-License-Identifier: GPL-3.0-or-later
"""Haywire placeholder nodes.

In ComfyUI they run normally, so a workflow can be built and tried in ComfyUI's own page.
When haywire runs the workflow it replaces Parameters by values and Images by Load Images
holding its own pictures; Haywire Output sends every image to haywire over the websocket.
"""

from __future__ import annotations

import base64
import io
import time

import comfy.utils
import numpy as np
import torch
from PIL import Image

from .params import PARAMETER_TYPES, parse_value

CATEGORY = "haywire"


class HaywireParameter:
    """A value haywire sets: shown as an inlet on the ComfyUI Workflow node."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "name": ("STRING", {"default": "Parameter"}),
                "type": (list(PARAMETER_TYPES), {"default": "number"}),
                "default": ("STRING", {"default": ""}),
            },
            "optional": {
                "min": ("FLOAT", {"default": 0.0, "min": -1e12, "max": 1e12}),
                "max": ("FLOAT", {"default": 1.0, "min": -1e12, "max": 1e12}),
            },
        }

    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("value",)
    FUNCTION = "value"
    CATEGORY = CATEGORY

    def value(self, name, type, default, min=None, max=None):
        return (parse_value(type, default),)


class HaywireImage:
    """An image haywire sends: shown as an IMAGE inlet. In ComfyUI it passes `image` on."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"name": ("STRING", {"default": "Image"})},
            "optional": {"image": ("IMAGE",)},
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "image"
    CATEGORY = CATEGORY

    def image(self, name, image=None):
        if image is None:
            image = torch.full((1, 512, 512, 3), 0.5)
        return (image,)


class HaywireLoadImage:
    """Haywire puts this in place of a Haywire Image: `data` is a base64 PNG."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"data": ("STRING", {"default": ""})}}

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "load"
    CATEGORY = CATEGORY + "/internal"

    def load(self, data):
        img = Image.open(io.BytesIO(base64.b64decode(data)))
        rgba = np.asarray(img.convert("RGBA"), dtype=np.float32) / 255.0
        image = torch.from_numpy(rgba[..., :3].copy())[None]
        mask = 1.0 - torch.from_numpy(rgba[..., 3].copy())[None]
        return (image, mask)


class HaywireOutput:
    """Sends its images to haywire, which shows them on an outlet named `name`. Never cached."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"images": ("IMAGE",), "name": ("STRING", {"default": "Image"})}}

    RETURN_TYPES = ()
    FUNCTION = "send"
    OUTPUT_NODE = True
    CATEGORY = CATEGORY

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Always run: a cached output would replay its message without sending the images.
        return time.time()

    def send(self, images, name):
        count = images.shape[0]
        bar = comfy.utils.ProgressBar(count)
        for i, image in enumerate(images):
            pixels = np.clip(255.0 * image.cpu().numpy(), 0, 255).astype(np.uint8)
            bar.update_absolute(i, count, ("PNG", Image.fromarray(pixels), None))
        return {"ui": {"info": [{"name": name, "index": i} for i in range(count)]}}


NODE_CLASS_MAPPINGS = {
    "HaywireParameter": HaywireParameter,
    "HaywireImage": HaywireImage,
    "HaywireLoadImage": HaywireLoadImage,
    "HaywireOutput": HaywireOutput,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HaywireParameter": "Haywire Parameter",
    "HaywireImage": "Haywire Image",
    "HaywireLoadImage": "Haywire Load Image (internal)",
    "HaywireOutput": "Haywire Output",
}
