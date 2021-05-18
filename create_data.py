import numpy as np
import json
import datetime

WANTED_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
def create(fp, n=10000):
    xs = np.linspace(-2*np.pi, 2*np.pi, n)


    date = datetime.datetime.now()
    data = {
        'date': [],
        'sensor1': [np.float32(i).item() for i in (np.sin(xs + np.pi/4))],
        'sensor2': [np.float32(i).item() for i in (np.sin(xs + np.pi/2))],
        'sensor3': [np.float32(i).item() for i in (np.sin(xs - np.pi/4))],
    }
    for i in range(n):
        dt = date + datetime.timedelta(0, 60 * i)
        st = datetime.datetime.strftime(dt, WANTED_DATETIME_FORMAT)
        data['date'].append(st)


    # for _ in range(10):
    #     p = np.random.randint(0, n)
    #     l = ['sensor1', 'sensor2', 'sensor3'][np.random.randint(0, 3)]
    #     data[l][p] += np.float32((np.random.rand(1) - 0.5)).item()

    with open(fp, 'w') as f:
        json.dump(data, f)