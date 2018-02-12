#!/usr/bin/env python3

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

import os
import sys
import logging
import argparse
import traceback
import mraa
import time

from src.camera import Camera
from src.face_recognition import FaceRecognition
from src.db import DataBase
from src.utils import Utils
from src.logger import init_logger
from src import logger

__version__ = '0.0.2'

log = logging.getLogger('fr3onn')


class DefaultHelpParser(argparse.ArgumentParser):
    # Display help message in case of error
    # http://stackoverflow.com/questions/4042452/display-help-message-with-python-argparse-when-script-is-called-without-any-argu
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(-2)


class Launcher:
    def __init__(self):
        self.args = self.create_parser().parse_args()
        self.db = DataBase()
        self.utils = Utils()
        self.face_recognition = FaceRecognition()
        self.camera = Camera(int(self.args.camera) if str(self.args.camera).isdigit() else self.args.camera)
        self.lock = mraa.Gpio(20)
        self.green_light = mraa.Gpio(32)
        self.is_door_opened = mraa.Gpio(26)
        self.quit = mraa.Gpio(18)
        self.remember_new_face = mraa.Gpio(16)
        self.pin = mraa.Gpio(12)
        self.exit_code = 0
        self.log_folder = None
        self.create_logger()

    @staticmethod
    def create_parser():
        parser = DefaultHelpParser(prog='fr3onn', description='Face Recognition with 3D imaging, '
                                                              'OpenCV and Neural Nets',
                                   formatter_class=argparse.RawTextHelpFormatter, add_help=True)
        parser.add_argument('-c', '--camera', metavar='CAMERA', required=False, default=0,
                            help='Device index, 0 by default')
        parser.add_argument('-d', '--db_dir', metavar='DB_DIR', required=False, default=None,
                            help='Path to database, <FR3ONN_DIR>/db by default')
        parser.add_argument('-v', '--version', action='version', help='Show version and exit', version=__version__)
        return parser

    def create_logger(self):
        self.log_folder = os.path.join(os.getcwd(), 'logs', self.utils.get_formatted_datetime())
        init_logger(self.log_folder)

    def header(self):
        log.info(self.utils.line_double)
        log.info('Face Recognition with 3D imaging, OpenCV and Neural Nets')
        log.info(self.utils.line_double)
        log.info('Log folder:  {}'.format(self.log_folder))
        log.info('Python:      {}'.format(sys.executable))
        log.info(self.utils.line_double)

    def open_lock(self):
        self.lock.write(1)
        time.sleep(1)
        self.lock.write(0)

    def green_light_on(self):
        self.green_light.write(1)

    def green_light_off(self):
        self.green_light.write(0)

    def main(self):
        try:
            self.header()
            self.db.set_db_dir(self.args.db_dir)
            self.face_recognition.initialize_face_encodings(self.db.get_all_persons())
            self.lock.dir(mraa.DIR_OUT)
            self.green_light.dir(mraa.DIR_OUT)
            self.is_door_opened.dir(mraa.DIR_IN)
            self.quit.dir(mraa.DIR_IN)
            self.remember_new_face.dir(mraa.DIR_IN)
            self.pin.dir(mraa.DIR_OUT) 
            self.pin.write(1)
            process_this_frame = True
            while True:
                frame = self.camera.get_frame()
                if process_this_frame:
                    name = self.face_recognition.recognize(frame)
                    if name:
                        log.info(self.utils.line_double)
                        log.info('**Access PROVIDED** to {}'.format(self.db.get_formatted_person_name(name)))
                        self.green_light_on()
                        if not self.is_door_opened.read():
                            self.open_lock()
                        log.info(self.utils.line_double)
                    else:
                        log.info('**Access DENIED**')
                        self.green_light_off()
                process_this_frame = not process_this_frame 
                if not self.remember_new_face.read() and frame is not None:
                    log.info('Starting to add you to database...')
                    name = 'Registered User'
                    file_name = self.db.add_person(name, frame)
                    self.face_recognition.add_new_face_encoding(file_name)
                    while not self.remember_new_face.read():
                        time.sleep(0.1)
                if not self.quit.read() and frame is not None:
                    log.info('Tumbler switch was pressed. Quit.')
                    break
        except KeyboardInterrupt:
            logger.switch_to_summary()
            log.info(self.utils.line_single)
            log.error('PROGRAM WAS INTERRUPTED')
            log.info(self.utils.line_single)
            self.exit_code = -1
        except Exception as ex:
            logger.switch_to_summary()
            log.info(self.utils.line_single)
            log.error('Something goes wrong **FAILED**:\n{} '.format(ex))
            log.error('Error: {}'.format(traceback.format_exc()))
            log.info(self.utils.line_single)
            self.exit_code = -2
        return self.exit_code


if __name__ == '__main__':
    sys.exit(Launcher().main())
