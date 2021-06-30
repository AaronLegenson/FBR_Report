# -*- coding: utf-8 -*-

import sys
import argparse
import socket

import pandas as pd

from get_cookie import get_cookie
from tools import *
from build_address import build_address
from build_distinct_address import build_distinct_address
from get_directories import get_directories
from get_node_summary import get_node_summary
from get_step_detail import get_step_detail
from judge_node import judge_node
from mail import Mail


def weekly_job(week_count, sent_flag=True, start_date_string=None, end_date_string=None):
    execute_path = sys.path[0]
    log = LogFBR()
    # Step 0: Basic Information
    weekday = get_week_day(now_time_string())
    log.print("[Step 0] Basic Information: Weekday: {0}".format(weekday))
    try:
        server_ip = socket.gethostbyname(socket.gethostname())
    except Exception as e:
        log.print("[Step 0] Error in getting ip:", e)
        server_ip = "unknown"
    log.print("[Step 0] Basic Information: Server IP: {0}".format(server_ip))
    log.print("[Step 0] Basic Information: Done")
    
    # Step 1: Get Cookie
    log.print("[Step 1] Get Cookie: ", "")
    try:
        cookie = get_cookie(PARAMS_URL_OA, PARAMS_OA_USERNAME, PARAMS_OA_PASSWORD)
    except Exception as e:
        print("\nError:", e)
        print("Error in getting cookie. Try again...")
        try:
            cookie = get_cookie(PARAMS_URL_OA, PARAMS_OA_USERNAME, PARAMS_OA_PASSWORD)
        except Exception as e:
            print("Error:", e)
            print("Still Failed. Skip this day.")
            return
    log.print(STRING_FORMAT_3.format(cookie[:-26], STRING_COVER_16, cookie[-10:]))
    log.print("[Step 1] Get Cookie: Done")

    # Step 2: Get Directories
    log.print("[Step 2] Get Directories: ", "")
    df_id_list = get_directories(cookie)
    log.print("{0} all".format(len(df_id_list)))
    log.print("[Step 2] Get Directories: Done")

    # Step 3: Get Address Book
    log.print("[Step 3] Get Address Book: ", "")
    df_address = build_address(cookie)
    df_distinct_address = build_distinct_address(cookie, df_address)
    df_book: pd.DataFrame = df_distinct_address.copy(deep=True)
    df_book.sort_values(by=[STRING_CN_DEPARTMENT, STRING_CN_NAME], inplace=True)
    df_book = df_book.reset_index(drop=True)
    log.print("{0} all".format(len(df_distinct_address)))
    log.print("[Step 3] Get Address Book: Done")

    # Step 4: Get Details
    df = pd.DataFrame()
    length = len(df_id_list)
    t_sum = 0
    for i in range(0, length):
        t0 = time.time()
        if i == length - 1 or (i + 1) % 100 == 0:
            log.print("[Step 4] Get Details: {0:03d}/{1:03d} ".format(i + 1, length), "")
        node_summary_df = get_node_summary(cookie, df_id_list.iloc[i][STRING_CN_FD_ID])
        step_detail_df = get_step_detail(cookie, df_id_list.iloc[i][STRING_CN_FD_ID])
        tmp_df = step_detail_df.merge(node_summary_df, on=STRING_CN_FD_ID, how=STRING_LEFT)
        df = pd.concat([df, tmp_df])
        t1 = time.time()
        t_sum += (t1 - t0)
        m, s = divmod(int(t_sum / float(i + 1) * (length - i - 1)), 60)
        h, m = divmod(m, 60)
        res_diff_time = STRING_FORMAT_HOUR_MINUTE_SECOND.format(h, m, s)
        if i == length - 1 or (i + 1) % 100 == 0:
            log.print(STRING_FORMAT_TIME_REMAIN.format(res_diff_time))
    log.print("[Step 4] Get Details: Done")

    # Step 5: Build Report
    log.print("[Step 5] Build Report: ", "")
    df = df.reset_index(drop=True)
    df_distinct_address.rename(
        columns={STRING_CN_NAME: STRING_CN_FD_NAME, STRING_CN_DEPARTMENT: STRING_CN_HANDLER_DEPARTMENT},
        inplace=True)
    df = df.merge(df_distinct_address, on=STRING_CN_FD_NAME, how=STRING_LEFT)
    df_distinct_address.rename(
        columns={STRING_CN_FD_NAME: STRING_CN_CREATOR, STRING_CN_HANDLER_DEPARTMENT: STRING_CN_CREATOR_DEPARTMENT},
        inplace=True)
    df = df.merge(df_distinct_address, on=STRING_CN_CREATOR, how=STRING_LEFT)
    df = df.merge(df_id_list, on=STRING_CN_FD_ID, how=STRING_LEFT)
    whether_keep_list, reasons_string_list = [], []
    if week_count == 0:
        legal_start = string_to_stamp(start_date_string, STRING_FORMAT_NO_HYPHEN)
        legal_end = string_to_stamp(end_date_string, STRING_FORMAT_NO_HYPHEN)
    else:
        legal_start, legal_end = last_legal_period(week_count, now_time_string())
    save_path, save_filename = create_path(execute_path, legal_start, legal_end)
    for index, row in df.iterrows():
        whether_keep, reasons_string = judge_node(row, legal_start, legal_end)
        whether_keep_list.append(whether_keep)
        reasons_string_list.append(reasons_string)
    df[STRING_CN_WHETHER_KEEP] = whether_keep_list
    df[STRING_CN_REASONS_STRING_WHY_NOT_KEEP] = reasons_string_list
    df = df[[
        STRING_CN_WHETHER_KEEP,
        STRING_CN_REASONS_STRING_WHY_NOT_KEEP,
        STRING_CN_FD_ID,
        STRING_CN_DOC_CREATE_TIME_TIME,
        STRING_CN_DOC_PUBLISH_TIME_TIME,
        STRING_CN_DOC_STATUS,
        STRING_CN_FD_NUMBER,
        STRING_CN_CREATOR,
        STRING_CN_CREATOR_DEPARTMENT,
        STRING_CN_DOC_SUBJECT,
        STRING_CN_MODEL_NAME,
        STRING_CN_MODEL_NAME_PART_1,
        STRING_CN_MODEL_NAME_PART_2,
        STRING_CN_WHETHER_BUSINESS,
        STRING_CN_WHETHER_ARCHIVE,
        STRING_CN_NODE,
        STRING_CN_FD_NAME,
        STRING_CN_HANDLER_DEPARTMENT,
        STRING_CN_HANDLE,
        STRING_CN_SYSTEM_HANDLE,
        STRING_CN_RECEIVE_TIME,
        STRING_CN_HANDLE_TIME,
        STRING_CN_REAL_START_TIME,
        STRING_CN_DEAL_TIME_PERIOD_OLD,
        STRING_CN_DEAL_TIME_PERIOD,
        STRING_CN_FBR_SATIS,
        STRING_CN_FD_USE_WORD,
        STRING_CN_FD_IS_FILING,
        STRING_CN_NODE_NAME,
        STRING_CN_HANDLER_NAME]]
    empty_flag = False
    if STRING_CN_YES not in whether_keep_list:
        empty_flag = True
        log.print("Empty Week Warning!")
        writer = pd.ExcelWriter(save_path)
        df.to_excel(
            writer, sheet_name=STRING_CN_SHEET_APPENDIX_DETAIL_ALL, float_format=STRING_FORMAT_FLOAT_4, index=False)
        df_book.to_excel(
            writer, sheet_name=STRING_CN_SHEET_APPENDIX_ADDRESS_BOOK, float_format=STRING_FORMAT_FLOAT_4, index=False)
        writer.save()
        log.print("[Step 5] Build Report: Save to {0}".format(save_path.replace(execute_path, "{Path}")))
        content_list = [
            ["none", STRING_CN_SHEET_FBR, ""],
            ["none", STRING_CN_SHEET_PERSON, ""],
            ["none", STRING_CN_SHEET_DEPARTMENT, ""],
            ["none", STRING_CN_SHEET_SUMMARY, ""],
            ["none", STRING_CN_SHEET_APPENDIX_DETAIL_KEEP, ""],
            ["none", STRING_CN_SHEET_APPENDIX_ADDRESS_BOOK, df_book.to_html()]
        ]
    else:
        log.print("Save to {0}".format(save_path.replace(execute_path, "{Path}")))
        content_list = calculate_all(df, df_book, save_path)
    latest_path = STRING_FORMAT_3.format(execute_path, os.sep, STRING_LATEST)
    latest_full_path = STRING_FORMAT_3.format(latest_path, os.sep, save_filename)
    log.print("[Step 5] Build Report: ", "")
    clean_dir(latest_path)
    log.print("Clean {0}".format(latest_path.replace(execute_path, "{Path}")))
    log.print("[Step 5] Build Report: ", "")
    copy_file(save_path, latest_full_path)
    log.print("Copy to {0}".format(latest_full_path.replace(execute_path, "{Path}")))
    log.print("[Step 5] Build Report: Done")

    # Step 6: SHA256 Hash
    log.print("[Step 6] SHA256 Hash: ", "")
    file_md5 = sha256(save_path)
    log.print(file_md5)
    log.print("[Step 6] SHA256 Hash: Done")

    # Step 7: Mail Report
    mail = Mail()
    log.print("[Step 7] Mail Report: Weekday is {0} (1-7)".format(get_week_day(now_time_string())))
    if get_week_day(now_time_string()) == 5:
        to_receivers = ["tanshuya@fusionfintrade.com"]
        cc_receivers = ["wangyiwei@fusionfintrade.com"]
        bcc_receivers = ["gusongtao@fusionfintrade.com"]
    else:
        to_receivers = ["gusongtao@fusionfintrade.com"]
        cc_receivers = ["gusongtao@fusionfintrade.com"]
        bcc_receivers = ["gusongtao@fusionfintrade.com"]
    log.print("[Step 7] Mail Report: Send to {0}".format(str(to_receivers)))
    log.print("[Step 7] Mail Report: Cc to {0}".format(str(cc_receivers)))
    content_list.append(["log", "Logs", log.log])
    content_html = unite_html(content_list)
    mail.set_receivers(to_receivers, cc_receivers, bcc_receivers)
    subject = STRING_FORMAT_FBR_SUBJECT.format(
        stamp_to_string(legal_start, STRING_FORMAT_NO_HYPHEN),
        stamp_to_string(legal_end, STRING_FORMAT_NO_HYPHEN))
    if empty_flag:
        subject = subject + STRING_CN_NO_CONTENT_WARNING
    if sent_flag:
        mail.send(content_html, [save_path], subject, STRING_HTML)
    log.print("[Step 7] Mail Report: Done")


