# -*- coding: utf-8 -*-

import pandas as pd

from strings import *
from tools import string_to_stamp, stamp_to_string


def judge_node(node_dic, legal_start, legal_end):
    reasons = []
    flag = True
    
    # 3.3.1	属于【统计范围】列明的流程类别
    # (1) 是否涉及业务
    if node_dic.get("是否涉及业务") == "非业务":
        flag = False
        reasons.append(STRING_REASON.format("3.3.1", "是否涉及业务", "非业务"))
    if node_dic.get("是否涉及业务") == "否":
        flag = False
        reasons.append(STRING_REASON.format("3.3.1", "是否涉及业务", "否"))
    # (2) 是否为业务档案/证照
    if node_dic.get("是否为业务档案/证照") == "非业务":
        flag = False
        reasons.append(STRING_REASON.format("3.3.1", "是否为业务档案/证照", "非业务"))
    # (3) 模板名称是否为"财务管理类/采购询价/评价表"
    if node_dic.get("模板名称") == "财务管理类/采购询价/评价表":
        flag = False
        reasons.append(STRING_REASON.format("3.3.1", "模板名称", "财务管理类/采购询价/评价表"))
        
    # 3.3.2	该流程字段【文档状态】内容为"结束"
    if node_dic.get("文档状态") != "结束":
        flag = False
        reasons.append(STRING_REASON.format("3.3.2", "文档状态", node_dic.get("文档状态")))
        
    # 3.3.3	该流程字段【结束时间】的时间位于3.2列明的统计时段之内
    if node_dic.get("结束时间") == "" or not legal_start <= string_to_stamp(node_dic.get("结束时间")) <= legal_end:
        flag = False
        reasons.append(STRING_REASON_TIME.format(
            "3.3.3",
            "结束时间",
            node_dic.get("结束时间"),
            stamp_to_string(legal_start),
            stamp_to_string(legal_end)
        ))
    
    # 3.4.1	字段【操作者】内容为"系统", "backup", "公司总经理(邵平)"
    if node_dic.get("操作者") in ["", "系统", "运营hook", "邵平"]:
        flag = False
        reasons.append(STRING_REASON.format("3.4.1", "操作者", node_dic.get("操作者")))
    
    # 3.4.2	字段【节点名称】内容为"填写申请单", "填写用印申请", "填报借阅申请", "拟稿", "起草节点" ,"直属领导" ,"领导审批"等
    if node_dic.get("节点名称") in [
        "", "填写申请单", "填写用印申请", "填报借阅申请", "拟稿",
        "起草节点", "直属领导", "领导审批", "一级部门负责人审批", "一级部门负责人意见",
        "二级负责人审批", "发起部门负责人审批", "终审人意见", "董事长/CEO审批", "部门负责人意见",
        "部门审批"
    ]:
        flag = False
        reasons.append(STRING_REASON.format("3.4.2", "节点名称", node_dic.get("节点名称")))
    
    # 附加: 极少数因离职等原因无部门归属员工
    if node_dic.get("操作者所在部门") == "（已禁用)":
        flag = False
        reasons.append(STRING_REASON.format("0.0.0", "操作者所在部门", "（已禁用)"))
    
    whether_keep = flag and "是" or "否"
    reasons_string = " / ".join(reasons)
    reasons_string = reasons_string == "" and "<无>" or reasons_string
    
    return whether_keep, reasons_string
    
    
if __name__ == "__main__":
    df = pd.read_excel("new_result.xlsx")

