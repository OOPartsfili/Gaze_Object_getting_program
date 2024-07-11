from PIL import Image

def resize_image(image_path, new_width, new_heigth):
    # 打开图像
    with Image.open(image_path) as img:
        # 缩放图像
        resized_img = img.resize((new_width, new_heigth), Image.LANCZOS)

        # 可以选择保存或直接返回缩放后的图像
        resized_img.save('../asset/resized_image.png')  # 保存到文件
        # return resized_img

# 使用函数
image_path = '../asset/SCREEN.png'  # 替换为你的图像路径
new_width = 1920  # 设置新的宽度
new_heigth = 1080  # 设置新的高度

resize_image(image_path, new_width,new_heigth)
