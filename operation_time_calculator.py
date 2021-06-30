# -*- coding: utf-8 -*-

import pandas as pd
import datetime
import json
import copy


def period(start_time, end_time):
    # if not len(start_time) < 19 or len(end_time) < 19:
    #     return 0.0
    if pd.to_datetime(start_time).hour in [22, 23]:
        start_time_tmp = datetime.datetime.combine((pd.to_datetime(start_time) + datetime.timedelta(days=1)).date(), datetime.time(hour=8, minute=0, second=0))
    elif pd.to_datetime(start_time).hour in [0, 1, 2, 3, 4, 5, 6, 7]:
        start_time_tmp = datetime.datetime.combine(pd.to_datetime(start_time).date(), datetime.time(hour=8, minute=0, second=0))
    else:
        start_time_tmp = start_time
    period_tmp = pd.to_datetime(end_time) - pd.to_datetime(start_time_tmp)
    period_hour = round(period_tmp.total_seconds() / 3600, 4)
    return max(0.0, period_hour)


def calculate_periods(periods_list):
    periods_list_sorted = sorted(periods_list, key=lambda x: x[0])
    result = []
    for one_period in periods_list_sorted:
        # result中最后一个区间的右值>=新区间的左值，说明两个区间有重叠
        if result and result[-1][1] >= one_period[0]:
            # 将result中最后一个区间更新为合并之后的新区间
            result[-1][1] = max(result[-1][1], one_period[1])
        else:
            result.append(one_period)
    # print(result)
    periods_sum = 0.0
    for one_period in result:
        periods_sum += period(one_period[0], one_period[1])
    return periods_sum


class Operation:
    def __init__(self, node_name, start_time, end_time, handler, operation_name, origin_id):
        self.origin_id = origin_id
        self.real_start_time = ""  # 排除等候回复加签
        self.pure_time = 0.0
        self.node_name = node_name
        self.start_time = start_time
        self.end_time = end_time
        self.handler = handler
        self.operation_name = operation_name
        # "驳回"/"加签"/"取消加签"/"回复"/"其它"
        if "驳回" in operation_name:
            self.operation_type = "驳回"
            self.to_person_list = []
        elif "取消加签" in operation_name:
            self.operation_type = "取消加签"
            self.to_person_list = operation_name.replace("取消加签：", "").replace(" ", "").replace("\"", "").split(";")
        elif "加签" in operation_name:
            self.operation_type = "加签"
            self.to_person_list = operation_name.replace("加签：", "").replace(" ", "").replace("\"", "").split(";")
        elif "回复" in operation_name:
            self.operation_type = "回复"
            self.to_person_list = operation_name.replace("回复：", "").replace(" ", "").replace("\"", "").split(";")
        else:
            self.operation_type = "其它"
            self.to_person_list = []
        self.half_flag = False  # 是否由驳回导致的half
        self.own = True  # True(内部) or False(外部)

    def content(self):
        content = {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "handler": self.handler,
            "operation_name": self.operation_name,
            "operation_type": self.operation_type,
            "to_person_list": self.to_person_list,
            "half_flag": self.half_flag,
            "own": self.own
        }
        return content

    def print(self):
        print(json.dumps(self.content(), indent=4, ensure_ascii=False))


class OperationQueue:
    def __init__(self, operation: Operation = None):
        self.queue = []
        if operation is not None:
            self.append(operation)

    def append(self, operation: Operation):
        self.queue.append(operation)

    def content(self):
        dic = dict()
        for i, one_operation in enumerate(self.queue):
            dic["Operation {0}/{1}{2}".format(i + 1, len(self.queue), "" if one_operation.own else " [outer]")] = one_operation.content()
        return dic

    def print(self):
        print(json.dumps(self.content(), indent=4, ensure_ascii=False))


