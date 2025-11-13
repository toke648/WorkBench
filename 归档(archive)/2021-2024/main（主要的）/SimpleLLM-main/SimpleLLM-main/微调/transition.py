import json
import argparse
import os

def convert_data(input_file, output_file):
    # 读取原始数据
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 转换数据格式
    converted_data = []
    for line in lines:
        data = json.loads(line)
        for conversation in data['conversation']:
            converted_data.append({
                "instruction": conversation['human'],
                "input": "",
                "output": conversation['assistant']
            })

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 保存为新的JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, ensure_ascii=False, indent=2)
    
    print(f"数据转换完成！已将 {len(converted_data)} 条对话数据保存到 {output_file}")

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='将对话数据从JSONL格式转换为指定的JSON格式')
    parser.add_argument('--input', '-i', type=str, required=True,
                        help='输入文件路径 (JSONL格式)')
    parser.add_argument('--output', '-o', type=str, required=True,
                        help='输出文件路径 (JSON格式)')

    # 解析命令行参数
    args = parser.parse_args()

    try:
        convert_data(args.input, args.output)
    except FileNotFoundError:
        print(f"错误：找不到输入文件 {args.input}")
    except json.JSONDecodeError:
        print("错误：输入文件格式不正确，请确保是有效的JSONL文件")
    except Exception as e:
        print(f"错误：{str(e)}")

if __name__ == '__main__':
    main()