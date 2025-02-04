from tensorflow.keras.models import load_model
import numpy as np
import cv2
import io
from PIL import Image
import tensorflow as tf
import sys

sys.stdout.reconfigure(encoding='utf-8')
model = tf.keras.models.load_model('mymodel.h5')


def check(img):
    


    img = cv2.resize(img, (64, 64))
    img2 = np.expand_dims(img / 255, axis=0)
    y=model.predict(img2)[0][0]
    if y>0.7:
        return "YOU HAVE TUMOR!"
    else:
        return "YOU ARE SAFE"


    

    
