from flask_core.app import create_app
from flask_core.config import Config
import os

os.environ["FLAG"] = "12345"
os.environ["FLAG_IDS"] = "one,two,three"
os.environ["FLAG_WRAP"] = "TEST_FLAG"
os.environ["FLAG_SECRET"] = "1234_i_declare_a_thumb_war"
os.environ["DB_CONNECTION_STRING"] = "postgres://postgres@localhost/test"
app = create_app(config=Config())
