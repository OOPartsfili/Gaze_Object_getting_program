
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# 计算两点的距离
def calculate_distance(point1, point2):
    """计算两点之间的欧几里得距离"""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# 计算所有点对的距离
def calculate_all_distances(points):
    distances = [calculate_distance(points[i], points[i+1]) for i in range(len(points)-1)]
    return distances

# 读取点的数据，变为[(23, 66), (24, 68), (26, 69), (30, 75), (56, 120)]的格式
def read_point(file_path):
    # 读取CSV文件
    data = pd.read_csv(file_path)
    # 提取ScreenPoint_x和ScreenPoint_y数据
    screen_points = data[['ScreenPoint2D_x', 'ScreenPoint2D_y']]
    # 将DataFrame的两列转换为列表的元组
    point_list = [(x, y) for x, y in zip(screen_points['ScreenPoint2D_x'], screen_points['ScreenPoint2D_y'])]
    # print(point_list)
    # 返回点列表
    return point_list


# 获取注视、扫视的距离阈值(最基础的算法)
# 输出一个阈值
def get_threshold(gaze_points):
    # 所有点间距离计算
    distances = calculate_all_distances(gaze_points)
    # print(distances[:30])
    # 计算距离的75分位数作为阈值
    threshold = np.percentile(distances, 90)

    # # 计算聚类中心的平均数作为阈值
    # threshold = np.mean(centers)

    print("注视距离阈值为:", threshold)

    # 绘制距离分布(艺术化处理，剔除异常值)
    distances2 = [i for i in distances if i<20000]
    plt.hist(distances2, bins=150, alpha=0.7, label='Distances')
    plt.axvline(x=threshold, color='r', linestyle='--', label=f'Threshold = {threshold:.2f}')
    plt.xlabel('Distance')
    plt.ylabel('Frequency')
    plt.title('Distance Distribution and Threshold')
    plt.legend()
    plt.show()

    return threshold

"""
    对眼动轨迹进行注视和扫视的分类。
    :param points: 列表，包含眼动的(x, y)坐标点
    :param distance_threshold: 两点间距离小于此值视为注视，否则视为扫视
    :return: 带有标签的列表，标签为'Fixation'或'Saccade'
"""
def classify_gaze(points, distance_threshold):
    labels = ['Start']  # 初始点，可以特殊处理或标记为任意一类
    for i in range(1, len(points)):
        distance = calculate_distance(points[i - 1], points[i])
        if distance < distance_threshold:
            labels.append('Fixation')
        else:
            labels.append('Saccade')
    return list(zip(points, labels))



# 进行眼动数据的平均处理（平滑滤波）
def average_fixation_points(points):
    result = []
    temp_points = []

    # Helper function to calculate average of points
    def calculate_average(sub_points):
        if not sub_points:
            return []
        avg_x = sum(x for x, y in sub_points) / len(sub_points)
        avg_y = sum(y for x, y in sub_points) / len(sub_points)
        return [((round(avg_x), round(avg_y)), 'Fixation') for _ in sub_points]

    # Iterate over points to group and process fixation points
    for (x, y), label in points:
        if label == 'Fixation':
            temp_points.append((x, y))
            # Process in batches of 5
            if len(temp_points) == 5:
                result.extend(calculate_average(temp_points))
                temp_points = []
        else:
            # Process any remaining fixation points before a saccade
            if temp_points:
                result.extend(calculate_average(temp_points))
                temp_points = []
            # Add saccade points as they are
            result.append(((x, y), label))

    # Make sure to process any remaining fixation points after the last saccade or at end of list
    if temp_points:
        result.extend(calculate_average(temp_points))

    return result


# 主函数
# 输出[((310, 496), 'Fixation'), ((310, 496), 'Fixation'), ((310, 496), 'Fixation')]这种格式的数据

def Eye_points_filter(file_path):
    # 数据读取
    gaze_points = read_point(file_path)
    threshold = get_threshold(gaze_points)
    # 这里taged_points【((517, 464), 'Fixation'), ((520, 486), 'Fixation')】
    taged_points = classify_gaze(gaze_points, threshold)
    ave_taged_points = average_fixation_points(taged_points)

    # return(ave_taged_points)



if __name__ == '__main__':
    file_path = '../SMA_data/SMA_processed.csv'

    # 数据读取
    gaze_points = read_point(file_path)
    threshold = get_threshold(gaze_points)
    # 这里taged_points【((517, 464), 'Fixation'), ((520, 486), 'Fixation')】
    taged_points = classify_gaze(gaze_points, threshold)

    ave_taged_points = average_fixation_points(taged_points)

    # print(ave_taged_points)
    # 创建DataFrame
    df = pd.DataFrame(ave_taged_points, columns=['ScreenPoint', 'Status'])
    # 拆分ScreenPoint列为两个单独的列
    df[['ScreenPoint_x', 'ScreenPoint_y']] = pd.DataFrame(df['ScreenPoint'].tolist(), index=df.index)
    # 删除原始的ScreenPoint列
    df.drop('ScreenPoint', axis=1, inplace=True)
    # 调整列顺序
    df = df[['ScreenPoint_x', 'ScreenPoint_y', 'Status']]

    data = pd.read_csv(file_path)


    df['StorageTime'] = data[['StorageTime']]

    # 输出DataFrame为CSV文件
    csv_filename = '../SMA_data/Filtered_data.csv'
    df.to_csv(csv_filename, index=False)


