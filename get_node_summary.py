# -*- coding: utf-8 -*-

import json
import math
from get_cookie import get_cookie
from tools import *
from operation_time_calculator import Operation, OperationQueueList


def node_summary_tmp(cookie, fd_id, page_number):
    data = http_get(cookie, PARAMS_URL_NODE_SUMMARY.format(fd_id, str(page_number)))
    data_json = json.loads(data)
    # print(json.dumps(data_json, indent=4, ensure_ascii=False))
    result = pd.DataFrame({
        STRING_CN_RECEIVE_TIME: [x[0][STRING_VALUE] for x in data_json[STRING_DATAS]],
        STRING_CN_HANDLE_TIME: [x[1][STRING_VALUE] for x in data_json[STRING_DATAS]],
        STRING_CN_NODE: [x[2][STRING_VALUE] for x in data_json[STRING_DATAS]],
        STRING_CN_FD_NAME: [clear_name(x[3][STRING_VALUE]) for x in data_json[STRING_DATAS]],
        STRING_CN_HANDLE: [clear(x[4][STRING_VALUE]) for x in data_json[STRING_DATAS]],
        STRING_CN_SYSTEM_HANDLE: [x[5][STRING_VALUE] for x in data_json[STRING_DATAS]]
    })
    result.drop(result[result[STRING_CN_RECEIVE_TIME] == STRING_EMPTY].index, inplace=True)
    result.drop(result[result[STRING_CN_HANDLE_TIME] == STRING_EMPTY].index, inplace=True)
    result[STRING_CN_RECEIVE_TIME_TMP] = [
        datetime.datetime.combine((
            pd.to_datetime(x) + datetime.timedelta(days=1)).date(),
            datetime.time(hour=8, minute=0, second=0)) if (pd.to_datetime(x).hour in [22, 23]) else x
        for x in result[STRING_CN_RECEIVE_TIME]]
    result[STRING_CN_RECEIVE_TIME_TMP] = [
        datetime.datetime.combine(pd.to_datetime(x).date(), datetime.time(hour=8, minute=0, second=0))
        if (pd.to_datetime(x).hour in [0, 1, 2, 3, 4, 5, 6, 7]) else x for x in result[STRING_CN_RECEIVE_TIME_TMP]]
    result[STRING_CN_DEAL_TIME_PERIOD_TMP] = \
        pd.to_datetime(result[STRING_CN_HANDLE_TIME]) - pd.to_datetime(result[STRING_CN_RECEIVE_TIME_TMP])
    result[STRING_CN_DEAL_TIME_PERIOD_TMP] = [
        round(x.total_seconds() / 3600, 4) for x in result[STRING_CN_DEAL_TIME_PERIOD_TMP]]
    result[STRING_CN_DEAL_TIME_PERIOD] = [max(y, 0) for y in result[STRING_CN_DEAL_TIME_PERIOD_TMP]]
    del result[STRING_CN_RECEIVE_TIME_TMP], result[STRING_CN_DEAL_TIME_PERIOD_TMP]
    return result, math.ceil(
        int(data_json[STRING_PAGE][STRING_TOTAL_SIZE]) / float(int(data_json[STRING_PAGE][STRING_PAGE_SIZE])))


def get_node_summary(cookie, fd_id):
    page_number = 1
    res_df, page_count = node_summary_tmp(cookie, fd_id, page_number)
    while page_number < page_count:
        page_number += 1
        temp, tmp = node_summary_tmp(cookie, fd_id, page_number)
        res_df = pd.concat([res_df, temp])
    # 202106新增operation_time_calculator来计算节点时间
    res_df[STRING_CN_DEAL_TIME_PERIOD_OLD] = res_df[STRING_CN_DEAL_TIME_PERIOD]
    operations = [
        Operation(node_name, start_time, end_time, handler, operation_name, origin_id) for
        node_name, start_time, end_time, handler, operation_name, origin_id in zip(
            res_df[STRING_CN_NODE],
            res_df[STRING_CN_RECEIVE_TIME],
            res_df[STRING_CN_HANDLE_TIME],
            res_df[STRING_CN_FD_NAME],
            res_df[STRING_CN_HANDLE],
            range(len(res_df))
        )
    ]
    oql = OperationQueueList(operations)
    res_df[STRING_CN_REAL_START_TIME] = oql.list_real_start_time
    res_df[STRING_CN_DEAL_TIME_PERIOD] = oql.list_pure_time
    res_df[STRING_CN_FD_ID] = [fd_id] * len(res_df)
    res_df = res_df[[
        STRING_CN_FD_ID,
        STRING_CN_NODE,
        STRING_CN_FD_NAME,
        STRING_CN_HANDLE,
        STRING_CN_SYSTEM_HANDLE,
        STRING_CN_RECEIVE_TIME,
        STRING_CN_HANDLE_TIME,
        STRING_CN_REAL_START_TIME,
        STRING_CN_DEAL_TIME_PERIOD_OLD,
        STRING_CN_DEAL_TIME_PERIOD,
    ]]
    res_df = res_df.reset_index(drop=True)
    return res_df.reset_index(drop=True)


if __name__ == "__main__":
    c = "JSESSIONID=7D42AC2340A5D0FD415911113520EA05;"
    c = get_cookie(PARAMS_URL_OA, PARAMS_OA_USERNAME, PARAMS_OA_PASSWORD, r"D:\Workspace\FBR\code\fbr_server\chromedriver")

    df = get_node_summary(c, "17824f1aa269bc98ff17a6a4f739fc98")
    # pd.set_option('display.max_rows', 500)
    # pd.set_option('display.max_columns', 500)
    # pd.set_option('display.width', 1000)
    # print(df)
    #
    # df = node_summary_tmp(c, "17824f1aa269bc98ff17a6a4f739fc98", 1)
    print_df(df)
    # data_json = json.loads(data)
    # print(json.dumps(data_json, indent=4, ensure_ascii=False))

