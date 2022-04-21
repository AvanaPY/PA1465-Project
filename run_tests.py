import unittest
from tests import BackendTest, ready

if ready():
    unittest.main()
else:
    print(f'Not running unit tests: Not ready')