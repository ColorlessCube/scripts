#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：scripts
@File    ：utils.py
@Author  ：alex
@Date    ：2022/10/13 9:50 下午
"""



def get_dict_mapping(dict_ls, key):
    res_dict = {}
    for item in dict_ls:
        res_dict[item.get(key)] = item
    return res_dict