class OperationQueueList:
    def __init__(self, operations: list):
        self.operations = operations
        self.queue_list = []
        self.queue_dic = dict()  # handler + start_time -> queue_list_id
        self.queue_to_dic = dict()  # to_person + end_time -> queue_list_id
        self.half_dic = dict()  # handler + node_name -> True or False
        self.handler_periods = dict()  # handler -> time(in hour)
        self.handler_periods_half = dict()  # handler -> time(in hour)
        self.result = dict()  # handler -> details(dict/json)
        for one_operation in operations:
            if self.half_dic.get("{0}+{1}".format(one_operation.handler, one_operation.node_name)):
                one_operation.half_flag = True
                self.half_dic["{0}+{1}".format(one_operation.handler, one_operation.node_name)] = False
            if one_operation.operation_type == "驳回":
                one_operation.half_flag = True
                self.half_dic["{0}+{1}".format(one_operation.handler, one_operation.node_name)] = True

        for one_operation in operations:
            one_operation: Operation = one_operation
            # print("\n现有队列 去找key:{0}+{1}".format(one_operation.handler, one_operation.start_time), end="")
            dic_get = self.queue_dic.get("{0}+{1}".format(one_operation.handler, one_operation.start_time))
            if dic_get is not None:
                # print(": 找到了")
                self.queue_list[dic_get].append(one_operation)
                if one_operation.operation_type == "加签":
                    for to_person in one_operation.to_person_list:
                        self.queue_to_dic["{0}+{1}".format(to_person, one_operation.end_time)] = dic_get
            else:
                # print(": 没找到")
                new_queue_id = len(self.queue_list)
                self.queue_dic["{0}+{1}".format(one_operation.handler, one_operation.start_time)] = new_queue_id
                # print("赋值新key:{0}+{1}".format(one_operation.handler, one_operation.start_time))
                new_queue = OperationQueue(one_operation)
                self.queue_list.append(new_queue)
                if one_operation.operation_type == "加签":
                    for to_person in one_operation.to_person_list:
                        self.queue_to_dic["{0}+{1}".format(to_person, one_operation.end_time)] = new_queue_id
            if one_operation.operation_type == "回复":
                # print("\n回复队列 当前keys: {0}".format(str(self.queue_to_dic.keys())))
                # print("回复队列 去找key:{0}+{1}".format(one_operation.handler, one_operation.start_time), end="")
                dic_to_get = self.queue_to_dic.get("{0}+{1}".format(one_operation.handler, one_operation.start_time))
                if dic_to_get is not None and self.queue_list[dic_to_get].queue[0].handler in one_operation.to_person_list:
                    # print(": 找到了")
                    operation_tmp = copy.deepcopy(one_operation)
                    operation_tmp.own = False
                    self.queue_list[dic_to_get].append(operation_tmp)
                # else:
                #     print(": 没找到")

        for one_queue in self.queue_list:  # 遍历queue_list
            for i, one_operation in enumerate(one_queue.queue):  # 遍历每个operation
                if one_operation.own:  # 如果是内部操作（非其他人操作）
                    if one_operation.operation_type == "取消加签":
                        continue
                    if i == 0:  # 对于序列第一个操作，起算时间为本操作开始时间
                        period_start = one_operation.start_time
                    else:  # 对于序列其它操作，起算时间为序列中上一个操作的操作时间
                        period_start = one_queue.queue[i - 1].end_time
                    period_end = one_operation.end_time
                    if not self.handler_periods.get(one_operation.handler):
                        self.handler_periods[one_operation.handler] = [[period_start, period_end, one_operation.origin_id]]
                    else:
                        tmp = self.handler_periods.get(one_operation.handler)
                        tmp.append([period_start, period_end, one_operation.origin_id])
                        self.handler_periods[one_operation.handler] = tmp
                    if one_operation.half_flag:
                        if not self.handler_periods_half.get(one_operation.handler):
                            self.handler_periods_half[one_operation.handler] = [[period_start, period_end, one_operation.origin_id]]
                        else:
                            tmp = self.handler_periods_half.get(one_operation.handler)
                            tmp.append([period_start, period_end, one_operation.origin_id])
                            self.handler_periods_half[one_operation.handler] = tmp
        # for one_key in self.handler_periods.keys():
        #     print(one_key, self.handler_periods.get(one_key))
        # for one_key in self.handler_periods_half.keys():
        #     print(one_key, self.handler_periods_half.get(one_key))
        for one_key in self.handler_periods.keys():
            period_sum_full = 0
            period_sum_half = 0
            periods_full = self.handler_periods.get(one_key)
            for one_period in periods_full:
                tmp = period(one_period[0], one_period[1])
                period_sum_full += tmp
                self.operations[one_period[2]].real_start_time = one_period[0]
                self.operations[one_period[2]].pure_time = period(one_period[0], one_period[1])
            periods_half = self.handler_periods_half.get(one_key)
            if periods_half:
                for one_period in periods_half:
                    tmp = period(one_period[0], one_period[1])
                    period_sum_half += tmp
                    # self.operations[one_period[2]].pure_time -= tmp * 0.5
            period_sum = period_sum_full - 0.5 * period_sum_half
            self.result[one_key] = {
                "handler": one_key,
                "period_sum": period_sum,
                "period_sum_full": period_sum_full,
                "period_sum_half": period_sum_half,
                "periods_full": periods_full,
                "periods_half": periods_half
            }
        # for one_key in self.handler_periods.keys():
        #     print(json.dumps(self.result.get(one_key), indent=4, ensure_ascii=False))
        # 暂不移除同操作者的重复时间
        self.list_real_start_time = [item.real_start_time for item in self.operations]
        self.list_pure_time = [item.pure_time for item in self.operations]




    def content(self):
        dic = dict()
        for i, one_queue in enumerate(self.queue_list):
            dic["Queue {0}/{1}".format(i + 1, len(self.queue_list))] = one_queue.content()
        return dic

    def print(self):
        print(json.dumps(self.content(), indent=4, ensure_ascii=False))


