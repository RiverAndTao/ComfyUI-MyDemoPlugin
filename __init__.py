
# ============================================================
# ComfyUI-MyDemoPlugin / __init__.py
# 作用：ComfyUI 启动时扫描此文件，完成节点注册
# ============================================================

from .nodes.image_nodes import ImageBrightnessNode, ImageInvertNode

# -----------------------------------------------------------
# NODE_CLASS_MAPPINGS
# Key   → ComfyUI 内部唯一标识符（不能重复）
# Value → 对应的 Python 类
# -----------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "ImageBrightnessNode": ImageBrightnessNode,
    "ImageInvertNode":     ImageInvertNode,
}

# -----------------------------------------------------------
# NODE_DISPLAY_NAME_MAPPINGS
# Key   → 与 NODE_CLASS_MAPPINGS 的 Key 保持一致
# Value → 显示在 ComfyUI UI 界面上的名称（可含中文/空格）
# -----------------------------------------------------------
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageBrightnessNode": "🎨 图像亮度调整",
    "ImageInvertNode":     "🔄 图像颜色反转",
}

# 可选：打印加载成功信息
print("✅ [MyDemoPlugin] 节点加载成功！")

# 导出映射（部分 ComfyUI 版本需要）
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