def calculate_all(df_history, df_book, save_path):
    df = df_history.copy(deep=True)
    df.drop(df[df[STRING_CN_WHETHER_KEEP] == STRING_CN_NO].index, inplace=True)
    df[STRING_CN_FD_NUMBER_AND_SUBJECT] = [STRING_FORMAT_MERGE_FD_NUMBER_AND_SUBJECT.format(x, y)
                                           for x, y in zip(df[STRING_CN_FD_NUMBER], df[STRING_CN_DOC_SUBJECT])]
    df = df[[
        STRING_CN_FD_NUMBER_AND_SUBJECT,
        STRING_CN_NODE,
        STRING_CN_FD_NAME,
        STRING_CN_HANDLER_DEPARTMENT,
        STRING_CN_HANDLE,
        STRING_CN_RECEIVE_TIME,
        STRING_CN_HANDLE_TIME,
        STRING_CN_REAL_START_TIME,
        STRING_CN_DEAL_TIME_PERIOD_OLD,
        STRING_CN_DEAL_TIME_PERIOD,
        STRING_CN_FBR_SATIS]]
    df_detail = df.copy(deep=True)
    df_detail.reset_index(drop=True)
    
    df_time_person, handler_dic = calculate_time_handler(df)
    df_time_department, department_dic, titles, departments = calculate_time_department(df)
    df_static_all = pd.DataFrame()
    df_static_all = df_static_all.append([handler_dic, department_dic], ignore_index=True)
    df_summary = calculate_summary(df_time_person, df_time_department, departments, titles, df)

    writer = pd.ExcelWriter(save_path)
    df_summary = sort_summary(df_summary)
    df_time_person = sort_time_person(df_time_person)
    df_time_department = sort_time_department(df_time_department)
    df_summary.to_excel(
        writer, sheet_name=STRING_CN_SHEET_FBR, float_format=STRING_FORMAT_FLOAT_4, index=False)
    df_time_person.to_excel(
        writer, sheet_name=STRING_CN_SHEET_PERSON, float_format=STRING_FORMAT_FLOAT_4, index=False)
    df_time_department.to_excel(
        writer, sheet_name=STRING_CN_SHEET_DEPARTMENT, float_format=STRING_FORMAT_FLOAT_4, index=False)
    df_static_all.to_excel(
        writer, sheet_name=STRING_CN_SHEET_SUMMARY, float_format=STRING_FORMAT_FLOAT_4, index=False)
    df_detail.to_excel(
        writer, sheet_name=STRING_CN_SHEET_APPENDIX_DETAIL_KEEP, float_format=STRING_FORMAT_FLOAT_4, index=False)
    df_history.to_excel(
        writer, sheet_name=STRING_CN_SHEET_APPENDIX_DETAIL_ALL, float_format=STRING_FORMAT_FLOAT_4, index=False)
    df_book.to_excel(
        writer, sheet_name=STRING_CN_SHEET_APPENDIX_ADDRESS_BOOK, float_format=STRING_FORMAT_FLOAT_4, index=False)
    writer.save()
    set_excel_style(save_path)
    content_list = [
        ["highlight", STRING_CN_SHEET_FBR, df_summary.to_html()],
        ["highlight", STRING_CN_SHEET_PERSON, df_time_person.to_html()],
        ["highlight", STRING_CN_SHEET_DEPARTMENT, df_time_department.to_html()],
        ["highlight", STRING_CN_SHEET_SUMMARY, df_static_all.to_html()],
        ["normal", STRING_CN_SHEET_APPENDIX_DETAIL_KEEP, df_detail.to_html()],
        ["normal", STRING_CN_SHEET_APPENDIX_ADDRESS_BOOK, df_book.to_html()]
    ]
    return content_list


