# PostgreSQL
PG_DBNAME = "CovIS"
PG_USR = "postgres"
PG_PSWD = "Df5#0Strq"
PG_HOST = "192.168.0.105"
PG_PORT = "5432"

# Face detection
FACE_DETECTION_PROTOTXT = "models/deploy.prototxt"
FACE_DETECTION_MODEL = "models/res10_300x300_ssd_iter_140000.caffemodel"

# GUI
WIDTH = 1800
HEIGHT = 900

# Cameras
CAMERAS = {
    "192.168.0.102": {
        "ID": 1,
        "IP": "192.168.0.102"
    },
    "Camera 2": {},
    "Camera 3": {},
    "Camera 4": {},
    "Camera 5": {},
    "Camera 6": {}
}
CAMERAS_IN_ROW = len(CAMERAS) if len(CAMERAS) < 3 else 3
