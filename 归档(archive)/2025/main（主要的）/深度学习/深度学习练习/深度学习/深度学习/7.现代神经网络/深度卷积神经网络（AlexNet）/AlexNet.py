import torch
import torch.nn as nn
import torch.nn.functional as F


class AlexNet(nn.Module):
    def __init__(self, num_classes=1000):
        super(AlexNet, self).__init__()
        # 特征提取部分（卷积层）
        self.features = nn.Sequential(
            # 第1层：输入3通道，输出64通道
            nn.Conv2d(3, 96, kernel_size=11, stride=4),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.BatchNorm2d(96),  # 添加BatchNorm

            # 第2层：输入64通道，输出192通道
            nn.Conv2d(96, 256, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.BatchNorm2d(256),  # 添加BatchNorm

            # 第3层：输入192通道，输出384通道
            nn.Conv2d(256, 384, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),

            # 第4层：输入384通道，输出256通道
            nn.Conv2d(384, 384, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),

            # 第5层：输入256通道，输出256通道
            nn.Conv2d(384, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),

        )

        # 分类器部分（全连接层）
        self.classifier = nn.Sequential(
            nn.Dropout(),
            nn.Linear(256 * 6 * 6, 4096),
            nn.ReLU(inplace=True),

            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),

            nn.Linear(4096, num_classes),
        )

    def forward(self, x):
        # 特征提取
        x = self.features(x)
        # 展平
        x = torch.flatten(x, 1)
        # 分类
        x = self.classifier(x)
        return x


def simulate_alexnet_forward_pass():
    torch.manual_seed(42)

    # 1. 创建模型实例
    model = AlexNet(num_classes=1000)
    print("✓ AlexNet模型创建成功")

    # 2. 生成随机输入张量 (batch_size=4, channels=3, height=227, width=227)
    # 模拟4张227x227的RGB图像
    input_tensor = torch.randn(4, 3, 227, 227)
    print(f"✓ 输入张量形状: {input_tensor.shape}")
    print(f"✓ 输入值范围: [{input_tensor.min():.3f}, {input_tensor.max():.3f}]")

    # 3. 将模型设置为评估模式（关闭dropout）
    model.eval()
    print("✓ 模型设置为评估模式")

    # 4. 前向传播（不计算梯度以节省内存）
    with torch.no_grad():
        print("\n🚀 开始前向传播...")

        # 逐层跟踪前向传播
        x = input_tensor.clone()
        print(f"输入层: {x.shape}")

        # 特征提取部分逐层处理
        for i, layer in enumerate(model.features):
            x = layer(x)
            if isinstance(layer, nn.Conv2d):
                print(f"卷积层 {i // 3 + 1}: {x.shape}")
            elif isinstance(layer, nn.MaxPool2d):
                print(f"池化层 {(i - 1) // 3 + 1}: {x.shape}")


        # 展平
        x = torch.flatten(x, 1)
        print(f"展平后: {x.shape}")

        # 分类器部分逐层处理
        for i, layer in enumerate(model.classifier):
            x_prev_shape = x.shape
            x = layer(x)
            if isinstance(layer, nn.Linear):
                print(f"全连接层 {i // 3 + 1}: {x_prev_shape} -> {x.shape}")
            elif isinstance(layer, nn.Dropout):
                print(f"Dropout层 {(i - 1) // 3 + 1}: 激活 {x_prev_shape[1]}个神经元")

        output = x

    # 5. 输出结果分析
    print(f"\n📊 前向传播完成！")
    print(f"最终输出形状: {output.shape}")
    print(f"输出值范围: [{output.min():.3f}, {output.max():.3f}]")
    print(f"输出示例（前5个类别的原始分数）: {output[0][:5]}")

    # 6. 应用softmax得到概率分布
    probabilities = F.softmax(output, dim=1)
    print(f"概率分布范围: [{probabilities.min():.3f}, {probabilities.max():.3f}]")
    print(f"概率总和（验证）: {probabilities.sum(dim=1)[0]:.3f}")

    # 7. 获取预测结果
    _, predicted_classes = torch.max(output, 1)
    print(f"预测类别: {predicted_classes}")

    return model, input_tensor, output, probabilities


# 运行模拟
model, input_tensor, output, probabilities = simulate_alexnet_forward_pass()