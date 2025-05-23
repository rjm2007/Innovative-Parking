import cv2
import numpy as np
import pickle
import pandas as pd
from ultralytics import YOLO
import cvzone

with open('parking', 'rb') as f:
    data = pickle.load(f)
    polylines, area_names = data['polylines'], data['area_names']

my_file = open('coco.txt','r')
data = my_file.read()
class_list = data.split('\n')


model = YOLO('yolov8s.pt')

cap = cv2.VideoCapture('easy1.mp4')


count=0

while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
   
    count += 1
    if count % 3 != 0:
       continue

    frame=cv2.resize(frame,(1020,500))
    frame_copy = frame.copy()
    results = model(frame)
    a = results[0].boxes.data.cpu().numpy()  # Convert tensor to NumPy on CPU
    px = pd.DataFrame(a).astype("float") 
 #   print(results)
    #a=results[0].boxes.data
    #px=pd.DataFrame(a).astype("float")
#    print(px)
    list1=[]
    for index,row in px.iterrows():
#        print(row)
 
        x1=int(row[0])
        y1=int(row[1])
        x2=int(row[2])
        y2=int(row[3])
        d=int(row[5])
        
        c=class_list[d]
        cx=int(x1+x2)//2
        cy=int(y1+y2)//2
        if 'car' in c:
            list1.append([cx,cy])
         #  cv2.rectangle(frame,(x1,y1),(x2,y2),(255,255,255),2)
            
    counter1 = []    
    list2 = []  
    for i, polyline in enumerate(polylines):
        print(i)
        list2.append(i)
        cv2.polylines(frame, [polyline], True, (0, 255, 0), 2)
        cvzone.putTextRect(frame, f'{area_names[i]}', tuple(polyline[0]), 1, 1)
        for i1 in list1:
            cx1 = i1[0]
            cx2 = i1[1]
            results = cv2.pointPolygonTest(polyline,(cx1,cx2),False)
            if results>=0:
                print(results)
                cv2.circle(frame,(cx1,cx2),5,(255,0,0),-1)
                cv2.polylines(frame, [polyline], True, (0, 0, 255), 2)
                counter1.append(cx1)


        
     
    car_count = len(counter1)
    free_space = len(polylines) - car_count
    cvzone.putTextRect(frame,f'CARCOUNTER:-{car_count}',(50,60),2,2)
    cvzone.putTextRect(frame,f'Free Space :-{free_space}',(50,160),2,2)
              
    cv2.imshow('FRAME', frame)
    key = cv2.waitKey(1) & 0xFF
    
    
    if key == ord('q'):
        break



cap.release()

cv2.destroyAllWindows()
