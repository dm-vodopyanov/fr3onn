# MIT License
#
# Copyright 2017-2018 Dmitry Vodopyanov, dmitry.vodopyanov@gmail.com
# Copyright 2017-2018 Artem Kashkanov, radiolokn@gmail.com
# Copyright 2017-2018 Sergey Shtin, sergey.shtin@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import datetime
import os
import re


class Utils:
    def __init__(self):
        self.line_double = '=' * 79
        self.line_single = '-' * 79

    @staticmethod
    def get_formatted_datetime():
        dt = datetime.datetime.now()
        dt_str = str(dt)
        dt_str = dt_str.partition('.')[0]
        dt_str = dt_str.split(' ')[0] + ' ' + dt_str.split(' ')[1]
        dt_str = dt_str.replace('-', '.')
        return dt_str.replace(':', '_').replace('.', '_').replace(' ', '_')

    @staticmethod
    def get_files_from_folder_recursively(src, pattern=None, folder_pattern=None):
        if not os.path.exists(src):
            return []
        files = []
        for root, dir_names, file_names in os.walk(src):
            for file_name in file_names:
                if (pattern is None or re.match(pattern, file_name, re.I)) \
                        and (folder_pattern is None or re.match(folder_pattern, root, re.I)):
                    files.append(os.path.join(root, file_name))
        return files
