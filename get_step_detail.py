# -*- coding: utf-8 -*-

import re
from bs4 import BeautifulSoup
from tools import *


def get_step_detail(cookie, fd_id):
    data = http_get(cookie, PARAMS_URL_STEP_DETAIL.format(fd_id))
    model_name = clear(
        re.findall("<tr><td class=\"td_normal_title\" width=15%>模板名称</td><td colspan=3>.*?</td></tr>", data)[0],
        TERRIBLE_MODEL_NAME
    )
    model_name_parts = model_name.split(STRING_SLASH)
    model_name_1, model_name_2 = model_name_parts[0], model_name_parts[1]
    soup = BeautifulSoup(data, STRING_LXML)
    location_start = soup.find_all(STRING_TR)
    start_person = STRING_CN_NONE
    for item in location_start:
        if (STRING_CN_APPLICANT in str(item.text) or STRING_CN_CREATOR in str(item.text)) and len(str(item.text)) < 40:
            location_start_parts = item.find_all(STRING_TD)
            start = [x.text for x in location_start_parts if no_bad(x.text, PARAMS_START_BAD)]
            start_person = clear(start[1])

    satis_parts = re.findall("满意度.*?</xformflag>", data)
    satis = STRING_CN_NONE
    if len(satis_parts) > 0:
        satis_info = re.findall("<label><input type=radio checked >.*?星", satis_parts[0])
        if len(satis_info) > 0:
            satis = satis_info[0][-2]
    
    business_parts = re.findall("是否涉及业务.*?</xformflag>", data)
    business = STRING_CN_NONE
    if len(business_parts) > 0:
        business_info = re.findall("<label><input type=radio checked >.*?&nbsp", business_parts[0])
        if len(business_info) > 0:
            business = business_info[0][34:-5]

    archive_parts = re.findall("是否为业务档案/证照.*?</xformflag>", data)
    archive = STRING_CN_NONE
    if len(archive_parts) > 0:
        archive_info = re.findall("<label><input type=radio checked >.*?&nbsp", archive_parts[0])
        if len(archive_info) > 0:
            archive = archive_info[0][34:-5]
    
    res_df = pd.DataFrame({
        STRING_CN_FD_ID: [fd_id],
        STRING_CN_MODEL_NAME: [model_name],
        STRING_CN_MODEL_NAME_PART_1: [model_name_1],
        STRING_CN_MODEL_NAME_PART_2: [model_name_2],
        STRING_CN_CREATOR: [start_person],
        STRING_CN_WHETHER_BUSINESS: [business],
        STRING_CN_WHETHER_ARCHIVE: [archive],
        STRING_CN_FBR_SATIS: [satis]
    })
    return res_df


if __name__ == "__main__":
    # c = get_cookie(PARAMS_URL_OA, PARAMS_OA_USERNAME, PARAMS_OA_PASSWORD)
    c = "JSESSIONID=7D42AC2340A5D0FD415911113520EA05;"
    # f_ids = [
    #     "17789f0a4cacacb81f92c0241de821a1"
    # ]
    # for f_id in f_ids:
    #     print(f_id)
    #     res = get_fbr(c, f_id)
    #     print(str(res))

    df = get_step_detail(c, "17742690fd5568adcc4da674dfaa53f5")
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    print(df)
    # data_json = json.loads(data)
    # print(json.dumps(data_json, indent=4, ensure_ascii=False))
    # print(data)
