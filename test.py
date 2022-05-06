from backend import BackendBase
from configparser import ConfigParser
parser = ConfigParser()
parser.read('./config.ini')

b = BackendBase(confparser=parser)

b.import_data_json('t.json', 'tabl')
data = b.get_all_data('tabl')
print(data)