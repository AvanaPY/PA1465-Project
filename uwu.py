from backend import BackendBase
import ai

from configparser import ConfigParser
parser = ConfigParser()
parser.read('./config.ini')

# ai_model = ai.create_ai_model()
# ai.save_ai_model(ai_model, "frick.ai")

b = BackendBase(confparser=parser, ai_model="frick.ai", load_ai=False)