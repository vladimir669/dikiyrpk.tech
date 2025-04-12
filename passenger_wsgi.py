import sys
import os

sys.path.insert(0, "/home/d/dikiyrpk/dikiyrpk.beget.tech/venv/lib/python3.7/site-packages")
project_root = os.path.dirname(os.path.abspath(__file__)) + "/app"
sys.path.insert(0, project_root)

from app import app as application
