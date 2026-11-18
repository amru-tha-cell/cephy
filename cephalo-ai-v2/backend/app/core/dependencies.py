
from threading import Lock

from app.inference.predictor import Predictor

# One model instance for the entire application
predictor = Predictor()

# Prevent concurrent requests from changing shared MC Dropout state
inference_lock = Lock()
