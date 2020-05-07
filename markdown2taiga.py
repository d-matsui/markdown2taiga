#!/usr/bin/env python3

from taiga import TaigaAPI
from collections import deque
from getpass import getpass
import sys
import re


def init_taiga_api():
    api = TaigaAPI(
        host='https://dmti.net'
    )
    print('Username or email: ', end='')
    username = input()
    password = getpass('Password: ')
    api.auth(
        username=username,
        password=password
    )
    return api


def readfile_as_array(filename):
    f = open(filename, 'r')
    lines = []
    for line in f.readlines():
        lines.append(line)
    f.close()
    return lines


def calc_min_level(lines):
    min_count_hash = float('inf')
    for line in lines:
        if not line.startswith('#'):
            continue
        count_hash = re.match(r'#+', line).end()
        min_count_hash = min(min_count_hash, count_hash)
    return min_count_hash


def get_linums(lines, target_level):
    linums = deque()
    for linum, line in enumerate(lines):
        if not line.startswith('#'):
            continue
        level = re.match(r'#+', line).end()
        if level == target_level:
            linums.append(linum)
    return linums


def create_us_and_task(project, lines, linums_us, level_task):
    for index_us, linum_us in enumerate(linums_us):
        us_title = lines[linum_us].strip('#').strip()
        us = project.add_user_story(us_title)

        linums_task = []
        if index_us == len(linums_us) - 1:
            linums_task = get_linums(lines[linum_us:], level_task)
        else:
            linum_us_next = linums_us[index_us + 1]
            linums_task = get_linums(lines[linum_us:linum_us_next], level_task)

        for index_task, linum_task in enumerate(linums_task):
            task_title = lines[linum_task].strip('#').strip()
            task_desc = ''
            if index_task == len(linums_task) - 1:
                task_desc = ''.join(lines[linum_task + 1:])
            else:
                linum_task_next = linums_task[index_task + 1]
                task_desc = ''.join(lines[linum_task + 1:linum_task_next])
            us.add_task(
                task_title,
                project.task_statuses[0].id,
                description=task_desc,
            )


def main():
    api = init_taiga_api()
    project = api.projects.get_by_slug('taiga-test')

    filename = sys.argv[1]
    lines = readfile_as_array(filename)
    min_level = calc_min_level(lines)
    linums_us = get_linums(lines, min_level)
    level_task = min_level + 1

    create_us_and_task(project, lines, linums_us, level_task)


if __name__ == '__main__':
    main()
