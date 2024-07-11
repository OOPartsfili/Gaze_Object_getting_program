import carla

# 位置信息
main_vehicle_location = carla.Location(x=-842.352051, y=-291.25)  # 主车位置



# 接管终点
start_location = carla.Location(x=-317, y=-295, z=2 )
end_location = carla.Location(x=-317, y=-283, z=2 )

# 数据记录信息
dict_index = {
    0: "main_car",
    1: "vice_car_L1_1",
    2: "vice_car_L1_2",
    3: "vice_car_L2_1",
    4: "vice_car_L3_1"
}

# 针对log回放的记录信息
Get_stareobj_index = {
    0: "vice_car_L1_1",
    1: "vice_car_L1_2",
    2: "vice_car_L2_1",
    3: "vice_car_L3_1",
    4: "obstacle"
}


# dict_0 是CSV文件的关键
dict_0 = {"time": []}

file_name1 = 'carla_data/data03.csv'
file_name2 = 'carla_data/data03_ARHUD.csv'