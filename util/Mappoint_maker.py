import pygame
import sys
import pandas as pd
import numpy as np
from matplotlib.path import Path
import cv2

# 获得3块屏幕边界的像素坐标
def Get_edge(image_path):
    # 初始化pygame
    pygame.init()
    image = pygame.image.load(image_path)
    width, height = image.get_size()
    # 设置窗口
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Click to get Pixel Coordinates')
    # 主循环
    running = True
    # 存储坐标文件
    ScreenEdge_points = []

    while running:
        for event in pygame.event.get():
            # 点击关闭
            if event.type == pygame.QUIT:
                pygame.quit()
                return ScreenEdge_points

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 鼠标点击事件
                if event.button == 1:  # 鼠标左键
                    x, y = event.pos
                    print(f"Clicked at position: ({x}, {y})")
                    ScreenEdge_points.append((x,y))

        # 显示图像
        screen.blit(image, (0, 0))

        # 绘制所有点击位置的红色圆圈
        for point in ScreenEdge_points:
            pygame.draw.circle(screen, (255, 0, 0), point, 5)
        pygame.display.flip()

    pygame.quit()
    # sys.exit()




def get_points_within_polygon(polygon_vertices, canvas_size):
    """
    获取一个由多边形顶点围成的区域内的所有点的坐标。
    参数:
    polygon_vertices (list of tuples): 多边形顶点坐标列表，每个元素为一个(x, y)元组。
    vertices = [(8, 368), (555, 408), (1207, 406), (1702, 391), (1704, 902), (1191, 768), (569, 775), (5, 935)]
    canvas_size (tuple): 画布的尺寸，格式为(width, height)。
    canvas_size = (1800, 1000)
    返回:
    list: 多边形内的所有点的坐标列表。
    """
    # 创建网格
    x, y = np.meshgrid(np.arange(canvas_size[0]), np.arange(canvas_size[1]))
    x, y = x.flatten(), y.flatten()
    points = np.vstack((x, y)).T
    # 构建多边形路径
    poly_path = Path(polygon_vertices)
    # 使用多边形路径检测点是否在多边形内
    grid = poly_path.contains_points(points)
    # 提取在多边形内的点
    points_within_polygon = points[grid]
    points_within_polygon = [tuple(point) for point in points_within_polygon.tolist()]

    return points_within_polygon


# 获取坐标矩阵
# 输入图像4点坐标和 映射目标四点坐标
# 输出映射矩阵
def Get_map_matrix(origin_points,aim_points):
    # 将挑选的四个点转换为NumPy数组
    pts1 = np.float32(origin_points)
    pts2 = np.float32(aim_points)
    # 计算透视变换矩阵
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    return matrix

# 检查点是在哪块屏幕范围内，从而对应着进行坐标映射
def Get_screen(Ori_point, ScreenEdge_points, matrixs, canvas_size):
    ScreenArea_points = get_points_within_polygon(ScreenEdge_points, canvas_size)

    # 先检查点在不在屏幕内,不在的直接不管了
    if Ori_point not in ScreenArea_points:
        Map_point = Ori_point
    else:
        if Ori_point[0] <=  ScreenEdge_points[1][0]:  #在第一块屏幕上
            pixel_relative_array = np.float32([[[Ori_point[0], Ori_point[1]]]])
            pixel_transformed = cv2.perspectiveTransform(pixel_relative_array, matrixs[0])
            Map_point = (pixel_transformed[0][0][0], pixel_transformed[0][0][1])

        elif Ori_point[0] <=  ScreenEdge_points[2][0]: #在第二块屏幕上
            pixel_relative_array = np.float32([[[Ori_point[0], Ori_point[1]]]])
            pixel_transformed = cv2.perspectiveTransform(pixel_relative_array, matrixs[1])
            Map_point = (pixel_transformed[0][0][0], pixel_transformed[0][0][1])
        else: #在第三块屏幕上
            pixel_relative_array = np.float32([[[Ori_point[0], Ori_point[1]]]])
            pixel_transformed = cv2.perspectiveTransform(pixel_relative_array, matrixs[2])
            Map_point = (pixel_transformed[0][0][0], pixel_transformed[0][0][1])
    # 像素坐标整数化
    Map_point2 = [int(Map_point[0]),int(Map_point[1])]
    # 超出边界部分的处理
    if Map_point2[0] <= 0:
        Map_point2[0] = 1
    elif Map_point2[0] >= canvas_size[0]*3:
        Map_point2[0] = canvas_size[0]*3-1

    if Map_point2[1] <= 0:
        Map_point2[1] = 1
    elif Map_point2[1] >= canvas_size[1]:
        Map_point2[1] = canvas_size[1]

    return Map_point2



