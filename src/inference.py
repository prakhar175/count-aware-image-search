from ultralytics import YOLO
from pathlib import Path
import torch
from PIL import Image
import numpy
from configs.config import CONF_THRESHOLD, YOLO_MODEL, IMAGE_EXTENSION

class YOLOInference:
    
    def __init__(self, model_name):
        self.model=YOLO(model_name)
        self.conf_threshold=CONF_THRESHOLD
        self.image_ext=IMAGE_EXTENSION
        
    def process_img(self, img_path):
        
        results = self.model.predict(
            source=img_path,
            conf=self.conf_threshold
            )
        detections=[]
        class_counts={}
        
        for result in results:
            for box in result.boxes:
                cls = result.names[int(box.cls)]
                conf = float(box.conf)
                bbox=box.xyxy[0].tolist()
                
                detections.append({
                    'class' :cls,
                    'conf':conf,
                    'bbox':bbox,
                    'count':1
                })
                class_counts[cls]=class_counts.get(cls,0) + 1
                
        for det in detections:
            det['count']=class_counts[det['class']]
        return {
            'img_path': str(img_path),
            'det':detections,
            'total_objects':len(detections),
            'unique_classes':list(class_counts.keys()),
            'class_counts':class_counts
        }

    def process_dir(self,img_dir):
        metadata=[]
        patterns=[i for i in self.image_ext]
        
        img_paths=[]
        for pattern in patterns:
            img_paths.extend(Path(img_dir).glob(pattern))
            
        for img_path in img_paths:
            metadata.extend(self.process_img(img_path))