from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import time
import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2

app = Flask(__name__)

# 設置目錄
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')
ANIMATION_DIR = os.path.join(STATIC_DIR, 'animations')

def ensure_directories():
    """確保必要的目錄存在且可寫入"""
    for directory in [STATIC_DIR, ANIMATION_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        # 測試寫入權限
        test_file = os.path.join(directory, 'test.txt')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"目錄 {directory} 可寫入")
        except Exception as e:
            print(f"警告：目錄 {directory} 可能沒有寫入權限：{e}")

def generate_random_animation(theme, color_mode, duration=30, fps=24):
    """生成隨機動畫"""
    try:
        # 創建唯一的文件名
        timestamp = int(time.time())
        video_filename = f'animation_{timestamp}.mp4'
        video_path = os.path.join(ANIMATION_DIR, video_filename)

        # 設置視頻參數
        frame_size = (640, 480)
        total_frames = duration * fps
        
        # 嘗試不同的編碼器
        codecs = [
            ('mp4v', '.mp4'),
            ('avc1', '.mp4'),
            ('XVID', '.avi'),
            ('MJPG', '.avi')
        ]
        
        for codec, ext in codecs:
            try:
                # 更新文件名擴展名
                video_filename = f'animation_{timestamp}{ext}'
                video_path = os.path.join(ANIMATION_DIR, video_filename)
                
                # 創建視頻寫入器
                fourcc = cv2.VideoWriter_fourcc(*codec)
                out = cv2.VideoWriter(
                    video_path, 
                    fourcc, 
                    fps, 
                    frame_size, 
                    isColor=(color_mode == 'color')
                )
                
                if not out.isOpened():
                    print(f"編碼器 {codec} 初始化失敗，嘗試下一個...")
                    continue
                
                print(f"使用編碼器：{codec}")
                
                # 生成每一幀
                for i in range(total_frames):
                    # 創建空白圖像
                    frame = np.zeros((frame_size[1], frame_size[0], 3), dtype=np.uint8)
                    frame.fill(255)  # 設置白色背景
                    
                    if color_mode == 'color':
                        # 隨機顏色
                        color = (
                            random.randint(0, 255),
                            random.randint(0, 255),
                            random.randint(0, 255)
                        )
                    else:
                        # 黑白
                        gray = random.randint(0, 255)
                        color = (gray, gray, gray)

                    # 生成隨機圖形
                    shape_type = random.choice(['circle', 'rectangle', 'line'])
                    
                    if shape_type == 'circle':
                        center = (
                            random.randint(0, frame_size[0]),
                            random.randint(0, frame_size[1])
                        )
                        radius = random.randint(20, 100)
                        cv2.circle(frame, center, radius, color, -1)
                        
                    elif shape_type == 'rectangle':
                        pt1 = (
                            random.randint(0, frame_size[0] - 100),
                            random.randint(0, frame_size[1] - 100)
                        )
                        pt2 = (
                            pt1[0] + random.randint(50, 100),
                            pt1[1] + random.randint(50, 100)
                        )
                        cv2.rectangle(frame, pt1, pt2, color, -1)
                        
                    else:  # line
                        pt1 = (
                            random.randint(0, frame_size[0]),
                            random.randint(0, frame_size[1])
                        )
                        pt2 = (
                            random.randint(0, frame_size[0]),
                            random.randint(0, frame_size[1])
                        )
                        cv2.line(frame, pt1, pt2, color, random.randint(2, 10))

                    # 添加文字（使用中文）
                    font_path = os.path.join(PROJECT_ROOT, 'fonts', 'simsun.ttc')
                    if os.path.exists(font_path):
                        # 如果有中文字體文件，使用 PIL 添加文字
                        frame_pil = Image.fromarray(frame)
                        draw = ImageDraw.Draw(frame_pil)
                        font = ImageFont.truetype(font_path, 32)
                        draw.text((20, 20), theme, font=font, fill=color)
                        frame = np.array(frame_pil)
                    else:
                        # 否則使用 OpenCV 默認字體
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        cv2.putText(frame, theme, (20, 50), font, 1, color, 2)

                    # 寫入幀
                    out.write(frame)

                # 釋放資源
                out.release()
                
                # 檢查文件是否成功生成
                if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                    print(f"視頻生成成功：{video_path}")
                    return f'/static/animations/{video_filename}'
                    
            except Exception as e:
                print(f"使用編碼器 {codec} 時出錯：{str(e)}")
                continue
        
        print("所有編碼器都失敗")
        return None
    
    except Exception as e:
        print(f"生成動畫時發生錯誤：{str(e)}")
        return None

@app.route('/')
def home():
    return render_template('animation.html')

@app.route('/generate_animation', methods=['POST'])
def create_animation():
    try:
        data = request.get_json()
        theme = data.get('theme', '')
        color_mode = data.get('colorMode', 'color')

        if not theme:
            return jsonify({
                'success': False,
                'error': '請輸入主題'
            })

        video_path = generate_random_animation(theme, color_mode)
        
        if video_path:
            return jsonify({
                'success': True,
                'video_path': video_path
            })
        else:
            return jsonify({
                'success': False,
                'error': '生成動畫失敗'
            })

    except Exception as e:
        print(f"處理請求時發生錯誤：{str(e)}")
        return jsonify({
            'success': False,
            'error': '生成過程出錯'
        })

@app.route('/static/animations/<path:filename>')
def serve_animation(filename):
    try:
        return send_from_directory(ANIMATION_DIR, filename)
    except Exception as e:
        print(f"提供視頻文件時出錯：{str(e)}")
        return jsonify({
            'success': False,
            'error': '無法讀取視頻文件'
        }), 404

if __name__ == '__main__':
    ensure_directories()
    app.run(debug=True) 