if __name__ == "__main__":
    image_path = '../asset/resized_image.png'
    canvas_size = (1913, 1010)
    HRT_split_path = "../HRT_data/HRT_split.csv"

    # 这一步先获得屏幕坐标,格式为[(687, 211), (533, 276), (547, 395), (846, 489), (856, 480), (375, 487), (384, 364)]
    ScreenEdge_points = Get_edge(image_path)
    # ScreenEdge_points = [(7, 368), (555, 406), (1200, 403),(1702, 390), (1702, 899), (1195, 776),(569, 780), (6, 934)]
    # 这是屏幕范围内全部的点，用来判断注视点是否在屏幕内的

    origin_points1 = [ScreenEdge_points[0], ScreenEdge_points[1], ScreenEdge_points[6], ScreenEdge_points[7]]
    origin_points2 = [ScreenEdge_points[1], ScreenEdge_points[2], ScreenEdge_points[5], ScreenEdge_points[6]]
    origin_points3 = [ScreenEdge_points[2], ScreenEdge_points[3], ScreenEdge_points[4], ScreenEdge_points[5]]

    # 这个是用完整3块屏做实验的屏幕参数
    # aim_points1 = [(0,0),(canvas_size[0],0),(canvas_size[0],canvas_size[1]),(0,canvas_size[1])]
    # aim_points2 = [(canvas_size[0],0),(canvas_size[0]*2,0),(canvas_size[0]*2,canvas_size[1]),(canvas_size[0],canvas_size[1])]
    # aim_points3 = [(canvas_size[0]*2,0),(canvas_size[0]*3,0),(canvas_size[0]*3,canvas_size[1]),(canvas_size[0]*2,canvas_size[1])]

    # 这个是为了保证数据有效性的特殊屏幕参数(就是前景放不下3块屏，或者放下后中间那个关键屏幕太小了)
    #截取部分的像素坐标
    Sp_x1 = 545
    Sp_x2 = 1445

    aim_points1 = [(Sp_x1, 0), (canvas_size[0], 0), (canvas_size[0], canvas_size[1]), (Sp_x1, canvas_size[1])]
    aim_points2 = [(canvas_size[0], 0), (canvas_size[0] * 2, 0), (canvas_size[0] * 2, canvas_size[1]),
                   (canvas_size[0], canvas_size[1])]
    aim_points3 = [(canvas_size[0] * 2, 0), (canvas_size[0] * 2 + Sp_x2, 0), (canvas_size[0] * 2 + Sp_x2, canvas_size[1]),
                   (canvas_size[0] * 2, canvas_size[1])]


    ScreenArea_points = get_points_within_polygon(ScreenEdge_points, canvas_size)

    Mat1 = Get_map_matrix(origin_points1, aim_points1)
    Mat2 = Get_map_matrix(origin_points2, aim_points2)
    Mat3 = Get_map_matrix(origin_points3, aim_points3)

    matrixs = [Mat1, Mat2, Mat3]


    # 读取眼动坐标，输出映射好后的坐标CSV文件
    origin_DF = pd.read_csv(HRT_split_path)
    origin_DF_x = origin_DF['ScreenPoint_x']
    origin_DF_y = origin_DF['ScreenPoint_y']
    coordinates = list(zip(origin_DF_x, origin_DF_y))
    DF_x = []
    DF_y = []

    i = 1

    for Ori_point in coordinates:
        print(f'现在已经完成了{i}个点')
        i += 1
        Map_point = Get_screen(Ori_point, ScreenEdge_points, matrixs, canvas_size)
        DF_x.append(Map_point[0])
        DF_y.append(Map_point[1])
    # print(Map_point)

    data = {'ScreenPoint_x': DF_x, 'ScreenPoint_y': DF_y}
    Screen_DF = pd.DataFrame(data)
    Screen_DF.to_csv('../HRT_data/Mapped_HRT_split.csv', index=False)