if __name__ == "__main__":
    test_operations = [
        ["不重要的节点", "2021-06-05 08:00:00", "2021-06-05 08:30:00", "A", "加签：B"],
        ["不重要的节点", "2021-06-05 08:30:00", "2021-06-05 09:00:00", "B", "加签：C"],
        ["不重要的节点", "2021-06-05 08:00:00", "2021-06-05 09:30:00", "A", "加签：C"],
        ["不重要的节点", "2021-06-05 09:30:00", "2021-06-05 10:00:00", "C", "加签：D"],
        ["不重要的节点", "2021-06-05 09:00:00", "2021-06-05 10:30:00", "C", "加签：D"],
        ["不重要的节点", "2021-06-05 10:00:00", "2021-06-05 11:00:00", "D", "加签：E;F"],
        ["不重要的节点", "2021-06-05 10:30:00", "2021-06-05 11:30:00", "D", "回复：C"],
        ["不重要的节点", "2021-06-05 09:00:00", "2021-06-05 12:00:00", "C", "回复：B"],
        ["不重要的节点", "2021-06-05 08:30:00", "2021-06-05 12:30:00", "B", "回复：A"],
        ["不重要的节点", "2021-06-05 10:00:00", "2021-06-05 13:00:00", "D", "取消加签：E;F"],
        ["不重要的节点", "2021-06-05 10:00:00", "2021-06-05 13:30:00", "D", "回复：C"],
        ["不重要的节点", "2021-06-05 09:30:00", "2021-06-05 14:00:00", "C", "回复：A"],
        ["不重要的节点", "2021-06-05 08:00:00", "2021-06-05 14:30:00", "A", "加签：D"],
        ["不重要的节点", "2021-06-05 14:30:00", "2021-06-05 15:00:00", "D", "回复：A"],
        ["不重要的节点", "2021-06-05 08:00:00", "2021-06-05 15:30:00", "A", "通过"]
    ]
    test_operations_2 = [
        ["直属领导", "2021-03-12 13:41:55", "2021-03-12 15:09:51", "申志华", "通过"],
        ["处理部门负责人", "2021-03-12 15:09:51", "2021-03-12 15:24:16", "张镱苧", "加签：\"何伟强\""],
        ["处理部门负责人", "2021-03-12 15:24:16", "2021-03-12 15:25:24", "何伟强", "加签：\"谢晓坤\""],
         ["处理部门负责人", "2021-03-12 15:25:24", "2021-03-12 15:26:18", "谢晓坤", "回复：\"何伟强\""],
         ["处理部门负责人", "2021-03-12 15:09:51", "2021-03-12 15:31:13", "张镱苧", "加签：\"岳冰\""],
         ["处理部门负责人", "2021-03-12 15:31:13", "2021-03-12 15:36:10", "岳冰", "回复：\"张镱苧\""],
         ["处理部门负责人", "2021-03-12 15:09:51", "2021-03-12 15:39:31", "张镱苧", "加签：\"谢晓坤\""],
         ["处理部门负责人", "2021-03-12 15:39:31", "2021-03-12 15:41:20", "谢晓坤", "回复：\"张镱苧\""],
         ["处理部门负责人", "2021-03-12 15:24:16", "2021-03-12 16:04:35", "何伟强", "回复：\"张镱苧\""],
         ["处理部门负责人", "2021-03-12 15:09:51", "2021-03-12 16:04:52", "张镱苧", "通过"]
    ]
    res_operations = [Operation(item[0], item[1], item[2], item[3], item[4], i) for i, item in enumerate(test_operations_2)]
    # que = OperationQueue()
    # for item in res_operations:
    #     que.append(item)
    # que.print()
    ql = OperationQueueList(res_operations)
    # ql.print()
    print(ql)




