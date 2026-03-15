#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Date     : 20260315
# Author   : tao.wang
# Usage    :
# Version  : 1.0
# Comment  :

from .nodes.image_nodes import ImageBrightnessNode, ImageInvertNode


# Key   → ComfyUI 内部唯一标识符（不能重复）
# Value → 对应的 Python 类
NODE_CLASS_MAPPINGS = {
    "ImageBrightnessNode": ImageBrightnessNode,
    "ImageInvertNode":     ImageInvertNode,
}


# Key   → 与 NODE_CLASS_MAPPINGS 的 Key 保持一致
# Value → 显示在 ComfyUI UI 界面上的名称（可含中文/空格）
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageBrightnessNode": "🎨 图像亮度调整",
    "ImageInvertNode":     "🔄 图像颜色反转",
}




__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
