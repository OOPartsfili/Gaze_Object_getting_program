import numpy as np
import cv2
from PIL import Image

# 读取图片
image_path = 'asset/image.png'
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
sorted_indices = np.argsort(-areas)[:6]
largest_centers = centers[sorted_indices]

# 转换为整数坐标
largest_centers = [(int(center[0]), int(center[1])) for center in largest_centers]

# 输出最大的6个色块的中心坐标
print(largest_centers)

# # 创建一个副本以在图像上绘制标记
# output_image_largest = image.copy()
#
# # 在每个中心坐标处绘制一个圆点
# for center in largest_centers:
#     cv2.circle(output_image_largest, center, 5, (255, 0, 0), -1)  # 使用红色圆点标记中心
#
# # 将绘制好的图像保存
# output_image_largest_path = '/mnt/data/marked_image_largest.png'
# output_image_largest_pil = Image.fromarray(output_image_largest)
# output_image_largest_pil.save(output_image_largest_path)