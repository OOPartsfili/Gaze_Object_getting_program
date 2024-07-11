'''
由于 carla的数据会比眼动数据少几行，这里专门进行数据扩充，保证两者行数一致

'''


import pandas as pd

# 加载CSV文件
recording_split_df = pd.read_csv('../Carla_data/Recording_split.csv')
hrt_split_df = pd.read_csv('../HRT_data/HRT_split.csv')

# 计算每个数据框的行数
num_rows_recording = len(recording_split_df)
num_rows_hrt = len(hrt_split_df)

# 计算需要插入的行数
rows_to_insert = num_rows_hrt - num_rows_recording

# 定义插入行的函数
def insert_rows(df, num_rows_to_insert):
    interval = len(df) // (num_rows_to_insert + 1)
    for i in range(1, num_rows_to_insert + 1):
        insertion_index = i * interval
        new_row = (df.iloc[insertion_index - 1] + df.iloc[insertion_index]) / 2
        df = pd.concat([df.iloc[:insertion_index], new_row.to_frame().T, df.iloc[insertion_index:]]).reset_index(drop=True)
    return df

# 插入必要的行
expanded_recording_split_df = insert_rows(recording_split_df, rows_to_insert)

# 保存扩充后的数据框为新的CSV文件
expanded_recording_split_df.to_csv('../Carla_data/Recording_split_expanded.csv', index=False)
