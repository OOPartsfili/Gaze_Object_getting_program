import numpy as np
import cv2
from PIL import Image

# 读取图片
image_path = 'asset/i2.png'
image = Image.open(image_path)
image = np.array(image)

# 找到R通道为14的像素位置
r_channel = image[:, :, 0]
mask = (r_channel == 14).astype(np.uint8)

# 使用连通域分析找到色块
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

# 获取每个色块的大小和中心坐标
areas = stats[1:, cv2.CC_STAT_AREA]  # 忽略背景区域
centers = centroids[1:]  # 忽略背景区域

# 根据色块大小排序并选择前6个最大的色块
sorted_indices = np.argsort(-areas)[:7]
largest_centers = centers[sorted_indices]

# 转换为整数坐标
largest_centers = [(int(center[0]), int(center[1])) for center in largest_centers]

# 输出最大的6个色块的中心坐标
print("Largest centers:", largest_centers)

# 创建一个副本以在图像上绘制标记
output_image_largest = image.copy()

# 在每个中心坐标处绘制一个圆点
for center in largest_centers:
    cv2.circle(output_image_largest, center, 5, (255, 0, 0), -1)  # 使用红色圆点标记中心

# 识别在同一竖线上的色块
threshold = 30  # 允许的误差范围
vertical_lines = []

# 创建一个标记数组，用于标记已经处理过的点
visited = [False] * len(largest_centers)

for i in range(len(largest_centers)):
    if not visited[i]:
        line = [largest_centers[i]]
        visited[i] = True
        for j in range(i + 1, len(largest_centers)):
            if abs(largest_centers[i][0] - largest_centers[j][0]) <= threshold:
                line.append(largest_centers[j])
                visited[j] = True
        if len(line) > 1:
            vertical_lines.append(sorted(line, key=lambda x: x[1], reverse=True))  # 按y坐标从大到小排序

# 定义一些颜色
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

# 在图像中连线
for idx, line in enumerate(vertical_lines):
    color = colors[idx % len(colors)]  # 选择颜色
    if len(line) > 1:  # 如果有多于一个点才连线
        for k in range(len(line) - 1):
            cv2.line(output_image_largest, line[k], line[k + 1], color, 2)  # 使用不同颜色连线

# 从上到下、从左到右排序中心点
sorted_centers = sorted(largest_centers, key=lambda x: (x[0], x[1]))

# 输出每个色块中心点对应的像素值
print("Pixel values at centers (sorted):")
for center in sorted_centers:
    pixel_value = image[center[1], center[0]]
    print(f"Center: {center}, Pixel value: {pixel_value}")

# 将绘制好的图像保存
output_image_largest_path = 'marked_image_largest_with_lines_v7.png'
output_image_largest_pil = Image.fromarray(output_image_largest)
output_image_largest_pil.save(output_image_largest_path)

output_image_largest_path
