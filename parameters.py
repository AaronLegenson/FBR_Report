# -*- coding: utf-8 -*-

PARAMS_URL_OA = "https://oa.fusionfintrade.com/login.jsp"  # "https://oa.fusionfintrade.com/"
PARAMS_URL_DIRECTORIES = \
    "https://oa.fusionfintrade.com/km/review/km_review_index/kmReviewIndex.do?method=list&q.mydoc=all&q.j_path=%2Flis" \
    "tAll&q.j_start=%2Fkm%2Freview%2Findex.jsp&q.j_target=_iframe&q.s_raq=0.3918110040551095&pageno={0}&rowsize=15&or" \
    "derby=docCreateTime&ordertype=down&s_ajax=true"
PARAMS_URL_NODE_SUMMARY = \
    "https://oa.fusionfintrade.com/sys/lbpmservice/support/lbpm_audit_note/lbpmAuditNote.do?method=list&fdModelId={0}" \
    "&pageno={1}&s_ajax=true"
PARAMS_URL_STEP_DETAIL = \
    "https://oa.fusionfintrade.com/km/review/km_review_main/kmReviewMain.do?method=view&fdId={0}"
PARAMS_URL_BUILD_ADDRESS = \
    "https://oa.fusionfintrade.com/sys/common/dataxml.jsp?s_bean=sysZoneAddressTree&parent={0}&orgType=11&top="

PARAMS_OA_USERNAME = "yunying_hook"
PARAMS_OA_PASSWORD = "Juliang123$%"

PARAMS_ALL_DEPARTMENTS = [
    "公司总经理",
    "金融机构合作首席代表刘志刚团队",
    "金融机构合作首席代表沈彦炜团队",
    "金融机构合作首席代表刘明团队",
    "金融机构合作首席代表张俊涛团队",
    "金融机构合作首席代表王晓光团队",
    "金融机构合作首席代表何伟强团队",
    "金融机构合作首席代表孟庆波团队",
    "医药行业事业部",
    "大数据管理部",
    "运营管理部",
    "技术开发部",
    "数字风控部",
    "计划财务部",
    "综合管理部",
    "集团董事长办公室",
    "增值服务业务部",
    "金融机构合作首席代表刘芊妤团队(筹)",
    "金融机构合作首席代表刘芊妤团队",
    "战略规划部"
]

PARAMS_START_BAD = [
    "日期", "时间", "编号", "20", "-"
]

TERRIBLE_DEFAULT = [" ", "\">", "&quot;"]
TERRIBLE_XML = ["\r", "\n", "\t", "\\r", "\\n", "\\t"]
TERRIBLE_MODEL_NAME = ["<tr><td class=\"td_normal_title\" width=15%>模板名称</td><td colspan=3>", "</td></tr>"]
TERRIBLE_OPERATION_DATE = ["<!--工作项结束时间不为空时，显示工作项结束时间-->", "<!--已查看-->", "<!--查看时间为空则显示工作项的结束时间-->"]
TERRIBLE_NAMES = [
    " ",
    "(",
    ")",
    "公司总经理",
    "首席大数据官",
    "首席运营官",
    "首席财务官",
    "首席技术官",
    "数字风控部总经理",
    "财务总经理",
    "青岛聚量融资租赁有限公司CEO",
    "风险合规中心总经理",
    "合规风控审核人",
    "聚量保理总裁",
    "集团办公室主任",
    "档案管理负责人",
    "运营中心审核",
    "财务审核",
    "汤平_运维",
    "产业物流赋能事业部项目总监",
    "品宣",
    "增值服务业务部总经理"
]
TRANS_DEFAULT = [["&lt;", "<"], ["&gt;", ">"]]



