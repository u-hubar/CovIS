import logging
import sys

import psycopg2
import psycopg2.extras

import database.utils.config as config
from database.utils.decorators import use_cursor

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("CovIS-Database")


class CovisDB:
    def __init__(self):
        self.connection = self._connect()
        self._register_caster()

    @use_cursor
    def select_person(self, person_id, cursor):
        select_query = """
            SELECT *
            FROM CovIS.Person
            WHERE idPerson = %s
        """

        cursor.execute(select_query, (person_id,))

        person = cursor.fetchone()
        return person

    @use_cursor
    def insert_person(self, person, cursor):
        insert_query = """
            INSERT INTO CovIS.Person (isStudent, isStaff, eligibleToEnter)
            VALUES (%s, %s, %s)
            RETURNING idPerson
        """

        cursor.execute(insert_query, person)
        person_id = cursor.fetchone()["idperson"]

        return person_id

    @use_cursor
    def check_enter_permission(self, person_id, cursor):
        select_query = """
            SELECT eligibleToEnter
            FROM CovIS.Person
            WHERE idPerson = %s
        """

        cursor.execute(select_query, (person_id,))
        permission = cursor.fetchone()["eligibletoenter"]

        return permission

    @use_cursor
    def update_person_status(self, person_id, elig, cursor):
        update_query = """
            UPDATE CovIS.Person
            SET eligibleToEnter = %s
            WHERE idPerson = %s
        """

        cursor.execute(update_query, (elig, person_id))

    @use_cursor
    def update_enter_time(self, person_id, time, cursor):
        update_query = """
            UPDATE CovIS.Person
            SET enterTime = %s
            WHERE idPerson = %s
        """

        cursor.execute(update_query, (time, person_id))

    @use_cursor
    def update_exit_time(self, person_id, time, cursor):
        update_query = """
            UPDATE CovIS.Person
            SET exitTime = %s
            WHERE idPerson = %s
        """

        cursor.execute(update_query, (time, person_id))

    @use_cursor
    def reset_time(self, cursor):
        update_query = """
            UPDATE CovIS.Person
            SET eligibleToEnter = FALSE,
            enterTime = NULL,
            exitTime = NULL
        """

        cursor.execute(update_query)

    @use_cursor
    def get_face_features(self, cursor):
        select_query = """
            SELECT *
            FROM CovIS.FaceFeatures
        """

        cursor.execute(select_query)

        face_features = cursor.fetchall()
        return face_features

    @use_cursor
    def insert_face_features(self, features, cursor):
        insert_query = f"""
            INSERT INTO CovIS.FaceFeatures (idPerson, {', '.join([f"feature{i}" for i in range(1, 129)])})
            VALUES %s
        """

        psycopg2.extras.execute_values(
            cursor, insert_query, features
        )

    def _register_caster(self):
        DEC2FLOAT = psycopg2.extensions.new_type(
            psycopg2.extensions.DECIMAL.values,
            'DEC2FLOAT',
            lambda value, curs: float(value) if value is not None else None)
        psycopg2.extensions.register_type(DEC2FLOAT)

    def _connect(self):
        logger.info("Connecting to PG Database...")
        connection = psycopg2.connect(
            dbname=config.PG_DBNAME,
            user=config.PG_USR,
            password=config.PG_PSWD,
            host=config.PG_HOST,
            port=config.PG_PORT,
        )
        logger.info("Successfully connected to PG Database!")

        connection.autocommit = True

        return connection
