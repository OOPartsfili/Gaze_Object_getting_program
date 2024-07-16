#!/usr/bin/env python
"""
运行这个文件，先在HRT文件里放好HRT输出的CSV
再在文件目录下放上对应的log文件

运行好后，相当于利用log的接管开始-结束时间戳从HRT的CSV里提取出需要的接管眼动数据HRT-split

"""

from util import Time_maker
import carla
import argparse
import pandas as pd


#将眼动数据提取出来
# 输入HRT文件路径，log的两个时间变量
# 输出 一个分割好的CSV文件(直接输出，不返回)
def split_SMA(file_path, begin_takeover_timestamp, end_takeover_timestamp):
    #读取HRT文件
    data = pd.read_csv(file_path)
    filtered_data = data[(data['StorageTime'] > begin_takeover_timestamp) & (data['StorageTime'] < end_takeover_timestamp)]

    # 提取ScreenPoint_x和ScreenPoint_y数据
    screen_points = filtered_data[['ScreenPoint2D_x', 'ScreenPoint2D_y']]
    screen_points.to_csv('../SMA_data/SMA_split.csv', index=False)
    # print(type(screen_points))


#将风险场数据提取出来
# 输入recording文件路径，log的两个时间变量
# 输出 一个分割好的CSV文件(直接输出，不返回)
def split_recording(file_path,begin_takeover_timestamp,end_takeover_timestamp):
    #读取recording文件
    data = pd.read_csv(file_path, encoding='utf-8')
    filtered_data = data[(data['time']  *1000 > begin_takeover_timestamp) & (data['time'] *1000 < end_takeover_timestamp)]

    # 提取ScreenPoint_x和ScreenPoint_y数据
    filtered_data.to_csv('../Carla_data/Recording_split.csv', index=False)

    # print(type(screen_points))



def main():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '-f', '--recorder_filename',
        metavar='F',
        default=r"E:\Search_data_package\Alignment_program\Gaze_Object_getting_program\Log_data\LOG.log",
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
        '-a', '--show_all',
        action='store_true',
        help='show detailed info about all frames content')
    argparser.add_argument(
        '-s', '--save_to_file',
        metavar='S',
        help='save result to file (specify name and extension)')

    args = argparser.parse_args()


    try:

        client = carla.Client(args.host, args.port)
        client.set_timeout(10.0)
        # 如果args.save_to_file这个东西存在
        if args.save_to_file:
            doc = open(args.save_to_file, "w+")
            doc.write(client.show_recorder_file_info(args.recorder_filename, args.show_all))
            doc.close()
        # 如果不存在
        else:
            # 截取时间数据
            # print(client.show_recorder_file_info(args.recorder_filename, args.show_all))

            #begin_Takeover是开始时间戳的str数据
            begin_takeover = client.show_recorder_file_info(args.recorder_filename, args.show_all)[:50]
            # print(begin_takeover)
            begin_takeover = Time_maker.log_get_begintime(begin_takeover)
            # print(begin_takeover)


            #last_time是持续时间的str数据
            last_time = client.show_recorder_file_info(args.recorder_filename, args.show_all)[-50:]
            last_time = Time_maker.log_get_lasttime(last_time)
            print(last_time)
            last_time = float(last_time)

            #这里接管开始和结束的13位时间戳，都是int数据
            begin_takeover_timestamp = Time_maker.local_time2timestamp(begin_takeover)
            end_takeover_timestamp = begin_takeover_timestamp + round(last_time * 1000)

            # 这里已经吃到了两个关键数据
            print(begin_takeover_timestamp,end_takeover_timestamp)


            SMAfile_path = '../SMA_data/SMA_processed.csv'
            Carlafile_path = '../Carla_data/DATA.csv'

            #开始分割HRT数据
            split_SMA(SMAfile_path, begin_takeover_timestamp, end_takeover_timestamp)

            #开始分割carla车辆信息数据
            split_recording(Carlafile_path,  begin_takeover_timestamp,end_takeover_timestamp)


    finally:
        pass



if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
