import argparse
import re
import json
import os
import time

import requests
import js2py


def run_js(js):
    js_rst = js2py.eval_js(f'var tmp = {js}').to_dict()
    # tmp = js2py.eval_js(f'var tmp = {js};JSON.stringify(tmp)')
    # js_rst = json.loads(tmp)
    return js_rst


# 去掉#开头的注释行
def select_line(line):
    line_new = re.sub(r'^\s+|\s+$', '', line)
    if line_new.startswith('#'):
        return ''
    else:
        return line


def parse_json(filename):
    """
    解析json文件
    """
    rst = []
    file = open(filename, encoding='utf-8')
    all_lines = file.readlines()
    file.close()
    for line in all_lines:
        rst.append(select_line(line))
    result = run_js(''.join(rst))
    return result


def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def download(url: str):
    str_list = url.split('/')
    if len(str_list) > 2:
        direction, file = str_list[-2:]
        dir_path = mkdirs(os.path.join('../../source', direction))
        with open(os.path.join(dir_path, file), 'wb') as f:
            f.write(requests.get(url).content)
        return direction, file
    else:
        raise ValueError(f'can not dir and file from {url}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--input', dest='input', default='', help='json file path')
    parser.add_argument('--output', dest='output', default='', help='json file path')
    args = parser.parse_args()
    input_path = args.input
    output_path = args.output

    js_data = parse_json(input_path)
    for site in js_data['sites']:
        ext = site.get('ext')
        if ext:
            if ext == 'https://freed.yuanhsing.cf/TVBox/MaooXB2/剧白白-蓝光.json':
                site['ext'] = 'https://cdn.staticaly.com/gh/celetor/JK@main/source/MaooXB2/剧白白-蓝光.json'
            elif ext == 'https://freed.yuanhsing.cf/TVBox/MaooXP/jubaibai.json':
                site['ext'] = 'https://cdn.staticaly.com/gh/celetor/JK@main/source/MaooXP/jubaibai.json'
        # if ext and str(ext).startswith('http'):
        #     print(ext)
        #     download(ext)
        #     time.sleep(0.5)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(js_data, f, indent=4, ensure_ascii=False)
