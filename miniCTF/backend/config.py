from re import DEBUG
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "ctf.db")

TOTAL_LEVELS = 15
HOST = "0.0.0.0"
PORT = 8000
DEBUG = False