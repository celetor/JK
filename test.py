import time
import datetime
year = datetime.date.today().strftime('%Y')
start_time_cn = '2022/11/02T20:30:00'
start_time_timestamp = time.strptime(start_time_cn, '%Y/%m/%dT%H:%M:%S')
start_time_utc = datetime.datetime.strptime(start_time_cn, '%Y/%m/%dT%H:%M:%S') - datetime.timedelta(hours=8)
start_time_utc = start_time_utc.strftime('%Y/%m/%dT%H:%M:%S')
print(start_time_timestamp)
print(start_time_timestamp2)
