# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 14:30:18 2024

@author: Lenovo
"""

import carla
import argparse
import numpy as np
import pygame
import time

import Set_sensor


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
        default=r'E:\Search_data_package\Alignment_program\Data_program\Log_data\LOG.log',
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

        vehicle = vehicles.find(76)

        # 初始化pygame
        pygame.init()
        pygame.font.init()

        #pygame_display = pygame.display.set_mode([800, 600], pygame.HWSURFACE | pygame.DOUBLEBUF)
        # rgb_camera = world.try_spawn_actor(rgb_camera_bp, rgb_camera_tf, attach_to=ego_vehicle)

        display_manager = Set_sensor.DisplayManager(grid_size=[1, 3], window_size=[500,1300])

        # 前景
        Set_sensor.SensorManager(world,display_manager, 'IS',
                                 carla.Transform(carla.Location(x=20, z=25), carla.Rotation(pitch=-90)),
                                 vehicle, {'fov': '100'}, display_pos=[0, 1], Sp_flag=[[0, 0], [500, 1500]])

        # 设置刷新帧率
        clock = pygame.time.Clock()
        fps = 60

        running = True
        while running:
            # pygame
            # pygame渲染刷新
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            # end of own scripts

            # Render received data
            display_manager.render()
            clock.tick(fps)
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
