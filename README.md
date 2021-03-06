FBR统计周报自动任务 说明文档
===========================
该文档用于说明FBR统计周报自动化脚本`FBR v2.0`的代码设计思路与算法介绍，以便将来的维护与拓展工作。

****
	
|项目|FBR统计周报自动任务|
|:--:|:--:
|版本|v2.0
|负责人|徐恩泽
|完成时间|2021-02-20
|部署状态|服务器10.30.4.101
|调度时间|每周五00:00:00-00:00:59自动启动

****
## 目录
* [概述](#概述)
* [需求文档](#需求文档)
* [代码文件介绍](#文件介绍)
    * Part 1 获取Cookie
        * `get_cookie.py`
    * Part 2 获取通讯录
        * `build_address.py`
        * `build_distinct_address.py`
    * Part 3 获取流程列表
        * `get_directories.py`
    * Part 4 获取单流程的基本信息
        * `get_step_detail.py`
    * Part 5 获取单流程包含的节点列表信息
        * `get_node_summary.py`
    * Part 6 每周任务的执行入口
        * `weekly_job.py`
    * Part 7 工具类型脚本
        * `tools.py`
        * `judge_node.py`
        * `mail.py`
    * Part 8 调度类型脚本
        * `clock_send.py`
        * `notice.py`
    * Part 9 参数常量
        * `parameters.py`
        * `strings.py`
* [文件夹介绍](#文件夹介绍)
    * Part 1 谷歌浏览器文件夹
        * `chromedriver`
    * Part 2 统计周报存档文件夹
        * `saves`
        * `latest`

****
## 概述

FBR统计周报自动任务的说明文档。FBR统计周报自动任务是一个每周五触发的自动任务，目前设置触发时间是在每周五00:00:00至00:00:59之间，负责导出OA系统中抄送运营的所有流程并按部门、个人计算平均处理时长等一系列统计项。结果以Excel形式呈现，通过邮箱发送给运营的同事。

****
## 需求文档

暂略，参考`FBR统计指标自动化导出需求20210204.docx`


****
## 代码文件介绍

### Part 1 获取Cookie
#### 1. 模块`get_cookie.py`
> **主要思路**  
通过selenium抓取Cookie。每次任务调度起之后的第一步，供此次任务的所有http-get操作使用。

1. 函数`chrome_driver`：创建`webdriver.Chrome`实例
2. 函数`get_cookie`：通过`selenuim`模拟浏览器界面的打开登录，获取有效的OA授权`Cookie`

### Part 2 获取通讯录
#### 2.模块`dfs_address.py`
> **主要思路**  
灵活使用字段person_id和parent_id，深搜获取完整的部门报告树。

1. 函数`dfs_address`：深度优先搜索，递归，获取完整的部门报告树
2. 函数`build_address`：将深搜的结果进行组装，生成完整的原始报告树

#### 3.模块`build_distinct_address.py`
> **主要思路**  
在前模块的基础上，通过手动规则的引入筛选出"姓名-部门"的一一配对。

1. 函数`deal_path`：从所有层级中筛选（因为包含不需要的子层级），仅保留合法的部门字段正[[可修改]](#)，附表见下：
2. 函数`build_distinct_address`：对`build_address`的结果筛选，并附加一些手动规则校正[[可修改]](#)

|部门
|-
|公司总经理
|金融机构合作首席代表刘志刚团队
|金融机构合作首席代表沈彦炜团队
|金融机构合作首席代表刘明团队
|金融机构合作首席代表张俊涛团队
|金融机构合作首席代表王晓光团队
|金融机构合作首席代表何伟强团队
|金融机构合作首席代表孟庆波团队
|医药行业事业部
|大数据管理部
|运营管理部
|技术开发部
|数字风控部
|计划财务部
|综合管理部
|集团董事长办公室

### Part 3 获取流程列表
#### 4.模块`get_directories.py`
> **主要思路**  
通过已有的Cookie做http-get，获取oa上yunying_hook发起的所有流程列表。

1. 函数`directories_tmp`：获取1页的所有流程，组装，同时得到总流程数和每页个数，计算得到有几页
2. 函数`get_directories`：反复调用`directories_tmp`，将多页流程和总

### Part 4 获取单流程的基本信息
#### 5.模块`get_step_detail.py`
> **主要思路**  
通过已有的Cookie做http-get，获取Part3获取的每个流程的基本信息。

1. 函数`get_step_detail`：获取单流程的`模板名称`、`发起人`、`是否涉及业务`、`是否为业务档案/证照`、`FBR评估满意度`等基本信息

### Part 5 获取单流程包含的节点列表信息
#### 6.模块`get_node_summary.py`
> **主要思路**  
通过已有的Cookie做http-get，获取Part3获取的每个流程的所有节点详细信息。

1. 函数`node_summary_tmp`：获取流程的`流程日志`中1页的所有节点信息，组装，同时得到总节点数和每页个数，计算得到有几页
2. 函数`get_node_summary`：反复调用`node_summary_tmp`，将多页节点和总

### Part 6 每周任务的执行入口
#### 7.模块`weekly_job.py`
> **主要思路**  
很复杂，暂略。

1. 函数`weekly_job`：每周任务的执行入口函数，单次调用有以下两种方式：
```
> # 方式一：指定统计的周数week，统计以上个周五00:00为时间终点的week个完整周（无参数情况下默认此方式，默认week为1）
> # 例子：假设今天2021年03月10日周三，统计过去两个完整周即2021-02-19 00:00:00至2021-03-05 00:00:00
> python weekly_job.py --week 2
>
> # 方式二：直接指定开始日期和结束日期，统计该时间段00:00至00:00之间
> # 例子：统计2021-02-01 00:00:00至2021-02-28 00:00:00
> python weekly_job.py --start 20210201 --end 20210228
>
> # 其它参数：--send，表示是否发送邮件，默认为1（发送），指定为0可以只完成任务但不发送邮件
> # 例子：统计过去一个完整周并且不发送邮件
> python weekly_job.py --week 1 --send 0
```
2. 函数`calculate_all`：组装excel文件并存档在本地
3. 函数`calculate_time_handler`：子Sheet`人均时长`的计算
4. 函数`calculate_time_department`：子Sheet`部门平均时长`的计算
5. 函数`calculate_summary`：子Sheet`FBR需求统计`的计算


### Part 7 工具类型脚本
#### 8.模块`tools.py`
> **主要思路**  
各种多次复用的工具型函数体

1. 函数`http_get`：通过已获取的Cookie，使用`http-get`获取对应url的内容
2. 函数`clear`：清洗字符串，去除匹配的`terrible`列表中字符串，按照`trans`列表字符串进行同义替换
3. 函数`clear_name`：在`流程日志`中，除了姓名还可能有职位、括号等杂项，清除杂项仅保留姓名
4. 函数`no_bad`：在获取"发起人"时，筛选掉不合适的字段
5. 函数`last_legal_period`：获取起始时间戳和结束时间戳，都是周五的00:00:00，由`count`指定是统计周数，参数`time_string`是需要传入今日的日期（避免linux服务器上的时差）
6. 函数`string_to_stamp`：时间字符串转时间戳
7. 函数`stamp_to_string`：时间戳转时间字符串
8. 函数`print_df`：打印dataframe，设置了格宽，在英文时可以对齐，中文内容时尽量对齐
9. 函数`select_first_match`：查找一个dataframe中，满足`key_col_1`列值为`key_1`且`key_col_2`列为`key_2`的第一行的`res_col`列的值
10. 函数`sum_all_match`：查找一个dataframe中，满足`key_col`列值为`key`的所有行的`res_col`列的值之和
11. 函数`not_all_nan`：在一个dataframe列中，是否并不全为`Null`，只要有非`Null`项即返回`True`，否则返回`False`
12. 函数`not_all_like`：在一个dataframe列中，是否并不全为`like`值，只要有非`like`项即返回`True`，否则返回`False`
13. 函数`mean_satis`：在一个dataframe列中，计算`FBR满意度`的均值，值为`<无>`的不参与计算
14. 函数`create_path`：创建存放在saves中的文件夹并返回
15. 函数`clean_dir`：清空一个文件夹中的文件（用于latest文件夹清空）
16. 函数`copy_file`：复制一个文件粘贴到另一个文件夹（用于从saves到latest文件夹的拷贝）
17. 函数`now_time_string`：获取当前时间字符串，格式形如`2021-03-10 10:01:29`，兼容linux和windows均处理成`UTC+08:00`
18. 函数`get_week_day`：由一个时间字符串得到对应是`UTC+08:00`下的星期几
19. 函数`sort_time_department`：子Sheet`部门平均时长`的排序
20. 函数`sort_time_person`：子Sheet`人均时长`的排序
21. 函数`sort_summary`：子Sheet`FBR需求统计`的排序
22. 函数`utc_to_local`：将一个`UTC+00:00`的时间字符串转成`UTC+08:00`的
23. 类`LogFBR`：用于构建邮件中的文本内容
24. 子函数`LogFBR.print`：作用包含`print`，补充额外的时间字符串信息，同时记录所有`print`的内容到`LogFBR.log`中


#### 9.模块`judge_node.py`
> **主要思路**  
很重要的环节，按照运营的要求筛选去除不参与统计的节点，并给出原因

1. 函数`judge_node`：对于全量数据的每行，根据筛选条件规则筛选去除不参与统计的节点，并给出原因，需要给出统计时间范围的时间戳。目前的筛选条件[[可修改]](#)附表见下：

|规则编号|规则名|规则涉及列|正负逻辑|监测值范围
|---|---|---|---|---
|3.3.1|属于【统计范围】列明的流程类别|是否涉及业务|排除|`非业务`/`否`
|3.3.1|属于【统计范围】列明的流程类别|是否为业务档案/证照|排除|`非业务`
|3.3.1|属于【统计范围】列明的流程类别|模板名称|排除|`财务管理类/采购询价/评价表`
|3.3.2|该流程字段【文档状态】内容为"结束"|是否为业务档案/证照|必须|`结束`
|3.3.3|该流程字段【结束时间】的时间位于3.2列明的统计时段之内|结束时间|必须|（时间戳范围）
|3.4.1|字段【操作者】内容为"系统", "backup", "公司总经理(邵平)"|操作者|排除|`(空)`/`系统`/`运营hook`/`邵平`
|3.4.2|字段【节点名称】内容为"填写申请单", "填写用印申请", "填报借阅申请", "拟稿", "起草节点" ,"直属领导" ,"领导审批"等|节点名称|排除|`(空)`/`填写申请单`/`填写用印申请`/`填报借阅申请`/`拟稿`/`起草节点`/`直属领导`/`领导审批`/`一级部门负责人审批`/`一级部门负责人意见`/`二级负责人审批`/`发起部门负责人审批`/`终审人意见`/`董事长/CEO审批`/`部门负责人意见`/`部门审批`
|0.0.0|极少数因离职等原因无部门归属员工|操作者所在部门|排除|`（已禁用)`

#### 10.模块`mail.py`
> **主要思路**  
发送邮件相关的代码，复用了以前用在BOS备份任务中的版本并微改

1. 类`Mail`：邮件类（主要使用`email`包，基于腾讯企业邮箱）
2. 子函数`Mail.format_address`：从邮箱名查类初始化函数中设置的通讯录得到收件人名
3. 子函数`Mail.set_receivers`：显式设置收件人、抄送、密送
4. 子函数`Mail.send`：发送邮件，可设置文本内容、附件（列表）、邮件主题名

### Part 8 调度类型脚本
#### 11.模块`clock_send.py`
> **主要思路**  
部署在服务器的总任务的入口函数，每50s检查当前时间是否落在notice.py中指定的范围，若满足则执行

1. 函数`clock_send`：每周任务的执行入口函数，部署方式是直接运行：
```
> python clock_send.py
```

#### 12.模块`notice.py`
> **主要思路**  
与clock_send对应，用于设定定时任务触发的时间（小时&分钟），仅定义变量，无函数体


### Part 9 参数常量
#### 13.模块`parameters.py`
> **主要思路**  
各种可能发生变化的参数，仅定义变量，无函数体


#### 14.模块`strings.py`
> **主要思路**  
各种一般不发生变化的字符串，仅定义变量，无函数体


****
## 文件夹介绍

### Part 1 谷歌浏览器文件夹
#### 1. 文件夹`chromedriver`
> **chromedriver浏览器内核**  
内含linux和windows两个文件夹，通过platform中的方法来判断运行任务时所属的平台，调用其中对应的chromedriver浏览器

### Part 2 统计周报存档文件夹
#### 2. 文件夹`saves`
> **统计周报全量存档**  
包含多个文件夹，以统计周期为文件夹名，例如"20210226-20210305"，同一统计周期内允许有多个统计周报文件，以时间区分，例如"FBR_Report_20210226-20210305_v20210304194319.xlsx"


#### 3. 文件夹`latest`
> **统计周报最新一期存档**  
仅包含一个文件，是最新一期的FBR统计周报
  
****