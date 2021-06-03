import logging
import sys

import numpy as np
from database.db import CovisDB

import face_recognition

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("CovIS-Recognizer")


class Recognizer(CovisDB):
    def __init__(self):
        super().__init__()

    def process_features(self, person_id, img):
        face_encodings = self._extract_features(img)
        self._save_features(person_id, face_encodings)

    def recognize(self, img):
        face_encoding = self._extract_features(img)
        face_encodings_all = np.array(self.get_face_features())

        matches = face_recognition.compare_faces(
            face_encodings_all[:, 2:], face_encoding[0]
        )
        face_distances = face_recognition.face_distance(
            face_encodings_all[:, 2:], face_encoding[0]
        )
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            person_id = face_encodings_all[best_match_index][1]
        else:
            person_info = (
                False,  # isStudent
                False,  # isStaff
                False,  # eligibleToEnter
            )
            person_id = self.insert_person(person_info)

            face_encoding = np.insert(
                face_encoding, 0, [person_id] * face_encoding.shape[0], axis=1
            )
            self.insert_face_features(face_encoding)

        person_permission = self.check_enter_permission(person_id)

        return (person_id, person_permission)

    def _extract_features(self, img):
        face_encodings = np.array(
            face_recognition.face_encodings(img)
        )

        return face_encodings

    def _save_features(self, person_id, face_encodings):
        face_encodings = np.insert(
            face_encodings, 0, [person_id] * face_encodings.shape[0], axis=1
        )

        self.insert_face_features(face_encodings)
