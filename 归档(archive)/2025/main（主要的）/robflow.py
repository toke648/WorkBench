from inference_sdk import InferenceHTTPClient
import base64

# 初始化客户端
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="fgURfIm1JVtXYCscDLrH"
)

# 运行工作流
result = client.run_workflow(
    workspace_name="main-zdes8",
    workflow_id="find-people",
    images={
        "image": "output_frames/frame_000040.jpg"
    },
    use_cache=True
)

# 检查结果结构
print("结果类型:", type(result))
print("结果长度:", len(result))

# 打印所有键，看看有什么可用字段
if result and isinstance(result, list) and len(result) > 0:
    print("可用字段:", result[0].keys())
    
    # 如果有可视化字段
    if 'visualization' in result[0]:
        # 解码base64字符串
        visualization_data = base64.b64decode(result[0]['visualization'])
        
        # 保存为图片文件
        with open("frame_000040_visualization.jpg", "wb") as f:
            f.write(visualization_data)
        print("可视化图片已保存为 frame_000040_visualization.jpg")
    
    # 保存原始结果到JSON文件以便分析
    import json
    with open("frame_000040_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("完整结果已保存为 frame_000040_result.json")
else:
    print("没有结果返回")