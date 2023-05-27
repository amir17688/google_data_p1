#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (C) 2013-2015 Danilo Bargen

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
from __future__ import print_function, division, absolute_import, unicode_literals

import sys

from RPLCD import CharLCD


try:
    range = xrange
except NameError:  # Python 3
    pass

try:
    safe_input = raw_input
except NameError:  # Python 3
    safe_input = input

try:
    unichr = unichr
except NameError:  # Python 3
    unichr = chr


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: %s <rows> <cols>' % sys.argv[0])
        sys.exit(1)

    rows, cols = int(sys.argv[1]), int(sys.argv[2])
    lcd = CharLCD(cols=cols, rows=rows)

    print('This tool shows the character map of your LCD on the display.')
    print('Press ctrl+c at any time to abort.\n')

    page = 0
    chars = rows * cols

    try:
        while True:
            offset = page * chars
            start = offset
            end = offset + chars
            lcd.clear()
            for i in range(offset, offset + chars):
                if i > 255:
                    if i > start:
                        print('Displaying page %d (characters %d-%d).\nDone.' %
                              (page, start, i - 1))
                    else:
                        print('Done.')
                    sys.exit(0)
                lcd.write_string(unichr(i))
            page += 1
            safe_input('Displaying page %d (characters %d-%d). Press <ENTER> to continue.' %
                       (page, start, end - 1))
    except KeyboardInterrupt:
        print('Aborting.')

    lcd.clear()
