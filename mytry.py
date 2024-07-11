import pygame
import csv

# 初始化 Pygame
pygame.init()

# 加载图片
image_path = 'asset/fbdeb991f9844721f57240753f8c090.png'  # 替换为你的图片路径
image = pygame.image.load(image_path)

# 设置显示窗口
screen = pygame.display.set_mode((image.get_width(), image.get_height()))
pygame.display.set_caption("像素颜色选择器")

# 获取给定位置的像素 RGBA 值的函数
def get_pixel_color(x, y):
    return pygame.Surface.get_at(image, (x, y))

# 用于保存像素数据的字典
pixel_data = {}

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            color = get_pixel_color(x, y)
            # 提示用户输入该像素的对象描述
            obj = input(f"请输入像素 {color} 的对象描述: ")
            pixel_data[str(color)] = obj

    # 显示图片
    screen.blit(image, (0, 0))
    pygame.display.flip()

# 将像素数据保存到 CSV 文件
with open('obj_pixel_table.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['pixel', 'obj'])
    for key, value in pixel_data.items():
        writer.writerow([key, value])

# 退出 Pygame
pygame.quit()
