import numpy as np

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from demo_ai import get_ai_2, create_data, map, test_ai

model = get_ai_2()

min_ok = 18
max_ok = 30

loc = 24
scale = 3

s = np.random.normal(loc=loc, scale=scale, size=100000)
X, Y = create_data(s, min_ok, max_ok)

model.fit([X], Y, batch_size=64, validation_split=0.2, epochs=25)

tests = np.random.normal(loc, scale, 100)
test_ai(model, tests, min_ok, max_ok)