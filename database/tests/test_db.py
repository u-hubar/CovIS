from datetime import datetime

import numpy as np
from database.db import CovisDB
from psycopg2.extras import DictCursor


class TestDatabase:
    def setup_class(self):
        self.cleanup_tables = [
            "CovIS.Person",
            "CovIS.FaceFeatures",
        ]
        self.db = CovisDB()
        self._cleanup(self)

    def teardown_class(self):
        self.cleanup_tables = [
            "CovIS.Person",
            "CovIS.FaceFeatures",
        ]
        self._cleanup(self)
        self.db.connection.close()

    def teardown_method(self):
        self._cleanup()

    def test_insert_person(self):
        self.cleanup_tables = [
            "CovIS.Person",
        ]

        person_info = (
            True,  # isStudent
            False,  # isStaff
            False,  # eligibleToEnter
        )

        person_id = self.db.insert_person(person_info)

        select_query = """
            SELECT * FROM CovIS.Person
        """

        with self.db.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(select_query)
            person = cursor.fetchone()

        assert person["idperson"] == person_id
        assert person["isstudent"]
        assert not person["isstaff"]
        assert not person["eligibletoenter"]
        assert person["entertime"] is None
        assert person["exittime"] is None

    def test_select_person(self):
        self.cleanup_tables = [
            "CovIS.Person",
        ]

        person_info = (
            True,  # isStudent
            False,  # isStaff
            False,  # eligibleToEnter
        )

        person_id = self.db.insert_person(person_info)
        person = self.db.select_person(person_id)

        assert person["idperson"] == person_id
        assert person["isstudent"]
        assert not person["isstaff"]
        assert not person["eligibletoenter"]
        assert person["entertime"] is None
        assert person["exittime"] is None

    def test_update_person_status(self):
        self.cleanup_tables = [
            "CovIS.Person",
        ]

        person_info = (
            True,  # isStudent
            False,  # isStaff
            False,  # eligibleToEnter
        )

        person_id = self.db.insert_person(person_info)
        self.db.update_person_status(
            person_id,
            True  # eligibleToEnter
        )

        person = self.db.select_person(person_id)

        assert person["idperson"] == person_id
        assert person["isstudent"]
        assert not person["isstaff"]
        assert person["eligibletoenter"]
        assert person["entertime"] is None
        assert person["exittime"] is None

    def test_check_enter_permission(self):
        self.cleanup_tables = [
            "CovIS.Person",
        ]

        first_person_info = (
            True,
            False,
            False,
        )

        second_person_info = (
            False,
            True,
            True,
        )

        first_person_id = self.db.insert_person(first_person_info)
        second_person_id = self.db.insert_person(second_person_info)

        first_person_perm = self.db.check_enter_permission(first_person_id)
        second_person_perm = self.db.check_enter_permission(second_person_id)

        assert not first_person_perm
        assert second_person_perm

    def test_update_enter_time(self):
        self.cleanup_tables = [
            "CovIS.Person",
        ]

        person_info = (
            True,
            False,
            True,
        )

        person_id = self.db.insert_person(person_info)

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        self.db.update_enter_time(person_id, current_time)

        person = self.db.select_person(person_id)

        assert person["entertime"].strftime("%H:%M:%S") == current_time

    def test_update_exit_time(self):
        self.cleanup_tables = [
            "CovIS.Person",
        ]

        person_info = (
            True,
            False,
            True,
        )

        person_id = self.db.insert_person(person_info)

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        self.db.update_exit_time(person_id, current_time)

        person = self.db.select_person(person_id)

        assert person["exittime"].strftime("%H:%M:%S") == current_time

    def test_reset_time(self):
        self.cleanup_tables = [
            "CovIS.Person",
        ]

        first_person = (
            True,
            False,
            False,
        )

        second_person = (
            False,
            True,
            True,
        )

        first_person_id = self.db.insert_person(first_person)
        second_person_id = self.db.insert_person(second_person)

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        self.db.update_enter_time(first_person_id, current_time)
        self.db.update_exit_time(second_person_id, current_time)

        self.db.reset_time()

        select_query = """
            SELECT * FROM CovIS.Person
        """

        with self.db.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(select_query)
            persons = cursor.fetchall()

        assert all(
            p["entertime"] is None and p["exittime"] is None for p in persons
        )

    def test_insert_face_features(self):
        self.cleanup_tables = [
            "CovIS.Person",
            "CovIS.FaceFeatures",
        ]

        person_info = (
            True,
            False,
            True,
        )

        person_id = self.db.insert_person(person_info)

        face_features = np.random.uniform(low=-1.0, high=1.0, size=(50, 128))
        face_features = np.insert(
            face_features,
            0,
            [person_id] * face_features.shape[0],
            axis=1
        )

        self.db.insert_face_features(face_features)

        select_query = """
            SELECT * FROM CovIS.FaceFeatures
        """

        with self.db.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(select_query)
            ffs = cursor.fetchall()

        assert all(ff["idperson"] == person_id for ff in ffs)
        assert len(ffs) == 50
        assert all(len(ff) == 130 for ff in ffs)

    def test_get_face_features(self):
        self.cleanup_tables = [
            "CovIS.Person",
            "CovIS.FaceFeatures",
        ]

        person_info = (
            True,
            False,
            True,
        )

        person_id = self.db.insert_person(person_info)

        face_features = np.random.uniform(low=-1.0, high=1.0, size=(50, 128))
        face_features = np.insert(
            face_features,
            0,
            [person_id] * face_features.shape[0],
            axis=1
        )

        self.db.insert_face_features(face_features)

        ffs = self.db.get_face_features()

        assert all(ff["idperson"] == person_id for ff in ffs)
        assert len(ffs) == 50
        assert all(len(ff) == 130 for ff in ffs)

    def _cleanup(self):
        with self.db.connection.cursor() as cursor:
            for table in self.cleanup_tables:
                cursor.execute(f"TRUNCATE {table} CASCADE")
            self.cleanup_tables = []
