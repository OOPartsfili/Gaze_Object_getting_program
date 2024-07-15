

import carla
import argparse
import pygame
from util import Time_maker
import pandas as pd
import Set_sensor
from Scene_data import Scene1


# 注视点可视化,在pygame窗口里绘制注视点，看看情况
# 输入 HRT文件路径，pygame的回放时间,后视镜管理器
# 输出：一个列名正确的DF
def map_eyePoint(HRT_split_path="HRT_data\Mapped_HRT_split.csv"):
    Screen_DF = pd.read_csv(HRT_split_path)
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
            obj = 'None'             #在看目标以外的东西
        finally:
            obj_list.append(obj)
    return obj_list

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

# 这样有和像素字典同长度的感知列表了
df = pd.read_csv( 'obj_pixel_table.csv')
obj_pixel_list = df['Pixel Value']
Feeling_list = []
for i in range(len(obj_pixel_list)):
        Feeling_list.append(0)


# 感受野方法
# 输入一个注视点，一个像素对应物体字典CSV文件路径
# 输出一个感知物体标签序列
def Stare2FeelingArea(display_manager,Stare_point, file_path= 'obj_pixel_table.csv'):
    global Feeling_list
    df = pd.read_csv(file_path)
    obj_pixel_list = df['Pixel Value']
    # print(obj_pixel_list)

    # 使用函数获取矩形内部所有整数点坐标
    center = Stare_point
    # 这里确定矩形的长和宽
    width = 120
    height = 120
    rectangle_points = find_points_in_rectangle(center, width, height)

    # 对所有整数点坐标吃一次像素
    pixel_list = []
    for one_point in rectangle_points:
        try:
            pixel = display_manager.display.get_at((int(one_point[0]), int(one_point[1])))
        except IndexError:
            pixel = (1, 1, 1, 1)
        # print(pixel)
        pixel_list.append(pixel)

    # 这里obj_pixel是物体对应的一个像素
    for obj_pixel_index in range(len(obj_pixel_list)):
        obj_pixel = obj_pixel_list[obj_pixel_index].strip('[]').split(',')
        obj_pixel = tuple(map(int, obj_pixel))

        if obj_pixel in pixel_list:
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
        default=r'E:\Search_data_package\Alignment_program\Gaze_Object_getting_program\Log_data\LOG.log',
        help='recorder filename')
    argparser.add_argument(
        '--host',metavar='H',default='127.0.0.1',help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port', metavar='P',default=2000,type=int,help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-s', '--start',metavar='S',default=0.0,type=float,help='starting time (default: 0.0)')
    argparser.add_argument(
        '-d', '--duration',metavar='D',default=0.0, type=float,help='duration (default: 0.0)')
    argparser.add_argument(
        '-a', '--show_all',action='store_true')
    argparser.add_argument(
        '-c', '--camera',metavar='C',default=0,type=int)
    # 这个延长时间非常重要啊
    argparser.add_argument(
        '-x', '--time-factor',
        metavar='X',
        default=0.4,
        type=float)
    argparser.add_argument('-i', '--ignore-hero',action='store_true')
    argparser.add_argument('--move-spectator',action='store_true')
    argparser.add_argument('--spawn-sensors',action='store_true')
    args = argparser.parse_args()


    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(10.0)

        # 设置播放器的时间因子
        client.set_replayer_time_factor(args.time_factor)

        # 设置是否忽略英雄车辆
        client.set_replayer_ignore_hero(args.ignore_hero)

        # set to ignore the spectator camera or not
        client.set_replayer_ignore_spectator(not args.move_spectator)

        # 这里要获取注视点的发送频率
        # last_time = client.show_recorder_file_info(args.recorder_filename, args.show_all)[-50:]
        # last_time = Time_maker.log_get_lasttime(last_time)
        # last_time = float(last_time)

        # 初始化pygame
        display_manager = Set_sensor.DisplayManager(grid_size=[1, 3], window_size=[5740, 1010])

        # 这句话后，开始在UE4里回放轨迹
        print(client.replay_file(args.recorder_filename, args.start, args.duration, args.camera, args.spawn_sensors))

        # 寻找主车
        world = client.get_world()
        vehicles = world.get_actors().filter('vehicle.*')
        print(vehicles)
        vehicle = vehicles.find(217)

        # 前景
        Set_sensor.SensorManager(world, display_manager, 'IS',
                                 carla.Transform(carla.Location(x=2, y=-0.18, z=1.3), carla.Rotation(yaw=+00)),
                                 vehicle, {'fov': '160'}, display_pos=[0, 1], Sp_flag=[[0, 0], [5740, 1010]])
        # 左后视镜
        Set_sensor.SensorManager(world, display_manager, 'IS',
                                 carla.Transform(carla.Location(x=1.5, y=-1, z=1.1), carla.Rotation(yaw=-140)),
                                 vehicle, {}, display_pos=[0, 0], Sp_flag=[[700, 570], [670, 430]])
        # 右后视镜
        Set_sensor.SensorManager(world, display_manager, 'IS',
                                 carla.Transform(carla.Location(x=1.5, y=1, z=1.1), carla.Rotation(yaw=+140)),
                                 vehicle, {}, display_pos=[0, 2], Sp_flag=[[4719, 560], [670, 430]])
        # 正后视镜
        Set_sensor.SensorManager(world, display_manager, 'IS',
                                 carla.Transform(carla.Location(x=-2.2, y=0, z=1.35), carla.Rotation(yaw=+180)),
                                 vehicle, {'fov': '120'}, display_pos=[1, 1], Sp_flag=[[2890, 210], [650, 190]])

        # 设置刷新帧率
        clock = pygame.time.Clock()
        fps = 60

        # 获取注视点映射坐标
        Screen_DF2 = map_eyePoint(HRT_split_path="HRT_data/Mapped_HRT_split.csv")
        # 这里加上你喜欢的颜色
        white = (255, 255, 255)
        # 这是为了辅助读取眼动数据的index，后视镜刷新一次，眼动也渲染一次
        eyepoint_index = 0
        #结束循环的关键旗子
        running = True

        # 最终输出的注视物列表
        Final_list = []

        while running:
            # 退出界面(这里一旦清除，像素值也变了)
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
            display_manager.render()
            # 这里可以改为可视化，也可以改为正式的提取像素值

            # 感受野方法
            try2 = Stare2FeelingArea(display_manager,(int(one_point[0]), int(one_point[1])))

            Final_list.append(try2)
            # 立刻吃一次注视点刷新
            pygame.draw.circle(display_manager.display, white, (one_point[0], one_point[1]), 60)
            pygame.display.flip()

            clock.tick(fps)

        # 存储注视物列表
        dict_index = Scene1.Get_stareobj_index

        # 获取字典值作为列名
        column_names = [dict_index[i] for i in sorted(dict_index.keys())]

        # 创建 DataFrame
        df = pd.DataFrame(Final_list, columns=column_names)

        # 输出 DataFrame 查看结构
        print(df)

        # 保存为 CSV 文件
        csv_file_path = 'Stare_obj_output.csv'
        df.to_csv(csv_file_path, index=False)

        print("注视物CSV文件已保存。")

    finally:
        pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
