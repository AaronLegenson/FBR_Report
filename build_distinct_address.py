# -*- coding: utf-8 -*-

import requests
import time
import urllib3
import json
import re
import math
import datetime
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from strings import *
from parameters import *
from get_cookie import get_cookie
from tools import *
from build_address import build_address


def deal_path(string):
    paths = string.split("/")
    path_result = ""
    for path in paths:
        if path in PARAMS_ALL_DEPARTMENTS:
            path_result += path
    if path_result == "":
        return None
    return path_result


def build_distinct_address(cookie, src_df):
    # src_df = build_address(cookie, file_name)
    # src_df = pd.read_excel(src_df)
    src_df.drop(src_df[(src_df["node_type"] == "2") | (src_df["node_type"] == 2)].index, inplace=True)
    src_df["department"] = [deal_path(x) for x in src_df["path"]]
    src_df["combo"] = [deal_path(x) for x in src_df["path"]]
    terrible_pairs = [
        ["刘明", "技术开发部"],
        ["汤平", "集团董事长办公室"],
        ["汤平", "综合管理部"],
        ["李万林", "集团董事长办公室"],
        ["陆昕卉", "集团董事长办公室"],
        ["杨虹", "综合管理部"]
        
    ]
    for item in terrible_pairs:
        src_df.drop(src_df[(src_df["name"] == item[0]) & (src_df["department"] == item[1])].index, inplace=True)
    src_df.dropna(subset=["department"], inplace=True)
    abnormal_pairs = [
        ["邵平", "公司总经理"],
        ["公司总经理", "公司总经理"],
        ["首席大数据官", "增值服务业务部"],
        ["首席运营官", "运营管理部"],
        ["首席财务官", "计划财务部"],
        ["首席技术官", "技术开发部"],
        ["数字风控部总经理", "数字风控部"],
        ["财务总经理", "计划财务部"],
        ["青岛聚量融资租赁有限公司CEO", "金融机构合作首席代表张俊涛团队"],
        ["风险合规中心总经理", "金融机构合作首席代表刘志刚团队"],
        ["合规风控审核人", "金融机构合作首席代表孟庆波团队"],
        ["聚量保理总裁", "金融机构合作首席代表沈彦炜团队"],
        ["集团办公室主任", "集团董事长办公室"],
        ["档案管理负责人", "综合管理部"],
        ["运营中心审核", "运营管理部"],
        ["财务审核", "计划财务部"],
        ["汤平_运维", "技术开发部"],
        ["产业物流赋能事业部项目总监", "金融机构合作首席代表刘明团队"],
        ["刘明2", "技术开发部"]
    ]
    for item in abnormal_pairs:
        src_df = src_df.append([{"name": item[0], "department": item[1]}], ignore_index=True)
    banned_pairs = [
        ["杨路", "（已禁用）"],
        ["杨冬华", "（已禁用）"],
        ["封心方", "（已禁用）"],
        ["刘笑影", "（已禁用）"],
        ["张京", "（已禁用）"],
        ["潘滋茂", "（已禁用）"],
        ["刘乔乔", "（已禁用）"],
        ["钱金金", "（已禁用）"]
    ]
    for item in banned_pairs:
        src_df = src_df.append([{"name": item[0], "department": item[1]}], ignore_index=True)
    src_df = src_df.sort_values(by="name", ascending=True)
    src_df.rename(columns={"name": "姓名", 'department': "部门"}, inplace=True)
    src_df = src_df[["姓名", "部门"]]
    src_df.drop_duplicates(inplace=True)
    src_df = src_df.reset_index(drop=True)
    
    # src_df.to_excel("address.xlsx")
    return src_df
    

if __name__ == "__main__":
    c = "JSESSIONID=7D42AC2340A5D0FD415911113520EA05;"
    df = build_distinct_address(c, "address_tree.xlsx")
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    print(df)
    # data_json = json.loads(data)
    # print(json.dumps(data_json, indent=4, ensure_ascii=False))
