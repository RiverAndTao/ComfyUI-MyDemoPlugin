#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Date     : ${DATE} ${TIME}
# Author   : tao.wang
# Usage    : 拖入后点击执行
# Version  :
# Comment  : 亮度节点,颜色反转节点


import torch


# 节点一：图像亮度 & 对比度调整
class ImageBrightnessNode:
    """
    对输入图像进行亮度和对比度调整。
    公式：output = (input - 0.5) * contrast + 0.5 + brightness
    """

    def __init__(self):
        pass

    # --------------------------------------------------------
    # INPUT_TYPES：定义节点的输入插槽和参数
    # --------------------------------------------------------
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # IMAGE 类型 → 左侧出现一个图像连线插槽
                "image": ("IMAGE",),

                # FLOAT 类型 → 显示为滑块
                "brightness": ("FLOAT", {
                    "default": 0.0,    # 默认值
                    "min": -1.0,       # 最小值
                    "max": 1.0,        # 最大值
                    "step": 0.01,      # 步进
                    "display": "slider"  # 显示为滑块（可选）
                }),

                "contrast": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 3.0,
                    "step": 0.01,
                    "display": "slider"
                }),
            },
            "optional": {
                # STRING 类型 → 文本输入框
                "label": ("STRING", {
                    "default": "processed",
                    "multiline": False,
                    "description": "输出标签，用于标识此次处理"
                }),
            }
        }

    # --------------------------------------------------------
    # RETURN_TYPES：定义节点的输出插槽类型（必须是 tuple）
    # RETURN_NAMES：对应输出插槽的显示名称（可选）
    # --------------------------------------------------------
    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("处理后图像", "标签信息",)

    # FUNCTION：ComfyUI 调用的方法名
    FUNCTION = "adjust_brightness"

    # CATEGORY：节点在菜单中的分类路径
    CATEGORY = "MyDemoPlugin/图像处理"

    # --------------------------------------------------------
    # 核心处理方法
    # 参数名必须与 INPUT_TYPES 中的 key 完全一致
    # --------------------------------------------------------
    def adjust_brightness(self, image, brightness, contrast, label="processed"):
        """
        参数:
            image      : torch.Tensor [B, H, W, C], 值域 0~1
            brightness : float, 亮度偏移量
            contrast   : float, 对比度系数
            label      : str,   输出标签
        返回:
            tuple: (处理后图像 Tensor, 标签字符串)
        """
        # 对比度调整：以 0.5 为中心缩放
        result = (image - 0.5) * contrast + 0.5

        # 亮度调整：整体偏移
        result = result + brightness

        # 将像素值裁剪回合法范围 [0, 1]，防止溢出
        result = torch.clamp(result, 0.0, 1.0)

        # 构建描述信息
        info = f"{label} | brightness={brightness:.2f}, contrast={contrast:.2f}"

        # 返回必须是 tuple
        return (result, info,)


# 节点二：图像颜色反转
class ImageInvertNode:
    """
    对图像颜色进行反转（负片效果）。
    公式：output = 1.0 - input
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                # INT 类型示例 → 整数输入框
                "channels": ("INT", {
                    "default": 3,
                    "min": 1,
                    "max": 3,
                    "step": 1,
                    "description": "反转的通道数（1=R, 2=RG, 3=全部RGB）"
                }),
                # BOOLEAN 类型示例 → 勾选框
                "preserve_alpha": ("BOOLEAN", {
                    "default": True,
                    "label_on": "保留Alpha",
                    "label_off": "不保留Alpha"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("反转图像",)
    FUNCTION = "invert_image"
    CATEGORY = "MyDemoPlugin/图像处理"

    def invert_image(self, image, channels=3, preserve_alpha=True):
        """
        参数:
            image          : torch.Tensor [B, H, W, C]
            channels       : int,  反转几个通道
            preserve_alpha : bool, 是否保留 Alpha 通道（如果有）
        """
        # 克隆一份，避免修改原始张量
        result = image.clone()

        # 只反转指定数量的通道
        result[..., :channels] = 1.0 - image[..., :channels]

        return (result,)



# （可选）节点三：演示 IS_CHANGED 机制
# IS_CHANGED 用于告诉 ComfyUI 节点是否需要重新执行
# 常用于随机数/时间戳类型的节点，避免被缓存跳过
import time
import random

class RandomSeedNode:
    """生成随机种子，每次运行都返回不同的值。"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "max_value": ("INT", {"default": 2**32, "min": 1, "max": 2**32}),
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("随机种子",)
    FUNCTION = "generate_seed"
    CATEGORY = "MyDemoPlugin/工具"

    # IS_CHANGED 返回不同的值时，ComfyUI 会强制重新执行该节点
    # 返回 float("nan") 是最常见的写法，表示"永远重新执行"
    @classmethod
    def IS_CHANGED(cls, max_value):
        return float("nan")

    def generate_seed(self, max_value):
        seed = random.randint(0, max_value - 1)
        print(f"[MyDemoPlugin] 生成随机种子: {seed}")
        return (seed,)
