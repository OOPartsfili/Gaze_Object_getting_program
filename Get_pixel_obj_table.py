# -*- coding: utf-8 -*-


import carla
import argparse
import numpy as np
import pygame
import time

import Set_sensor
import cv2
from PIL import Image
import csv


def capture_screen_area(screen, x, y, width, height):
    """
    截取Pygame窗口的指定位置和尺寸的一张图，并返回为numpy数组。

    参数:
    screen: Pygame的显示屏对象。
    x: 截图区域的左上角X坐标。
    y: 截图区域的左上角Y坐标。
    width: 截图区域的宽度。
    height: 截图区域的高度。

    返回:
    numpy数组，表示截取的图像。
    """
    # 从屏幕上获取图像
    screenshot = pygame.Surface((width, height))
    screenshot.blit(screen, (0, 0), (x, y, width, height))

    # 将Pygame的Surface对象转换为numpy数组
    screenshot_array = pygame.surfarray.array3d(screenshot)
    screenshot_array = np.transpose(screenshot_array, (1, 0, 2))  # 转换维度以匹配图像格式
    return screenshot_array

def process_image(image):
    """
    处理图像，找到R通道为14的像素位置，并进行分析和标记。

    参数:
    image: numpy数组，表示输入的图像。

    返回:
    numpy数组，表示处理后的图像。
    """
    # 找到R通道为14或15的像素位置
    r_channel = image[:, :, 0]
    mask = ((r_channel == 14) | (r_channel == 15)).astype(np.uint8)

    # 使用连通域分析找到色块
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

    # 获取每个色块的大小和中心坐标
    areas = stats[1:, cv2.CC_STAT_AREA]  # 忽略背景区域
    centers = centroids[1:]  # 忽略背景区域

    # 根据色块大小排序并选择前10个最大的色块
    sorted_indices = np.argsort(-areas)[:10]
    largest_centers = centers[sorted_indices]

    # 转换为整数坐标
    largest_centers = [(int(center[0]), int(center[1])) for center in largest_centers]

    # 输出最大的10个色块的中心坐标
    print("Largest centers:", largest_centers)

    # 创建一个副本以在图像上绘制标记
    output_image_largest = image.copy()

    # 在每个中心坐标处绘制一个圆点
    for center in largest_centers:
        cv2.circle(output_image_largest, center, 5, (255, 0, 0), -1)  # 使用红色圆点标记中心

    # 识别在同一竖线上的色块
    threshold = 10  # 允许的误差范围
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
    colors = [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (255, 255, 0, 255), (255, 0, 255, 255),
              (0, 255, 255, 255)]

    # 在图像中连线
    for idx, line in enumerate(vertical_lines):
        color = colors[idx % len(colors)]  # 选择颜色
        if len(line) > 1:  # 如果有多于一个点才连线
            for k in range(len(line) - 1):
                cv2.line(output_image_largest, line[k], line[k + 1], color, 2)  # 使用不同颜色连线

    # 从上到下、从左到右排序中心点
    sorted_centers = sorted(largest_centers, key=lambda x: (x[0], x[1]))
    # 把主车自己删了
    sorted_centers = sorted_centers[:4] + sorted_centers[5:]

    # 定义车辆名称列表
    car_names = ["Car1", "Car2", "Car3", "Car4", "Car5", "Car6", "Car7", "Car8", "Car9"]

    with open('obj_pixel_table.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Pixel Value', 'Object'])
        for i, center in enumerate(sorted_centers):
            pixel_value = image[center[1], center[0]].tolist()
            pixel_value.append(255)  # 添加透明度通道
            obj_name = car_names[i] if i < len(car_names) else f"Car{i + 1}"
            writer.writerow([pixel_value, obj_name])
            print(f"Center: {center}, Pixel value: {pixel_value}, Object: {obj_name}")

    return output_image_largest



def main():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')

    argparser.add_argument(
        '-s', '--start',
        metavar='S',
        default=0.0,
        type=float,
        help='starting time (default: 0.0)')
    argparser.add_argument(
        '-d', '--duration',
        metavar='D',
        default=0.0,
        type=float,
        help='duration (default: 0.0)')

    argparser.add_argument(
        '-f', '--recorder-filename',
        metavar='F',
        default=r'E:\Search_data_package\Alignment_program\Gaze_Object_getting_program\Log_data\LOG.log',
        help='recorder filename (test1.log)')

    argparser.add_argument(
        '-c', '--camera',
        metavar='C',
        default=0,
        type=int,
        help='camera follows an actor (ex: 82)')

    argparser.add_argument(
        '-x', '--time-factor',
        metavar='X',
        default=1.0,
        type=float,
        help='time factor (default 1.0)')

    argparser.add_argument(
        '-i', '--ignore-hero',
        action='store_true',
        help='ignore hero vehicles')

    argparser.add_argument(
        '--move-spectator',
        action='store_true',
        help='move spectator camera')

    argparser.add_argument(
        '--spawn-sensors',
        action='store_true',
        help='spawn sensors in the replayed world')

    args = argparser.parse_args()

    try:

        client = carla.Client(args.host, args.port)
        client.set_timeout(10.0)

        # set the time factor for the replayer设置播放器的时间因子
        client.set_replayer_time_factor(args.time_factor)

        # set to ignore the hero vehicles or not设置是否忽略英雄车辆
        client.set_replayer_ignore_hero(args.ignore_hero)

        # set to ignore the spectator camera or not
        client.set_replayer_ignore_spectator(not args.move_spectator)

        # replay the session
        # client.replay_file(args.recorder_filename, args.start, args.duration, args.camera, args.spawn_sensors)
        print(client.replay_file(args.recorder_filename, args.start, args.duration, args.camera, args.spawn_sensors))

        world = client.get_world()

        # 寻找主车
        vehicles = world.get_actors().filter('vehicle.*')
        print(vehicles)

        vehicle = vehicles.find(99)

        # 初始化pygame
        pygame.init()
        pygame.font.init()


        display_manager = Set_sensor.DisplayManager(grid_size=[1, 3], window_size=[500,1300])
        # 前景
        Set_sensor.SensorManager(world,display_manager, 'IS',
                                 carla.Transform(carla.Location(x=30, z=30), carla.Rotation(pitch=-90)),
                                 vehicle, {'fov': '100'}, display_pos=[0, 1], Sp_flag=[[0, 0], [500, 1500]])

        t = 1
        running = True
        while running:
            pygame.display.flip()
            display_manager.render()
            if t<50:
                t+=1
            else:
                screen = display_manager.display
                # 截取屏幕中指定区域的图像
                screenshot_array = capture_screen_area(screen, 200, 0, 100, 1300)

                # 处理截取的图像
                processed_image = process_image(screenshot_array)

                # 保存处理后的图像
                output_image_path = 'processed_screenshot.png'
                output_image_pil = Image.fromarray(processed_image)
                output_image_pil.save(output_image_path)
                print(f"Processed image saved as {output_image_path}")
                running = False

            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         running = False
    finally:
        pass


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
