
from datetime import datetime
import re


# 输入一个17位时间戳（int）
# 输出一个毫秒级正常时间数据（str）
def timestamp2local_time_with_ms(timestamp):
    # 将时间戳转换为10位
    timestamp = timestamp/10000000
    local_time = datetime.fromtimestamp(timestamp)
    ms = timestamp % 1
    return local_time.strftime('%Y-%m-%d %H:%M:%S') + f'.{int(ms * 1000):03d}'


# 将log文件中时间文字转变为17位时间戳
# 输入log文件夹中的时间(str)
# 输出一个17位时间戳（int）
def local_time2timestamp(log_str = "03/29/24 21:58:08"):
    # 输入时间的格式
    input_time_format = "%m/%d/%y %H:%M:%S"

    # 将输入的时间字符串转换为datetime对象
    input_time = datetime.strptime(log_str, input_time_format)
    # 因为时间戳是基于UTC的，确保转换后的时间也是UTC
    input_time = input_time.replace()
    # 将datetime对象转换为毫秒级时间戳
    timestamp_ms = int(input_time.timestamp() * 10000000)
    return timestamp_ms



# log文件有时候并不规则，需要用正则提取所需文本
# 输入log文件开头的部分
# 输出log文件开头里的日期部分
def log_get_begintime(head):
    # 使用正则表达式匹配日期和时间信息
    date_pattern = r"Date: (\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})"
    date_match = re.search(date_pattern, head)

    # 提取并打印完整的日期和时间信息
    if date_match:
        date_time_info = date_match.group(1)
    else:
        print("log文件出错，寄了")
    return date_time_info

# 提取log文件结尾的持续时间数据
# 输入log文件结尾的部分
# 输出一个持续时间str
def log_get_lasttime(tail):
    duration_pattern = r"Duration: ([\d.]+) seconds"
    duration_match = re.search(duration_pattern, tail)

    # 提取并打印持续时间秒数
    if duration_match:
        duration_seconds = duration_match.group(1)
    else:
        print("log文件出错，寄了")
    return duration_seconds


if __name__ == "__main__":
    timestamp = 17117208568227251
    result = local_time2timestamp()
    result2 = timestamp2local_time_with_ms(result)

    print(result)
    print(result2)



