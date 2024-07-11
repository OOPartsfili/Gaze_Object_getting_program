文件是有命名规范的,方便路径读取:
Carla_data的名称改为DATA
HRT_data的名称改为HRT
Log_data的名称改为LOG
asset的名称，屏幕图改为SCREEN


先运行Eye_maker进行整体数据滤波  # 在眼动数据大改进前需要做
再运行Split_by_log进行log文件分割

'''
replay是为了截图输入pixel_maker中，这里物体与config里要一一对应
再运行Pixel_maker获得目标图像对应的像素值(关键是obj_pixel_table.csv)
'''

运行Get_pixel_obj_table，检查screenshot图像，自动生成像素-物体对应表格

将屏幕截图的白边切去
再运行picture_maker，将屏幕截图变为（1920X1080）
再运行Mappoint_maker 进行注视点坐标映射，这里一定要检查截图的像素是不是改为（1920X1080）

最后运行replay_get_piexlV2，获取注视点可视化/感受野注视物列表