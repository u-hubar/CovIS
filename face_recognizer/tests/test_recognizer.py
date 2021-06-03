from face_recognizer.recognizer import Recognizer
from psycopg2.extras import DictCursor
import pathlib
import cv2


class TestRecognizer:
    def setup_class(self):
        self.cleanup_tables = [
            "CovIS.Person",
            "CovIS.FaceFeatures",
        ]
        self.recognizer = Recognizer()
        self._cleanup(self)

    def test_process_features(self):
        self.cleanup_tables = [
            "CovIS.Person",
            "CovIS.FaceFeatures"
        ]

        image_path = pathlib.Path(__file__).parent / "data/ok1.jpg"
        image = cv2.imread(str(image_path))

        person = (
            True,  # isStudent
            False,  # isStaff
            True,  # eligibleToEnter
        )
        person_id = self.recognizer.insert_person(person)

        self.recognizer.process_features(person_id, image)

        with self.recognizer.connection.cursor(cursor_factory=DictCursor) as cursor:
            query = """
                SELECT *
                FROM CovIS.FaceFeatures
                WHERE idPerson = %s
            """
            cursor.execute(query, (person_id,))
            face_features = cursor.fetchone()

        assert len(face_features) == 130

    def test_recognize(self):
        self.cleanup_tables = [
            "CovIS.Person",
            "CovIS.FaceFeatures"
        ]

        image1_path = pathlib.Path(__file__).parent / "data/ok1.jpg"
        image2_path = pathlib.Path(__file__).parent / "data/ok2.jpg"
        image1 = cv2.imread(str(image1_path))
        image2 = cv2.imread(str(image2_path))

        person = (
            True,
            False,
            True,
        )
        person_id = self.recognizer.insert_person(person)

        self.recognizer.process_features(person_id, image1)

        id, permission = self.recognizer.recognize(image2)

        assert id == person_id

    def teardown_class(self):
        self.cleanup_tables = [
            "CovIS.Person",
            "CovIS.FaceFeatures",
        ]
        self._cleanup(self)
        self.recognizer.connection.close()

    def teardown_method(self):
        self._cleanup()

    def _cleanup(self):
        with self.recognizer.connection.cursor() as cursor:
            for table in self.cleanup_tables:
                cursor.execute(f"TRUNCATE {table} CASCADE")
            self.cleanup_tables = []
