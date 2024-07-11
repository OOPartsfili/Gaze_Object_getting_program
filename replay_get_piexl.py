# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 14:30:18 2024

@author: Lenovo
"""

import carla
import argparse
import pygame
from util import Time_maker
import pandas as pd
import Set_sensor


# 坐标映射个性化函数
# 输入 原始坐标数据框
# 输出 坐标映射好后的数据框
def Coordinate_mapping(origin_DF):
    origin_DF_x = origin_DF['ScreenPoint_x']
    origin_DF_y = origin_DF['ScreenPoint_y']

    # 个性化映射函数（1920X1080）
    # 屏幕长、宽数值：1060，590
    # 屏幕左上角度：（140，317）
    # pygame窗口大小：（1800X1000）
    DF_x = (origin_DF_x - 140)*( 1800/1060 )
    DF_y = (origin_DF_y - 317)*( 1000/590 )
    for i in range(len(DF_x)):
        if DF_x[i] >= 1800:
            DF_x[i] = 1799
        elif DF_x[i] <= 0:
            DF_x[i] = 1

        # 出边界也假设他没出，在边界上
        if DF_y[i] >= 1000:
            DF_y[i] = 999
        if DF_y[i] <= 0:
            DF_y[i] = 1

    data = {'ScreenPoint_x': DF_x, 'ScreenPoint_y': DF_y}
    Screen_DF = pd.DataFrame(data)
    # print(Screen_DF)
    return Screen_DF


# 注视点可视化,在pygame窗口里绘制注视点，看看情况
# 输入 HRT文件路径，pygame的回放时间,后视镜管理器
# 输出：一个
def map_eyePoint(HRT_split_path="HRT_data\HRT_split.csv"):
    origin_DF = pd.read_csv(HRT_split_path)
    # 点的播放频率
    # frequency = lasttime/len(origin_DF)
    # 进行点坐标的映射
    Screen_DF = Coordinate_mapping(origin_DF)

    x_column_name = 'ScreenPoint_x'
    y_column_name = 'ScreenPoint_y'
    if x_column_name in Screen_DF.columns and y_column_name in Screen_DF.columns:
        # 创建一个新的Screen_DF2，包含组合后的(x, y)坐标
        Screen_DF2 = Screen_DF[[x_column_name, y_column_name]].apply(lambda row: (row[x_column_name], row[y_column_name]),axis=1)
    else:
        print(f"确保列名正确：'{x_column_name}' 和 '{y_column_name}' 必须存在于数据中。")

    return Screen_DF2


# 将像素值转换为物体ID ，这个函数处理的是1对1注视物
# 输入一个注视像素值列表，一个像素对应物体字典CSV文件路径
# 返回一个物体ID列表
def piexl2object(piexl_list,file_path= 'obj_pixel_table.csv'):
    # 使用pandas读取CSV文件
    df = pd.read_csv(file_path)
    # 将DataFrame转换为字典，其中pixel列的值作为键，obj列的值作为对应的值
    obj_pixel_dict = df.set_index('pixel')['obj'].to_dict()

    obj_list = []
    for piexl_point in piexl_list:
        # 背景像素值
        key = str(piexl_point)
        try:
            obj = obj_pixel_dict[key]
        except KeyError:
            #在看目标以外的东西
            obj = 'None'
        finally:
            obj_list.append(obj)
    return obj_list



# 感受野方法
# 输入一个注视点，一个像素对应物体字典CSV文件路径
# 输出一个感知物体0-1列表
def Stare2FeelingArea(display_manager,Stare_point, file_path= 'obj_pixel_table.csv'):
    df = pd.read_csv(file_path)
    obj_pixel_list = df['pixel']

    # print(obj_pixel_list)

    # 暂时用正方形感受野
    def find_points_in_rectangle(center, width, height):
        x_center, y_center = center
        points = []

        # 计算矩形的左、右、上、下边界
        left = x_center - width // 2
        right = x_center + width // 2
        top = y_center - height // 2
        bottom = y_center + height // 2

        # 遍历矩形范围内的所有整数点
        for x in range(left, right + 1):
            for y in range(top, bottom + 1):
                points.append([x, y])
        return points


    # 使用函数获取矩形内部所有整数点坐标
    center = Stare_point
    width = 20
    height = 20
    rectangle_points = find_points_in_rectangle(center, width, height)


    # 这里需要防止坐标超过范围
    for i in range(len(rectangle_points)):
        if rectangle_points[i][0] >= 1800:
            rectangle_points[i][0] = 1799.0
        elif rectangle_points[i][0] <= 0:
            rectangle_points[i][0] = 1.0

        # 出边界也假设他没出，在边界上
        if rectangle_points[i][1]>= 1000:
            rectangle_points[i][1] = 999.0
        if rectangle_points[i][1] <= 0:
            rectangle_points[i][1] = 1.0


    # 对所有整数点坐标吃一次像素
    pixel_list = []
    for one_point in rectangle_points:
        pixel = display_manager.display.get_at((int(one_point[0]), int(one_point[1])))
        pixel_list.append(pixel)
    # 这样有和像素字典同长度的感知列表了
    Feeling_list = []

    for i in range(len(obj_pixel_list)):
          Feeling_list.append(0)

    # 这里obj_pixel是物体对应的一个像素
    for obj_pixel_index in range(len(obj_pixel_list)):
        if obj_pixel_list[obj_pixel_index] in pixel_list:
            # 感知到了
            Feeling_list[obj_pixel_index] = 1

    # print(Feeling_list)
    return Feeling_list


def main():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '-f', '--recorder-filename',
        metavar='F',
        default=r'E:\Search_data_package\Alignment_program\Data_program\Log_data\test1.log',
        help='recorder filename')

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
        '-a', '--show_all',
        action='store_true',
        help='show detailed info about all frames content')
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

        # 这里要获取注视点的发送频率
        last_time = client.show_recorder_file_info(args.recorder_filename, args.show_all)[-50:]
        last_time = Time_maker.log_get_lasttime(last_time)
        last_time = float(last_time)

        # 初始化pygame
        display_manager = Set_sensor.DisplayManager(grid_size=[1, 3], window_size=[1800, 1000])

        # 这句话后，开始在UE4里回放轨迹
        print(client.replay_file(args.recorder_filename, args.start, args.duration, args.camera, args.spawn_sensors))

        world = client.get_world()


        # 寻找主车
        vehicles = world.get_actors().filter('vehicle.*')
        print(vehicles)
        vehicle = vehicles.find(307)


        # 左后视镜
        Set_sensor.SensorManager(world, display_manager, 'IS',
                                 carla.Transform(carla.Location(x=0.5, y=-1, z=1.1), carla.Rotation(yaw=-150)),
                                 vehicle, {}, display_pos=[0, 0], Sp_flag=[[0, 500], [500, 500]])
        # 右后视镜
        Set_sensor.SensorManager(world, display_manager, 'IS',
                                 carla.Transform(carla.Location(x=0.5, y=1, z=1.1), carla.Rotation(yaw=+150)),
                                 vehicle, {}, display_pos=[0, 2], Sp_flag=[[1300, 500], [500, 500]])
        # 前景
        Set_sensor.SensorManager(world, display_manager, 'IS',
                                 carla.Transform(carla.Location(x=2, y=-0.18, z=1.3), carla.Rotation(yaw=+00)),
                                 vehicle, {}, display_pos=[0, 1], Sp_flag=[[500, 0], [800, 1000]])
        # 正后视镜
        Set_sensor.SensorManager(world, display_manager, 'IS',
                                 carla.Transform(carla.Location(x=-1.6, y=0, z=1.35), carla.Rotation(yaw=+180)),
                                 vehicle, {}, display_pos=[1, 1], Sp_flag=[[600, 0], [600, 200]])

        # 设置刷新帧率
        clock = pygame.time.Clock()
        fps = 60


        # 获取注视点映射坐标
        Screen_DF2 = map_eyePoint(HRT_split_path="HRT_data/HRT_split.csv")
        # 这里加上你喜欢的颜色
        white = (255, 255, 255)
        # 这是为了辅助读取眼动数据的index，后视镜刷新一次，眼动也渲染一次
        eyepoint_index = 0
        #结束循环的关键旗子
        running = True

        # 保存像素点的列表
        pixel_list = []

        while running:
            # 退出界面(包括停止回放，车辆销毁)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            # 如果眼动数据不足了，也退出
            if eyepoint_index == len(Screen_DF2)-1:
                running = False

            one_point = Screen_DF2[eyepoint_index]
            eyepoint_index += 1
            # pygame渲染刷新
            pygame.display.flip()
            # 渲染器刷新4个后视镜的画面
            display_manager.render()
            # 这里可以改为可视化，也可以改为正式的提取像素值

            # 立刻吃一次注视点刷新
            # pygame.draw.circle(display_manager.display, white, (one_point[0], one_point[1]), 15)
            # pygame.display.flip()

            # 立刻提取一次像素值
            # pixel = display_manager.display.get_at((int(one_point[0]), int(one_point[1])))
            # pixel_list.append(pixel)
            # print(pixel)


            # # 感受野方法
            try2 = Stare2FeelingArea(display_manager,(int(one_point[0]), int(one_point[1])))
            print(try2)

            # 锁帧
            clock.tick(fps)


        # Stare_obj_list = piexl2object(pixel_list, file_path='obj_pixel_table.csv')
        #
        # # print(Stare_obj_list)
        # # 将列表写入 CSV 文件
        # df = pd.DataFrame(Stare_obj_list)
        # df.to_csv('Stare_obj_output.csv', index=False)
        #
        # # 存一份像素的列表
        # df_pixel_list = pd.DataFrame(pixel_list)
        # df_pixel_list.to_csv('Stare_pixel_output.csv', index=False)

        print("注视物CSV文件已保存。")


    finally:
        # 如果display_manager还存在，就将其摧毁
        pass


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
