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


def dfs_address(cookie, row, p):
    # print("path =", p)
    # data = get_team(cookie, row["person_id"])
    data = http_get(
        cookie,
        PARAMS_URL_BUILD_ADDRESS.format(row["person_id"]))
    # print(data)
    soup = BeautifulSoup(data, "lxml")

    person_id = [x.attrs.get("id") for x in soup.find_all("data")]
    name = [x.attrs.get("name") for x in soup.find_all("data")]
    parent_id = [x.attrs.get("parentid") for x in soup.find_all("data")]
    node_type = [x.attrs.get("nodetype") for x in soup.find_all("data")]
    is_leader = [x.attrs.get("isleader") for x in soup.find_all("data")]
    length = len(person_id)
    leader = [None] * length
    path = [p] * length
    src_df = pd.DataFrame({
        "person_id": person_id,
        "name": name,
        "parent_id": parent_id,
        "node_type": node_type,
        "is_leader": is_leader,
        "leader": leader,
        "path": path
    })
    tmp_leader = None
    # res_df = src_df.copy(deep=True)
    res_df = pd.DataFrame(columns=["person_id", "name", "parent_id", "node_type", "is_leader", "leader", "path"])
    for index, row in src_df.iterrows():
        if row.get("node_type") == "2":
            ld, tmp_df = dfs_address(cookie, row, "{0}/{1}".format(p, row.get("name")))
            row["leader"] = ld
            row["path"] = p
            res_df = res_df.append([row], ignore_index=True)
            res_df = pd.concat([res_df, tmp_df])
        elif row.get("node_type") == "8":
            row["path"] = p
            res_df = res_df.append([row], ignore_index=True)
        if row.get("is_leader") == "true":
            tmp_leader = row["name"]
    return tmp_leader, res_df.reset_index(drop=True)


def build_address(cookie):
    person_id = ['1674444bc07af32cd851f5849bf9bbcd', '16a24fb84348b2ba056959b49e5a25be']
    name = ['聚均科技', '集团董事长办公室']
    parent_id = ['root', 'root']
    node_type = ['2', '2']
    is_leader = [None, None]
    leader = [None, None]
    path = ["", ""]
    src_df = pd.DataFrame({
        "person_id": person_id,
        "name": name,
        "parent_id": parent_id,
        "node_type": node_type,
        "is_leader": is_leader,
        "leader": leader,
        "path": path
    })
    # res_df = src_df.copy(deep=True)
    res_df = pd.DataFrame(columns=["person_id", "name", "parent_id", "node_type", "is_leader", "leader", "path"])
    for index, row in src_df.iterrows():
        if row.get("node_type") == "2":
            ld, tmp_df = dfs_address(cookie, row, "/{0}".format(row.get("name")))
            row["leader"] = ld
            res_df = res_df.append([row], ignore_index=True)
            res_df = pd.concat([res_df, tmp_df])
    res_df = res_df.reset_index(drop=True)
    # res_df.to_excel(file_name)
    return res_df
    

if __name__ == "__main__":
    c = "JSESSIONID=9424AD80A80AAE8DBBA875E283E8492A;"
    c = get_cookie(PARAMS_URL_OA, PARAMS_OA_USERNAME, PARAMS_OA_PASSWORD)
    df = build_address(c)
    print_df(df)
    # data_json = json.loads(data)
    # print(json.dumps(data_json, indent=4, ensure_ascii=False))
