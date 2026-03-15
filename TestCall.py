
import json
import time
import requests

# ── 配置 ──────────────────────────────────────────
SERVER      = "http://127.0.0.1:8188"
WORKFLOW_PATH = "D:/AI/ComfyUI-aki-v1.6/ComfyUI/user/default/workflows/test.json"
OUTPUT_DIR  = "D:/AI/ComfyUI-aki-v1.6/ComfyUI/custom_nodes/ComfyUI-MyDemoPlugin/"
# ─────────────────────────────────────────────────

def load_workflow(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def convert_to_api_format(workflow):
    """
    把 UI 格式的 workflow.json 转成 API 格式
    UI 格式: {"nodes": [...], "links": [...]}
    API 格式: {"节点ID": {"class_type": ..., "inputs": {...}}}
    """
    # 如果已经是 API 格式，直接返回
    if "nodes" not in workflow:
        return workflow

    # 构建链接映射: link_id -> [源节点ID, 源输出槽]
    link_map = {}
    for link in workflow.get("links", []):
        # link 格式: [link_id, 源节点ID, 源输出槽, 目标节点ID, 目标输入槽, 类型]
        link_id = link[0]
        link_map[link_id] = [str(link[1]), link[2]]

    api_workflow = {}
    for node in workflow["nodes"]:
        node_id = str(node["id"])
        class_type = node["type"]
        inputs = {}

        widget_values = node.get("widgets_values", [])
        widget_idx = 0

        for inp in node.get("inputs", []):
            link_id = inp.get("link")
            if link_id is not None:
                # 连线输入：引用其他节点的输出
                inputs[inp["name"]] = link_map[link_id]
            else:
                # widget 输入：从 widgets_values 取值
                if widget_idx < len(widget_values):
                    inputs[inp["name"]] = widget_values[widget_idx]
                    widget_idx += 1

        # 没有 link 的 widget（纯 widget 节点）
        for prop in node.get("inputs", []):
            pass  # 已处理

        api_workflow[node_id] = {
            "class_type": class_type,
            "inputs": inputs
        }

    return api_workflow


def modify_params(api_workflow, node_id, **kwargs):
    """修改指定节点的参数"""
    if node_id in api_workflow:
        for key, value in kwargs.items():
            api_workflow[node_id]["inputs"][key] = value
        print(f"✅ 已修改节点 {node_id}: {kwargs}")
    else:
        print(f"❌ 节点 {node_id} 不存在，可用节点: {list(api_workflow.keys())}")


def queue_prompt(api_workflow):
    """提交任务到 ComfyUI 队列"""
    payload = {"prompt": api_workflow}
    resp = requests.post(f"{SERVER}/prompt", json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"ComfyUI 报错: {data['error']}")
    return data["prompt_id"]


def wait_for_result(prompt_id, timeout=120):
    """轮询等待任务完成"""
    print(f"⏳ 等待生成完成（最多 {timeout}s）...")
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(f"{SERVER}/history/{prompt_id}", timeout=10)
        history = resp.json()
        if prompt_id in history:
            status = history[prompt_id].get("status", {})
            if status.get("completed"):
                print("✅ 生成完成！")
                return history[prompt_id]
            elif status.get("status_str") == "error":
                raise RuntimeError(f"ComfyUI 执行出错: {status}")
        time.sleep(2)
        print(".", end="", flush=True)
    raise TimeoutError(f"超时：{timeout}s 内未完成")


def save_images(result, output_dir):
    """下载并保存生成的图像"""
    saved = []
    outputs = result.get("outputs", {})
    for node_id, node_output in outputs.items():
        for img_info in node_output.get("images", []):
            filename  = img_info["filename"]
            subfolder = img_info.get("subfolder", "")
            folder    = img_info.get("type", "output")

            params = {"filename": filename, "subfolder": subfolder, "type": folder}
            img_resp = requests.get(f"{SERVER}/view", params=params, timeout=30)
            img_resp.raise_for_status()

            save_path = f"{output_dir}/{filename}"
            with open(save_path, "wb") as f:
                f.write(img_resp.content)
            print(f"🖼️  已保存: {save_path}")
            saved.append(save_path)
    return saved


# ── 主流程 ────────────────────────────────────────
if __name__ == "__main__":
    # 1. 读取工作流
    workflow = load_workflow(WORKFLOW_PATH)

    # 2. 转换为 API 格式
    api_wf = convert_to_api_format(workflow)
    print("📋 工作流节点:", list(api_wf.keys()))

    # 3. 修改参数（节点ID从上面打印的列表里找）
    # 根据你的工作流 JSON，ImageBrightnessNode 的 id 是 62
    modify_params(api_wf, "62", brightness=0.8, contrast=1.5)

    # 4. 提交任务
    prompt_id = queue_prompt(api_wf)
    print(f"📨 任务已提交，ID: {prompt_id}")

    # 5. 等待完成
    result = wait_for_result(prompt_id)

    # 6. 保存图像
    save_images(result, OUTPUT_DIR)
