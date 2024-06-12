# -*- encoding: utf-8 -*-
import os
from datetime import datetime

import cv2
import numpy as np
from flask import Blueprint, Flask, Response, render_template, request
from flask_cors import CORS
from flask_login import login_required
from jinja2 import TemplateNotFound
from ultralytics import YOLO

from apps.config import API_GENERATOR

blueprint = Blueprint('home', __name__)
app = Flask(__name__)
CORS(app)

# YOLOv8 모델 로드
model = YOLO('C:/Users/user/Desktop/JJW/05. master course/수업/2024년 1학기/AI융합프로젝트/코드/flask-soft-ui-dashboard-master/model/best.pt')


def save_frame(frame, detection_count):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"detected_{detection_count}_{timestamp}.jpg"
    filepath = os.path.join('C:/Users/user/Desktop/JJW/05. master course/수업/2024년 1학기/AI융합프로젝트/코드/flask-soft-ui-dashboard-master/detections', filename)
    if not os.path.exists('C:/Users/user/Desktop/JJW/05. master course/수업/2024년 1학기/AI융합프로젝트/코드/flask-soft-ui-dashboard-master/detections'):
        os.makedirs('C:/Users/user/Desktop/JJW/05. master course/수업/2024년 1학기/AI융합프로젝트/코드/flask-soft-ui-dashboard-master/detections')
    cv2.imwrite(filepath, frame)

def gen_frames():
    camera = cv2.VideoCapture(0)  # 웹 카메라 사용
    detection_count = 0
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # YOLO 객체 감지
            results = model(frame)

            # 감지된 객체가 임계값 이상일 때 결과 프레임에 그리기
            detection_flag = False
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    if box.conf[0] > 0.7:  # 임계값 설정
                        detection_flag = True
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = box.conf[0]
                        cls = int(box.cls[0])
                        label = model.names[cls]
                        
                        # Draw bounding box
                        color = (0, 255, 0) # Green color for bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # if detection_flag:
                        detection_count += 1
                        save_frame(frame, detection_count)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@blueprint.route('/video_feed')
def video_feed():
    try:
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        return str(e), 500

@blueprint.route('/index')
@login_required
def index():
    try:
        return render_template('home/index.html', segment='index', API_GENERATOR=len(API_GENERATOR))
    except Exception as e:
        return str(e), 500

@blueprint.route('/fire_event')
def fire_event():
    try:
        return render_template('home/fire_event.html')
    except Exception as e:
        return str(e), 500

@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'
        
        segment = get_segment(request)
        return render_template("home/" + template, segment=segment, API_GENERATOR=len(API_GENERATOR))
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except Exception as e:
        print(f"Error: {e}")
        return render_template('home/page-500.html'), 500

def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except Exception as e:
        return None