def calculate_time_handler(df):
    df.drop(
        df[(df[STRING_CN_NODE] == STRING_CN_SATIS_JUDGE) | (df[STRING_CN_NODE] == STRING_CN_CREATOR_JUDGE)].index,
        inplace=True)
    handlers = list(set(df[STRING_CN_FD_NAME]))
    handlers.sort(key=lambda x: x)
    titles = list(set(df[STRING_CN_FD_NUMBER_AND_SUBJECT]))
    titles.sort(key=lambda x: x)
    reject_dic = dict()
    clear_time = []
    for index, row in df.iterrows():
        if STRING_CN_REJECT in row.get(STRING_CN_HANDLE):
            clear_time.append(row.get(STRING_CN_DEAL_TIME_PERIOD) / 2.0)
            reject_dic[str(row.get(STRING_CN_FD_NUMBER_AND_SUBJECT))] = True
        elif not reject_dic.get(str(row.get(STRING_CN_FD_NUMBER_AND_SUBJECT))):
            clear_time.append(row.get(STRING_CN_DEAL_TIME_PERIOD))
        else:
            clear_time.append(row.get(STRING_CN_DEAL_TIME_PERIOD) / 2.0)
            reject_dic[str(row.get(STRING_CN_FD_NUMBER_AND_SUBJECT))] = False
    df[STRING_CN_DEAL_TIME_PERIOD_CLEAR] = clear_time
    df = df[[
        STRING_CN_FD_NUMBER_AND_SUBJECT,
        STRING_CN_FD_NAME,
        STRING_CN_HANDLER_DEPARTMENT,
        STRING_CN_DEAL_TIME_PERIOD_CLEAR
    ]].groupby([STRING_CN_FD_NUMBER_AND_SUBJECT, STRING_CN_FD_NAME, STRING_CN_HANDLER_DEPARTMENT]).sum()
    dis_df = pd.DataFrame(
        columns=[
            STRING_CN_FD_NUMBER_AND_SUBJECT,
            STRING_CN_FD_NAME,
            STRING_CN_HANDLER_DEPARTMENT,
            STRING_CN_DEAL_TIME_PERIOD_CLEAR])
    for index, row in df.iterrows():
        dis_df = dis_df.append([{
            STRING_CN_FD_NUMBER_AND_SUBJECT: row.name[0],
            STRING_CN_FD_NAME: row.name[1],
            STRING_CN_HANDLER_DEPARTMENT: row.name[2],
            STRING_CN_DEAL_TIME_PERIOD_CLEAR: row[0]}], ignore_index=True)
    res_df = pd.DataFrame()
    handler_sum = 0
    handler_time_sum = 0.0
    for handler in handlers:
        tmp_dic = dict()
        tmp_dic[STRING_CN_FD_NAME] = handler
        tmp_dic[STRING_CN_FD_PARENT] = select_first_match(
            dis_df, STRING_CN_FD_NAME, handler, STRING_CN_FD_NAME, handler, STRING_CN_HANDLER_DEPARTMENT)
        tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_AVERAGE] = 0.0
        tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_SUM] = 0.0
        tmp_dic[STRING_CN_FD_PARTICIPATE] = 0
        for title in titles:
            tmp_dic[title] = select_first_match(
                dis_df,
                STRING_CN_FD_NUMBER_AND_SUBJECT,
                title,
                STRING_CN_FD_NAME,
                handler,
                STRING_CN_DEAL_TIME_PERIOD_CLEAR)
            if not pd.isnull(tmp_dic[title]):
                tmp_dic[STRING_CN_FD_PARTICIPATE] = tmp_dic[STRING_CN_FD_PARTICIPATE] + 1
                tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_SUM] = tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_SUM] + tmp_dic[title]
            if tmp_dic[STRING_CN_FD_PARTICIPATE] == 0:
                tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_AVERAGE] = 0.0
            else:
                tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_AVERAGE] = \
                    tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_SUM] / float(tmp_dic[STRING_CN_FD_PARTICIPATE])
        res_df = res_df.append([tmp_dic], ignore_index=True)
        handler_sum += 1
        handler_time_sum += tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_AVERAGE]
    if handler_sum == 0:
        average_person_time = 0.0
    else:
        average_person_time = handler_time_sum / float(handler_sum)
    handler_dic = {
        STRING_CN_STAT_ITEM: STRING_CN_PERSON_TIME_PERIOD_AVERAGE,
        STRING_CN_AVERAGE: average_person_time,
        STRING_CN_SUM: handler_time_sum,
        STRING_CN_COUNT: handler_sum
    }
    return res_df, handler_dic


