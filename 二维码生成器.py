import qrcode

# 要编码的内容
data = "https://toke648.github.io/"

# 创建二维码对象
qr = qrcode.QRCode(
    version=1,  # 1-40 控制二维码的大小，1 最小
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # 容错率 L/M/Q/H
    box_size=10,  # 每个小格子的像素大小
    border=2,  # 边框厚度（格子数）
)

qr.add_data(data)
qr.make(fit=True)

# 生成二维码图像
img = qr.make_image(fill_color="black", back_color="white")

# 保存成文件
img.save("qrcode.png")
