# -*- coding: utf-8 -*-

import json
import re
import math
from tools import *


def directories_tmp(cookie, page_number):
    data = http_get(cookie, PARAMS_URL_DIRECTORIES.format(str(page_number)))
    data_json = json.loads(data)
    fd_id = [x[0][STRING_VALUE] for x in data_json[STRING_DATAS]]  # 流程id
    doc_subject = [re.findall(">.*?</span>", x[1][STRING_VALUE])[0][1: -7] for x in data_json[STRING_DATAS]]  # 主题
    fd_number = [x[2][STRING_VALUE] for x in data_json[STRING_DATAS]]  # 申请单编号
    fd_use_word = [x[3][STRING_VALUE] for x in data_json[STRING_DATAS]]  # 启用Word
    # fd_name = [x[4][STRING_VALUE] for x in data_json[STRING_DATAS]]  # 申请人
    # doc_create_time = [x[5][STRING_VALUE] for x in data_json[STRING_DATAS]]  # 创建日期
    doc_create_time_time = [x[6][STRING_VALUE] for x in data_json[STRING_DATAS]]  # 创建时间
    # doc_publish_time = [x[7][STRING_VALUE] for x in data_json[STRING_DATAS]]  # 结束日期
    doc_publish_time_time = [x[8][STRING_VALUE] for x in data_json[STRING_DATAS]]  # 结束时间
    fd_is_filing = [x[9][STRING_VALUE] for x in data_json[STRING_DATAS]]  # 是否归档
    doc_status = [x[10][STRING_VALUE] for x in data_json[STRING_DATAS]]  # 文档状态
    # arrival_time = [clear(re.findall(">.*?</div>", x[11][STRING_VALUE])[0][1: -6]) for x in data_json[STRING_DATAS]]
    # 送审时间
    node_name = [clear(re.findall(">.*?</div>", x[12][STRING_VALUE])[0][1: -6]) for x in data_json[STRING_DATAS]]
    # 当前环节
    handler_name = [clear(re.findall(">.*?</div>", x[13][STRING_VALUE])[0][1: -6]) for x in data_json[STRING_DATAS]]
    # 当前处理人
    dfs = pd.DataFrame({
        STRING_CN_FD_ID: fd_id,
        STRING_CN_DOC_SUBJECT: doc_subject,
        STRING_CN_FD_NUMBER: fd_number,
        STRING_CN_FD_USE_WORD: fd_use_word,
        # STRING_CN_DOC_CREATE_TIME: doc_create_time,
        STRING_CN_DOC_CREATE_TIME_TIME: doc_create_time_time,
        # STRING_CN_DOC_PUBLISH_TIME: doc_publish_time,
        STRING_CN_DOC_PUBLISH_TIME_TIME: doc_publish_time_time,
        STRING_CN_FD_IS_FILING: fd_is_filing,
        STRING_CN_DOC_STATUS: doc_status,
        # STRING_CN_ARRIVAL_TIME: arrival_time,
        STRING_CN_NODE_NAME: node_name,
        STRING_CN_HANDLER_NAME: handler_name
    })
    return dfs, math.ceil(
        int(data_json[STRING_PAGE][STRING_TOTAL_SIZE]) / float(int(data_json[STRING_PAGE][STRING_PAGE_SIZE])))


def get_directories(cookie):
    page_number = 1
    res_df, page_count = directories_tmp(cookie, page_number)
    while page_number < page_count:
        page_number += 1
        tmp_df, tmp = directories_tmp(cookie, page_number)
        res_df = pd.concat([res_df, tmp_df])
    return res_df.reset_index(drop=True)


if __name__ == "__main__":
    c = "JSESSIONID=495AD2EA259755BB8375D461505CB7A9;"
    # c = get_cookie(PARAMS_URL_OA, PARAMS_OA_USERNAME, PARAMS_OA_PASSWORD)
    res = get_directories(c)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    print(res)
    # df = get_directories(c)
    # df = df.reset_index(drop=True)
    # df.to_excel("1.xlsx")