def calculate_time_department(df):
    df.drop(
        df[(df[STRING_CN_NODE] == STRING_CN_SATIS_JUDGE) | (df[STRING_CN_NODE] == STRING_CN_CREATOR_JUDGE)].index,
        inplace=True)
    departments = list(set(df[STRING_CN_HANDLER_DEPARTMENT]))
    departments.sort(key=lambda x: x)
    titles = list(set(df[STRING_CN_FD_NUMBER_AND_SUBJECT]))
    titles.sort(key=lambda x: x)
    reject_dic = dict()
    clear_time = []
    for index, row in df.iterrows():
        if STRING_CN_REJECT in row.get(STRING_CN_HANDLE):
            clear_time.append(row.get(STRING_CN_DEAL_TIME_PERIOD) / 2.0)
            reject_dic[str(row.get(STRING_CN_FD_NUMBER_AND_SUBJECT))] = True
        elif not reject_dic.get(str(row.get(STRING_CN_FD_NUMBER_AND_SUBJECT))):
            clear_time.append(row.get(STRING_CN_DEAL_TIME_PERIOD))
        else:
            clear_time.append(row.get(STRING_CN_DEAL_TIME_PERIOD) / 2.0)
            reject_dic[str(row.get(STRING_CN_FD_NUMBER_AND_SUBJECT))] = False
    df[STRING_CN_DEAL_TIME_PERIOD_CLEAR] = clear_time
    df = df[[
        STRING_CN_FD_NUMBER_AND_SUBJECT, STRING_CN_HANDLER_DEPARTMENT, STRING_CN_DEAL_TIME_PERIOD_CLEAR
    ]].groupby([STRING_CN_FD_NUMBER_AND_SUBJECT, STRING_CN_HANDLER_DEPARTMENT]).sum()
    dis_df = pd.DataFrame(
        columns=[STRING_CN_FD_NUMBER_AND_SUBJECT, STRING_CN_HANDLER_DEPARTMENT, STRING_CN_DEAL_TIME_PERIOD_CLEAR])
    for index, row in df.iterrows():
        dis_df = dis_df.append([{
            STRING_CN_FD_NUMBER_AND_SUBJECT: row.name[0],
            STRING_CN_HANDLER_DEPARTMENT: row.name[1],
            STRING_CN_DEAL_TIME_PERIOD_CLEAR: row[0]}], ignore_index=True)
    res_df = pd.DataFrame()
    department_sum = 0
    department_time_sum = 0.0
    for department in departments:
        tmp_dic = dict()
        tmp_dic[STRING_CN_FD_PARENT] = department
        tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_AVERAGE] = 0.0
        tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_SUM] = 0.0
        tmp_dic[STRING_CN_FD_PARTICIPATE] = 0
        for title in titles:
            tmp_dic[title] = select_first_match(
                dis_df,
                STRING_CN_FD_NUMBER_AND_SUBJECT,
                title,
                STRING_CN_HANDLER_DEPARTMENT,
                department,
                STRING_CN_DEAL_TIME_PERIOD_CLEAR)
            if not pd.isnull(tmp_dic[title]):
                tmp_dic[STRING_CN_FD_PARTICIPATE] = tmp_dic[STRING_CN_FD_PARTICIPATE] + 1
                tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_SUM] = tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_SUM] + tmp_dic[title]
            if tmp_dic[STRING_CN_FD_PARTICIPATE] == 0:
                tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_AVERAGE] = 0.0
            else:
                tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_AVERAGE] = \
                    tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_SUM] / float(tmp_dic[STRING_CN_FD_PARTICIPATE])
        res_df = res_df.append([tmp_dic], ignore_index=True)
        department_sum += tmp_dic[STRING_CN_FD_PARTICIPATE]
        department_time_sum += tmp_dic[STRING_CN_HANDLE_TIME_PERIOD_SUM]
    if department_sum == 0:
        average_department_time = 0.0
    else:
        average_department_time = department_time_sum / float(department_sum)
    department_dic = {
        STRING_CN_STAT_ITEM: STRING_CN_DEPARTMENT_TIME_PERIOD_AVERAGE,
        STRING_CN_AVERAGE: average_department_time,
        STRING_CN_SUM: department_time_sum,
        STRING_CN_COUNT: department_sum
    }
    return res_df, department_dic, titles, departments


