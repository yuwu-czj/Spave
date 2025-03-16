from flask import Flask, render_template, jsonify, request, send_from_directory
import os
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

def generate_qcat():
    """生成Q版貓咪圖片"""
    try:
        # 創建更大的圖片尺寸以容納背景
        size = (600, 800)
        image = Image.new('RGB', size, '#87CEEB')  # 天空藍色背景
        draw = ImageDraw.Draw(image)

        # 隨機天氣效果
        weather = random.choice(['sunny', 'rainy', 'thunder'])
        
        # 繪製雲朵
        def draw_cloud(x, y, size):
            cloud_color = 'white' if weather == 'sunny' else '#666666'
            draw.ellipse([x, y, x+size, y+size], fill=cloud_color)
            draw.ellipse([x+size*0.5, y-size*0.2, x+size*1.5, y+size*0.8], fill=cloud_color)
            draw.ellipse([x+size, y, x+size*2, y+size], fill=cloud_color)

        # 添加多朵雲
        for _ in range(3):
            cloud_x = random.randint(0, size[0]-200)
            cloud_y = random.randint(20, 150)
            draw_cloud(cloud_x, cloud_y, 80)

        # 如果是下雨天，添加雨滴
        if weather in ['rainy', 'thunder']:
            for _ in range(50):
                rain_x = random.randint(0, size[0])
                rain_y = random.randint(0, size[1])
                draw.line(
                    [(rain_x, rain_y), (rain_x-15, rain_y+30)],
                    fill='#ADD8E6',
                    width=2
                )

        # 如果是打雷，添加閃電
        if weather == 'thunder':
            lightning_points = [
                (random.randint(100, size[0]-100), 0),  # 起點
                (random.randint(50, size[0]-50), 100),  # 轉折點
                (random.randint(0, size[0]), 200)       # 終點
            ]
            draw.line(lightning_points, fill='yellow', width=5)

        # 繪製地面
        ground_color = '#90EE90'  # 淺綠色草地
        draw.rectangle([0, size[1]-200, size[0], size[1]], fill=ground_color)

        # 繪製樹
        def draw_tree(x, y):
            # 樹幹
            draw.rectangle([x-20, y-150, x+20, y], fill='#8B4513')
            # 樹葉
            draw.ellipse([x-80, y-250, x+80, y-50], fill='#228B22')

        # 添加多棵樹
        for i in range(3):
            tree_x = random.randint(100, size[0]-100)
            draw_tree(tree_x, size[1]-200)

        # 繪製石頭
        def draw_rock(x, y, size):
            rock_color = '#808080'
            points = [
                (x, y),
                (x+size, y),
                (x+size*1.2, y-size*0.7),
                (x+size*0.8, y-size),
                (x-size*0.2, y-size*0.8)
            ]
            draw.polygon(points, fill=rock_color, outline='#696969')

        # 添加多個石頭
        for i in range(5):
            rock_x = random.randint(50, size[0]-100)
            rock_y = size[1]-180
            rock_size = random.randint(30, 50)
            draw_rock(rock_x, rock_y, rock_size)

        # 貓咪顏色
        cat_colors = {
            'orange': (255, 165, 0),
            'gray': (169, 169, 169),
            'brown': (139, 69, 19),
            'white': (255, 255, 255),
            'black': (45, 45, 45)
        }
        
        main_color = random.choice(list(cat_colors.values()))
        
        # 調整貓咪位置到新的畫布中心
        center_x = size[0] // 2
        center_y = size[1] - 300  # 讓貓咪站在地面上

        # 繪製貓咪身體（圓形）
        body_radius = 80
        draw.ellipse(
            [
                center_x - body_radius,
                center_y - body_radius,
                center_x + body_radius,
                center_y + body_radius
            ],
            fill=main_color,
            outline='black',
            width=3
        )

        # 繪製貓咪頭部（圓形）
        head_radius = 60
        head_y = center_y - 70
        draw.ellipse(
            [
                center_x - head_radius,
                head_y - head_radius,
                center_x + head_radius,
                head_y + head_radius
            ],
            fill=main_color,
            outline='black',
            width=3
        )

        # 繪製耳朵（三角形）
        ear_size = 40
        # 左耳
        draw.polygon(
            [
                (center_x - 40, head_y - 50),
                (center_x - 60, head_y - 90),
                (center_x - 10, head_y - 60)
            ],
            fill=main_color,
            outline='black',
            width=3
        )
        # 右耳
        draw.polygon(
            [
                (center_x + 40, head_y - 50),
                (center_x + 60, head_y - 90),
                (center_x + 10, head_y - 60)
            ],
            fill=main_color,
            outline='black',
            width=3
        )

        # 繪製眼睛（橢圓）
        eye_width = 25
        eye_height = 35
        # 左眼
        draw.ellipse(
            [
                center_x - 40 - eye_width//2,
                head_y - eye_height//2,
                center_x - 40 + eye_width//2,
                head_y + eye_height//2
            ],
            fill='white',
            outline='black',
            width=3
        )
        # 右眼
        draw.ellipse(
            [
                center_x + 40 - eye_width//2,
                head_y - eye_height//2,
                center_x + 40 + eye_width//2,
                head_y + eye_height//2
            ],
            fill='white',
            outline='black',
            width=3
        )

        # 繪製瞳孔
        pupil_size = 12
        # 左瞳孔
        draw.ellipse(
            [
                center_x - 40 - pupil_size//2,
                head_y - pupil_size//2,
                center_x - 40 + pupil_size//2,
                head_y + pupil_size//2
            ],
            fill='black'
        )
        # 右瞳孔
        draw.ellipse(
            [
                center_x + 40 - pupil_size//2,
                head_y - pupil_size//2,
                center_x + 40 + pupil_size//2,
                head_y + pupil_size//2
            ],
            fill='black'
        )

        # 繪製鼻子（愛心形狀）
        nose_size = 10
        draw.polygon(
            [
                (center_x, head_y + 20),
                (center_x - nose_size, head_y + 10),
                (center_x + nose_size, head_y + 10)
            ],
            fill='pink',
            outline='black',
            width=2
        )

        # 繪製嘴巴（可愛的曲線）
        if random.random() > 0.5:
            # 微笑
            draw.arc(
                [center_x - 20, head_y + 20, center_x + 20, head_y + 40],
                0, 180, fill='black', width=3
            )
        else:
            # 貓咪嘴型
            draw.arc(
                [center_x - 15, head_y + 20, center_x + 15, head_y + 35],
                180, 360, fill='black', width=3
            )

        # 繪製鬍鬚
        whisker_length = 50
        whisker_y_positions = [head_y + 15, head_y + 25, head_y + 35]
        for y in whisker_y_positions:
            # 左側鬍鬚
            draw.line(
                [(center_x - 30, y), (center_x - 30 - whisker_length, y)],
                fill='black',
                width=2
            )
            # 右側鬍鬚
            draw.line(
                [(center_x + 30, y), (center_x + 30 + whisker_length, y)],
                fill='black',
                width=2
            )

        # 添加臉頰紅暈
        blush_radius = 12
        draw.ellipse(
            [
                center_x - 60 - blush_radius,
                head_y + 10 - blush_radius,
                center_x - 60 + blush_radius,
                head_y + 10 + blush_radius
            ],
            fill=(255, 192, 203, 128)
        )
        draw.ellipse(
            [
                center_x + 60 - blush_radius,
                head_y + 10 - blush_radius,
                center_x + 60 + blush_radius,
                head_y + 10 + blush_radius
            ],
            fill=(255, 192, 203, 128)
        )

        # 保存圖片
        timestamp = str(int(random.random() * 10000))
        filename = f'qcat_{timestamp}.png'
        filepath = os.path.join(IMAGES_DIR, filename)
        image.save(filepath)
        
        return f'/static/images/{filename}'
        
    except Exception as e:
        print(f"生成Q版貓咪時出錯：{str(e)}")
        return None

@app.route('/')
def home():
    return render_template('qcat.html')

@app.route('/generate_qcat', methods=['POST'])
def create_qcat():
    try:
        image_path = generate_qcat()
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
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    ensure_directories()
    app.run(debug=True) 