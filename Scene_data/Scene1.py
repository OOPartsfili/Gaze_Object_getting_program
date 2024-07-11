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



Get_stareobj_index = {

    0: "Car1",
    1: "Car2",
    2: "Car3",
    3: "Car4",
    4: "main_car",
    5: "Car5",
    6: "Car6",
    7: "Car7",
    8: "Car8",
    9: "Car9_Obs",
}