def calculate_summary(df_time_person, df_time_department, departments, titles, df):
    df_summary = pd.DataFrame()
    df_summary[STRING_CN_FD_PARENT] = departments
    df_summary[STRING_CN_REQUIREMENTS_SOLVED] = df_time_department[STRING_CN_FD_PARTICIPATE]
    handler_time_avg = []
    for department in departments:
        handler_time_sum = sum_all_match(
            df_time_person, STRING_CN_FD_PARENT, department, STRING_CN_HANDLE_TIME_PERIOD_SUM)
        handler_time_count = sum_all_match(df_time_person, STRING_CN_FD_PARENT, department, STRING_CN_FD_PARTICIPATE)
        if handler_time_count == 0:
            handler_time_avg.append(0.0)
        else:
            handler_time_avg.append(handler_time_sum / float(handler_time_count))
    df_summary[STRING_CN_PERSON_TIME_PERIOD_AVERAGE] = handler_time_avg
    participator_avg = []
    for department in departments:
        participator_sum = sum_all_match(df_time_person, STRING_CN_FD_PARENT, department, STRING_CN_FD_PARTICIPATE)
        title_count = 0
        df_participator_avg = df_time_person[df_time_person[STRING_CN_FD_PARENT] == department]
        for title in titles:
            if not_all_nan(df_participator_avg[title]):
                title_count += 1
        if title_count == 0:
            participator_avg.append(0.0)
        else:
            participator_avg.append(participator_sum / float(title_count))
    df_summary[STRING_CN_AVERAGE_HANDLER_COUNT] = participator_avg
    df_summary[STRING_CN_AVERAGE_HANDLE_TIME_PERIOD] = df_time_department[STRING_CN_HANDLE_TIME_PERIOD_AVERAGE]
    satis_avg = []
    for department in departments:
        df_satis = df[df[STRING_CN_HANDLER_DEPARTMENT] == department]
        satis_avg.append(mean_satis(df_satis[STRING_CN_FBR_SATIS]))
    df_summary[STRING_CN_AVERAGE_SATIS] = satis_avg
    return df_summary
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", default=1, help="number of weeks involved in the statistics")
    parser.add_argument("--start", default=None, help="start of statistical range. example: '19491001'")
    parser.add_argument("--end", default=None, help="end of statistical range. example: '19491001'")
    parser.add_argument("--send", default=1, help="whether to send email")
    opt = parser.parse_args()
    if opt.send == "0":
        send = False
    else:
        send = True
    try:
        if not opt.start or not opt.end:
            weekly_job(opt.week, send)
        else:
            weekly_job(0, send, opt.start, opt.end)
    except Exception as e1:
        print("Error:", e1)
        print("Rerunning as default (week = 1)...")
        try:
            weekly_job(1)
        except Exception as e2:
            print("Error:", e2)
            print("Still failed. Skipped.")
