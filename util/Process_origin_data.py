import pandas as pd
import ast

# 读取CSV文件
file_path = '../SMA_data/SMA.csv'
df = pd.read_csv(file_path)

# 定义默认值
default_value = {
    'WorldPoint': {'x': 0, 'y': 0, 'z': 0},
    'ObjectPoint': {'x': 0, 'y': 0, 'z': 0},
    'ObjectName': 'ScreenMiddle'
}

# 定义一个函数来解析字典字符串
def parse_dict_string(dict_string):
    try:
        return ast.literal_eval(dict_string)
    except (ValueError, SyntaxError):
        return None

# 解析FilteredClosestWorldIntersection列的字典字符串
df['FilteredClosestWorldIntersection'] = df['FilteredClosestWorldIntersection'].apply(parse_dict_string)

# 处理第一行数据
def process_first_row(row):
    if row is None:
        return default_value
    elif not row.get('ObjectName'):
        row['ObjectName'] = 'ScreenMiddle'
    return row

df.at[0, 'FilteredClosestWorldIntersection'] = process_first_row(df.loc[0, 'FilteredClosestWorldIntersection'])

# 处理后续行数据
for i in range(1, len(df)):
    prev_row = df.loc[i - 1, 'FilteredClosestWorldIntersection']
    current_row = df.loc[i, 'FilteredClosestWorldIntersection']

    if current_row is None:
        df.at[i, 'FilteredClosestWorldIntersection'] = prev_row
    else:
        if not current_row.get('ObjectName'):
            current_row['ObjectName'] = prev_row.get('ObjectName')
        if 'ObjectPoint' not in current_row:
            current_row['ObjectPoint'] = prev_row.get('ObjectPoint', {'x': 0, 'y': 0, 'z': 0})
        df.at[i, 'FilteredClosestWorldIntersection'] = current_row

# 提取并处理ObjectPoint的x、y坐标
def extract_screen_point(row):
    object_point = row['ObjectPoint']
    x, y = object_point['x'], object_point['y']
    if row['ObjectName'] == 'ScreenMiddle':
        x += 1920
    elif row['ObjectName'] == 'ScreenRight':
        x += 3840
    return pd.Series({'ScreenPoint2D_x': x, 'ScreenPoint2D_y': y})

# 新增ScreenPoint2D_x和ScreenPoint2D_y列
df[['ScreenPoint2D_x', 'ScreenPoint2D_y']] = df['FilteredClosestWorldIntersection'].apply(extract_screen_point)

# 将处理后的数据写入新的CSV文件
output_file_path = '../SMA_data/SMA_processed.csv'
df.to_csv(output_file_path, index=False)
