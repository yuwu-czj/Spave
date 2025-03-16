from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import time
from PIL import Image, ImageDraw, ImageFont
import random

app = Flask(__name__)

# 設置目錄
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')
IMAGES_DIR = os.path.join(STATIC_DIR, 'images')

def ensure_directories():
    """確保必要的目錄存在"""
    for directory in [STATIC_DIR, IMAGES_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"創建目錄：{directory}")

def generate_random_image(prompt, size=(512, 512)):
    """生成隨機圖片"""
    try:
        # 創建唯一的文件名
        timestamp = int(time.time())
        image_filename = f'image_{timestamp}.png'
        image_path = os.path.join(IMAGES_DIR, image_filename)

        # 創建圖片
        image = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(image)

        # 生成隨機背景色塊
        for _ in range(5):
            color = (
                random.randint(200, 255),
                random.randint(200, 255),
                random.randint(200, 255)
            )
            x1 = random.randint(0, size[0])
            y1 = random.randint(0, size[1])
            x2 = x1 + random.randint(100, 300)
            y2 = y1 + random.randint(100, 300)
            draw.rectangle([x1, y1, x2, y2], fill=color)

        # 添加一些裝飾圖形
        for _ in range(30):
            color = (
                random.randint(0, 200),
                random.randint(0, 200),
                random.randint(0, 200)
            )
            
            x = random.randint(0, size[0])
            y = random.randint(0, size[1])
            size_shape = random.randint(20, 60)
            
            shape_type = random.choice(['circle', 'square', 'triangle'])
            
            if shape_type == 'circle':
                draw.ellipse([x, y, x+size_shape, y+size_shape], fill=color)
            elif shape_type == 'square':
                draw.rectangle([x, y, x+size_shape, y+size_shape], fill=color)
            else:  # triangle
                draw.polygon([
                    (x, y+size_shape),
                    (x+size_shape//2, y),
                    (x+size_shape, y+size_shape)
                ], fill=color)

        # 添加提示文字
        try:
            # 嘗試加載中文字體
            font_paths = [
                "C:\\Windows\\Fonts\\simsun.ttc",  # Windows 宋體
                "C:\\Windows\\Fonts\\msyh.ttc",    # Windows 微軟雅黑
                "simsun.ttc",
                "msyh.ttc"
            ]
            
            font = None
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, 30)
                        break
                except:
                    continue
            
            if font is None:
                font = ImageFont.load_default()
            
            # 計算文字位置使其居中
            text_bbox = draw.textbbox((0, 0), prompt, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            # 添加文字陰影效果
            draw.text((x+2, y+2), prompt, font=font, fill='gray')
            draw.text((x, y), prompt, font=font, fill='black')
            
        except Exception as e:
            print(f"添加文字時出錯：{e}")
            # 使用基本字體
            draw.text((10, 10), prompt, fill='black')

        # 保存圖片
        image.save(image_path, 'PNG')
        print(f"圖片已保存：{image_path}")
        
        return f'/static/images/{image_filename}'
    
    except Exception as e:
        print(f"生成圖片時發生錯誤：{str(e)}")
        return None

@app.route('/')
def home():
    ensure_directories()
    return render_template('image.html')

@app.route('/generate_image', methods=['POST'])
def create_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({
                'success': False,
                'error': '請輸入圖片描述'
            })

        image_path = generate_random_image(prompt)
        
        if image_path:
            return jsonify({
                'success': True,
                'image_path': image_path
            })
        else:
            return jsonify({
                'success': False,
                'error': '生成圖片失敗'
            })

    except Exception as e:
        print(f"處理請求時發生錯誤：{str(e)}")
        return jsonify({
            'success': False,
            'error': '生成過程出錯'
        })

@app.route('/static/images/<path:filename>')
def serve_image(filename):
    try:
        return send_from_directory(IMAGES_DIR, filename)
    except Exception as e:
        print(f"提供圖片文件時出錯：{str(e)}")
        return jsonify({
            'success': False,
            'error': '無法讀取圖片文件'
        }), 404

if __name__ == '__main__':
    ensure_directories()
    print("伺服器啟動中...")
    app.run(debug=True) 