import cv2
from ultralytics import YOLO
import sys
import tensorflow as tf
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

cell_model = tf.keras.models.load_model(r'C:\Users\Divyansh\practium\mymodel.h5')

# Load YOLOv8 model

model = YOLO('yolov8n.pt')



def gen_giv(cap):

    while True:
        frame=cap
        """ret, frame = cap.read()

        if not ret:
            break"""

    
        results = model(frame)


        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                
            
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                
                cropped_frame = frame[y1:y2, x1:x2]

            
                img2 = cv2.resize(cropped_frame, (64, 64))
                img2 = np.expand_dims(img2 / 255.0, axis=0)

            
                prediction = cell_model.predict(img2)

        
                if prediction > 0.4:
                    frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        return frame
        """cv2.imshow('Live Object Detection', frame)

    
        if cv2.waitKey(0) == ord('q'):
            break"""



