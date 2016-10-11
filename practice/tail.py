# coding:utf-8
import os
import sys
import threading


def tailf(path):
    # 初始文件指针
    offset = 0
    event = threading.Event()
    try:
        while not event.is_set():
            with open(path) as f:
                # 判断文件是否被截断(清空/覆盖), 如果是的话则将文件指针置为0
                if offset > os.stat(path).st_size:
                    offset = 0
                f.seek(offset)
                # yield fron 等同 for line in f: yield line
                yield from f
                # 获取当前文件指针
                offset = f.tell()
            # wait等同sleep，但sleep是不可打断的，而wait可以
            event.wait(1)
    except KeyboardInterrupt:
        event.set()


if __name__ == '__main__':
    for line in tailf(sys.argv[1]):
        print(line, end='')
