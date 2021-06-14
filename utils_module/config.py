# PostgreSQL
PG_DBNAME = "CovIS"
PG_USR = "postgres"
PG_PSWD = "Df5#0Strq"
PG_HOST = "192.168.0.105"
PG_PORT = "5432"

# Face detection
FACE_DETECTION_PROTOTXT = "models/deploy.prototxt"
FACE_DETECTION_MODEL = "models/res10_300x300_ssd_iter_140000.caffemodel"

# Mask recognition
MASK_REC_MODEL = "models/mask_rec_model.pt"

# GUI
WIDTH = 1800
HEIGHT = 900

# Cameras
RECOGNITION_CAMERA = "192.168.0.102"
CAMERAS = {
    "1": {
        "Name": "Camera 1",
        "IP": "192.168.0.102"
    },
    "2": {
        "Name": "Camera 2",
        "IP": "192.168.0.104"
    },
    "3": {
        "Name": "",
        "IP": ""
    },
    "4": {
        "Name": "",
        "IP": ""
    },
    "5": {
        "Name": "",
        "IP": ""
    },
    "6": {
        "Name": "",
        "IP": ""
    }
}
CAMERAS_IN_ROW = len(CAMERAS) if len(CAMERAS) < 3 else 3
