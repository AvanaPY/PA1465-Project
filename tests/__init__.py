from .backendtest import BackendTest
from .backendtest import b

def ready():
    return b._my_db is not None