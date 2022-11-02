import os
import re
import datetime

import openpyxl


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def get_month(path):
    file = os.path.basename(path)
    matcher = re.search(r'(\d+)月', file)
    if matcher:
        month = matcher.group(1)
        return month
    else:
        return None


def get_name_sheet(sh, row_count, name):
    # 姓名的行列
    name_info = (0, 0)
    for y in range(2, row_count):
        for x in range(1, 5):
            if sh.cell(row=y, column=x).value == name:
                name_info = (x, y)
                break
    return name_info


def read_excel(path, name, sheet=None):
    # 打开工作簿
    workbook = openpyxl.load_workbook(path)
    if sheet is None:
        for sheet_name in workbook.sheetnames:
            if str(sheet_name).find('工时') > -1:
                continue
            # 获取表单
            sh = workbook[sheet_name]
            name_info = get_name_sheet(sh, sh.max_row, name)
            if name_info[0] > 0 and name_info[1] > 0:
                sheet = sheet_name
                break

    sh = workbook[sheet]
    row_count = sh.max_row  # 有效数据行数
    col_count = sh.max_column  # 有效数据列数

    # 姓名的行列
    name_info = get_name_sheet(sh, row_count, name)
    # 日期的行列
    date_info = (0, 0)
    for y in range(2, row_count):
        for x in range(1, 5):
            if str(sh.cell(row=y, column=x).value).find('日期') > -1:
                date_info = (x, y)
                break

    # 获取月份
    month = get_month(path)
    if not month:
        month = get_month(sh.cell(row=1, column=1).value)

    work_info = []
    for x in range(name_info[0] + 1, col_count):
        day = str(sh.cell(row=date_info[1], column=x).value)
        if is_int(day):
            month = month if len(month) > 1 else f'0{month}'
            day = day if len(day) > 1 else f'0{day}'
            work_info.append({
                'month': month,
                'day': day,
                'state': sh.cell(row=name_info[1], column=x).value
            })
    return work_info


def main(path, name, sheet=None):
    work_list = read_excel(path, name, sheet)
    ical = f"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:PUBLISH
PRODID:Celetor
X-WR-CALNAME:{int(work_list[0]['month'])}月排班表"""

    for work in work_list:
        title = work['state']
        if title == '☆':
            continue
        elif title == 'E':
            start_hms = '09:00:00'
            end_hms = '21:30:00'
        elif title == 'D':
            start_hms = '09:00:00'
            end_hms = '18:00:00'
        elif title == 'G':
            start_hms = '13:30:00'
            end_hms = '18:00:00'
        elif title == 'H':
            start_hms = '13:30:00'
            end_hms = '21:30:00'
        else:
            start_hms = '00:00:00'
            end_hms = '00:00:00'
        year = datetime.date.today().strftime('%Y')
        date = f'{year}/{work["month"]}/{work["day"]}'
        start_time_cn = f'{date}T{start_hms}'
        start_time_utc = datetime.datetime.strptime(start_time_cn, '%Y/%m/%dT%H:%M:%S') - datetime.timedelta(hours=8)
        start_time = start_time_utc.strftime('%Y%m%dT%H%M%SZ')
        end_time_cn = f'{date}T{end_hms}'
        end_time_utc = datetime.datetime.strptime(end_time_cn, '%Y/%m/%dT%H:%M:%S') - datetime.timedelta(hours=8)
        end_time = end_time_utc.strftime('%Y%m%dT%H%M%SZ')

        description = f'打工时间：{start_hms[:-3]}～{end_hms[:-3]}\\n注意：周五、周六或节假日22:00闭店'
        ical += f'''
BEGIN:VEVENT
SUMMARY:{title}班
UID:{start_time}
DTSTART:{start_time}
DTEND:{end_time}
DESCRIPTION:{description}
END:VEVENT'''

    ical += '''
END:VCALENDAR'''
    with open('./s-work.ics', 'w', encoding='utf-8') as f:
        f.write(ical)


if __name__ == "__main__":
    main(r'D:/附件1：11月计划排班.xlsx', '姓名')
