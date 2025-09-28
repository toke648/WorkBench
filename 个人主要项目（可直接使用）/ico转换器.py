from PIL import Image


def convert_image_to_ico(input_image_path, output_ico_path, sizes=[(32, 32)]):
    """
    将输入的图片转换为 ICO 格式并保存，支持指定尺寸。

    :param input_image_path: 输入图片的路径
    :param output_ico_path: 输出ICO图片的路径
    :param sizes: 输出ICO文件中图标的尺寸列表
    """
    # 打开图片文件
    with Image.open(input_image_path) as img:
        img = img.convert("RGBA")  # 转换为 RGBA 格式以支持透明度

        # 使用 .save 方法时传入 sizes 参数
        img.save(output_ico_path, format='ICO', sizes=sizes)

    # 示例用法


if __name__ == "__main__":
    input_image = '二期.png'  # 把这里的文件名替换为你要转换的图片文件名
    output_image = 'favicon.ico'  # 输出的ICO文件名

    # 指定多个图标尺寸
    ico_sizes = [(32, 32)]

    convert_image_to_ico(input_image, output_image, sizes=ico_sizes)
    print(f'图片已成功转换为 {output_image}，包括尺寸 {ico_sizes}')