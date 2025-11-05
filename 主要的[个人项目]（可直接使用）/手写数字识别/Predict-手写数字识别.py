import torch  # 导入PyTorch库，用于构建和训练神经网络
import torch.nn.functional as F  # 导入PyTorch的神经网络功能库，包含如softmax等函数
from torchvision import transforms  # 导入torchvision的transforms模块，用于图像预处理
from PIL import Image  # 导入PIL库中的Image模块，用于打开和处理图像文件
import matplotlib.pyplot as plt


from Train import *  # 确保从正确的位置导入CNN类，这里CNN应该是一个定义好的卷积神经网络模型

class Predict(object):  # 定义一个名为Predict的类，用于图像预测
    def __init__(self):
        self.network = CNN()  # 实例化CNN类，创建一个神经网络对象
        # 加载预训练的模型权重
        self.network.load_state_dict(torch.load('./ckpt/cp-0010.pth'))  # 从指定路径加载训练好的模型权重
        self.network.eval()  # 将网络设置为评估模式，关闭dropout和batchnorm的训练特性

    def predict(self, image_path):  # 定义一个预测函数，接受图像路径作为参数
        # 图像预处理
        transform = transforms.Compose([  # 创建一个预处理流程
            transforms.Resize((28, 28)),  # 将图像大小调整为28x28
            transforms.ToTensor(),  # 将PIL图像或numpy.ndarray转换为torch.Tensor，并归一化到[0, 1]
            transforms.Normalize((0.5,), (0.5,))  # 对Tensor图像进行标准化，这里使用的是单通道图像，均值为0.5，标准差也为0.5
        ])

        img = Image.open(image_path).convert('L')  # 打开图像文件，并转换为灰度图
        img_tensor = transform(img).unsqueeze(0)  # 对图像应用预处理流程，并添加一个批次维度（batch dimension）
        print(img_tensor.size())

        # 预测
        with torch.no_grad():  # 在不计算梯度的情况下进行预测，减少内存消耗并加速计算
            output = self.network(img_tensor)  # 将预处理后的图像输入网络，得到输出
            predicted_probabilities = F.softmax(output, dim=1).squeeze(0)  # 对输出应用softmax函数得到概率分布，并移除批次维度

        # 获取最大概率的类别
        _, predicted_class = torch.max(predicted_probabilities, 0)  # 在概率分布中找到最大值的索引，即预测的类别

        print(image_path)  # 打印图像路径
        print(predicted_probabilities, ' -> 预测数字为：', predicted_class.item())  # 打印预测的概率分布和预测的类别


if __name__ == "__main__":  # 当此脚本作为主程序运行时
    app = Predict()  # 创建Predict类的实例
    app.predict('./test_images/0_57.png')  # 对第二张测试图像进行预测
    # app.predict('./test2/0_57_inverted.png')  # 对第二张测试图像进行预测
    app.predict('./test_images/1_32.png')  # 对第二张测试图像进行预测
    # app.predict('./test2/1_32_inverted.png')  # 对第二张测试图像进行预测
    app.predict('./test_images/3_59.png')  # 对第二张测试图像进行预测
    # app.predict('./test2/3_59_inverted.png')  # 对第二张测试图像进行预测
    # app.predict('./test_images/3_59.png')  # 对第三张测试图像进行预测



# 显示手写数据集图像（通过显示图像找到上面测试手写数字不准确的原因，生成新的黑白图像测试图）
# data = DataSource()
#
# # 获取一批训练数据
# dataiter = iter(data.train_loader)
# # images:[64, 1, 28, 28] labels:[64]
# images, labels = next(dataiter)
#
# # 创建一个图形窗口来显示图像
# fig, axes = plt.subplots(1, len(images[0]), figsize=(10, 3))
# # for i, (image, label) in enumerate(zip(images, labels)):
# # 将图像从张量转换回numpy数组，并去掉归一化（如果需要）
#
# # images[0]选取批次中的第一张图像（张量形状为 [1, 28, 28]）。
# # .numpy()将PyTorch张量转换为NumPy数组。
# # .squeeze()移除数组中的单维度条目（即从 [1, 28, 28]变为 [28, 28]）。
# # * 255是为了将归一化后的像素值（原始预处理中归一化到[-1,1]或[0,1]）反变换回0-255范围，但这里可能不精确
# image = images[0].numpy().squeeze() * 255  # 这里乘以255是为了将归一化的值转换回0-255范围（如果原始图像是0-255的话）
# # 也可以使用image = image.permute(1, 2, 0).numpy() * 255.0来转换，但这里已经使用了squeeze()去掉了多余的维度
# # 显示图像 cmap='gray'指定使用灰度色彩映射
# axes.imshow(image, cmap='gray')
# axes.set_title(f'Label: {labels[0].item()}')
# axes.axis('off')  # 关闭坐标轴
#
# # 显示图形
# plt.show()
