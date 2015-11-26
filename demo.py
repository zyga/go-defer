#!/usr/bin/env python
from __future__ import print_function, absolute_import
from go_defer import with_defer, defer


def do_close(f):
    print("closing", f)
    f.close()


@with_defer
def main():
    print('opening demo-1.txt')
    f1 = open('demo-1.txt', 'rt')
    defer(do_close, f1)
    print('opening demo-2.txt')
    f2 = open('demo-2.txt', 'rt')
    defer(do_close, f2)
    print('returning...')


if __name__ == '__main__':
    main()
