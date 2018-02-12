# MIT License
#
# Copyright 2017-2018 Dmitry Vodopyanov, dmitry.vodopyanov@gmail.com
# Copyright 2017-2018 Atrem Kashkanov, radiolokn@gmail.com
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

import os
import uuid
import logging
import cv2

from src.utils import Utils

log = logging.getLogger('fr3onn')


class DataBase:
    def __init__(self):
        self.name = None
        self.working_dir = os.getcwd()
        self.db_dir = os.path.join(self.working_dir, 'db')
        self.utils = Utils()

    def add_person(self, name, frame):
        try:
            log.info("Adding {} to database...".format(name))
            file_name = os.path.join(self.db_dir, '{0}-{1}.jpg'.format(name, str(uuid.uuid4())))
            cv2.imwrite(file_name, frame)
            log.info("{0} was added to database to {1} file.".format(name, file_name))
            return file_name
        except Exception as ex:
            log.error("Failed to add person to database: {}".format(ex))

    @staticmethod
    def get_formatted_person_name(file_path):
        return file_path.split('/')[-1].split('-')[0]

    def remove_person(self, name):
        log.info("Removing all {}-* images from database...".format(name))
        files = self.utils.get_files_from_folder_recursively(self.get_db_dir(), pattern='^{}-.*$'.format(name))
        if files:
            for file in files:
                if os.path.isfile(file):
                    os.remove(file)
                log.info("Person with name {} was successfully removed from database.".format(name))
        else:
            log.warning("Person with name {} is not in database. Nothing to remove.".format(name))

    def set_db_dir(self, db_dir):
        if db_dir:
            self.db_dir = db_dir
        try:
            if not os.path.exists(self.db_dir):
                os.makedirs(self.db_dir)
                log.info("Database folder was created in {}.".format(self.db_dir))
            else:
                log.info("Using database from {} folder.".format(self.db_dir))
        except Exception as ex:
            raise Exception('Unable to initialize database folder: {}'.format(ex))

    def get_db_dir(self):
        return self.db_dir

    def get_all_persons(self):
        return self.utils.get_files_from_folder_recursively(self.db_dir, pattern=r'^.*\.(jpg|png|tiff|bmp)$')
