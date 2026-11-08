# SPDX-License-Identifier: GPL-3.0-or-later
"""comfyui-haywire: placeholder nodes and a workflow exchange for haywire's ComfyUI Workflow node."""

if __package__:  # loaded by ComfyUI as custom_nodes/<dir>; pytest imports this file bare
    from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
    from .routes import register

    register()

    WEB_DIRECTORY = "./web"

    __all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
