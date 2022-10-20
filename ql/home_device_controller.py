#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：scripts 
@File    ：home_device_controller.py
@Author  ：alex
@Date    ：2022/10/20 1:55 下午 
"""
import json

from requests import request
from logger import logger

# Home assistant token.
token = ''
default_headers = {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
}
# Your Home assistant service url.
base_url = ''

device_id_mapping = {
    '书房电源': 'switch.cuco_cp1_5e1f_switch'
}


def request_api(url, method='GET', headers=None, json_=None):
    """
    Request API for home assistant.
    @param url:
    @param method:
    @param headers:
    @param json_:
    @return:
    """
    if headers is None:
        headers = default_headers
    url = base_url + url
    response = request(url=url, method=method, headers=headers, json=json_)
    response = json.loads(response.content)
    logger.info('Remote request completed:\n    url={url}\n    headers={headers}\n    result={result}'.format(**{
        'result': response,
        'url': url,
        'headers': headers
    }))
    return response


def get_device_state(device):
    """
    Get device status by device id.
    @param device:
    @return:
    """
    device_id = device_id_mapping.get(device)
    return request_api('/api/states/' + device_id).get('state')


def set_device_state(device, state):
    """
    Set device status by device id.
    @param device:
    @param state:
    @return:
    """
    device_id = device_id_mapping.get(device)
    return request_api('/api/services/switch/turn_' + state, method='POST', json_={
        'entity_id': device_id
    })


def reverse_device_state(device):
    """
    Reverse device state.
    @param device:
    @return:
    """
    status = get_device_state(device)
    if status == 'on':
        set_device_state(device, 'off')
    else:
        set_device_state(device, 'on')


def main():
    reverse_device_state('书房电源')


if __name__ == '__main__':
    main()
