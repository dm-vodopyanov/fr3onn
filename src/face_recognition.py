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

import logging
import face_recognition
# TODO: import RealSense here

log = logging.getLogger('fr3onn')


class FaceRecognition:
    def __init__(self):
        self.face_encodings = []
        self.face_file_names = []

    def initialize_face_encodings(self, images):
        log.info('Initialize encodings of known faces from database...')
        try:
            # clean previous face encodings and file names
            self.face_encodings = []
            self.face_file_names = []
            for image in images:
                face = face_recognition.load_image_file(image)
                if face_recognition.face_encodings(face):
                    self.face_encodings.append(face_recognition.face_encodings(face)[0])
                self.face_file_names.append(image)
        except Exception as ex:
            raise Exception('Failed to initialize encodings: {}'.format(ex))
        log.info('Initialization finished successfully. {} faces were processed.'.format(len(images)))

    def add_new_face_encoding(self, image):
        log.info('Create encoding for new face...')
        try:
            face = face_recognition.load_image_file(image)
            if face_recognition.face_encodings(face):
                self.face_encodings.append(face_recognition.face_encodings(face)[0])
            self.face_file_names.append(image)
        except Exception as ex:
            raise Exception('Failed to create encoding: {}'.format(ex))
        log.info('Creating finished successfully.')

    def get_face_encodings(self):
        return self.face_encodings

    def get_file_names(self):
        return self.face_file_names

    def recognize(self, frame):
        name = None
        try:
            # Find all sub-images of faces -
            # see result: https://github.com/ageitgey/face_recognition#find-faces-in-pictures
            # face_locations = face_recognition.face_locations(frame)
            sel_top = 0
            sel_right = 0
            sel_bottom = 0
            sel_left = 0
            LOW_THRSHOLD = 64 * 64  # simple NMS
            any_selection = False
            dist_to_centre = 0
            img_h, img_w = frame.shape[:2]
            centre_x = img_w / 2
            centre_y = img_h / 2
            face_locations = face_recognition.face_locations(frame)
            for face_location in face_locations:
                top, right, bottom, left = face_location
                width = bottom - top
                height = right - left
                delta_x = top + width / 2
                delta_y = left + height / 2
                if width * height > LOW_THRSHOLD:
                    if not any_selection:
                        sel_top = top
                        sel_right = right
                        sel_bottom = bottom
                        sel_left = left
                        any_selection = True
                        dist_to_centre = (centre_x - delta_x) * (centre_x - delta_x) + \
                                         (centre_y - delta_y) * (centre_y - delta_y)
                    dist = (centre_x - delta_x) * (centre_x - delta_x) + \
                           (centre_y - delta_y) * (centre_y - delta_y)
                    if dist < dist_to_centre:
                        sel_top = top
                        sel_right = right
                        sel_bottom = bottom
                        sel_left = left
                        dist_to_centre = dist
            # ? do we need to extend region?

            # TODO: somehow check depth of such sub-images using realsense
            # if an sub-image is flat, do not create face encoding for it
            # probably sub-image should be passed to face_recognition.face_encodings rather than frame
            strangers_face_encodings = face_recognition.face_encodings(frame[sel_top:sel_bottom, sel_left:sel_right])
            for strangers_face_encoding in strangers_face_encodings:
                match = face_recognition.compare_faces(self.face_encodings, strangers_face_encoding)
                n = min(len(match), len(self.get_file_names()))
                for i in range(n):
                    if match[i]:
                        name = self.get_file_names()[i]
                        break
            return name
        except Exception as ex:
            raise Exception('Something goes wrong: {}'.format(ex))

