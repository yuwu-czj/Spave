import os
import subprocess
import time
from flask import Flask, render_template, jsonify, send_from_directory
from music21 import *
import random
import shutil
from PIL import Image, ImageDraw, ImageFont
import sys

app = Flask(__name__)

# 獲取項目根目錄
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')

# 設置環境變量
os.environ['PATH'] = os.environ['PATH'] + ';C:\Program Files\MuseScore 4\bin'

def find_musescore():
    # 新增更多可能的路徑
    possible_paths = [
        # MuseScore Studio 4 路徑
        r'C:\Users\czhen\AppData\Local\Programs\MuseScore Studio 4\bin\MuseScore4.exe',
        r'C:\Users\czhen\AppData\Local\Programs\MuseScore Studio 4\MuseScore4.exe',
        # MuseScore 4 路徑
        r'C:\Program Files\MuseScore 4\bin\MuseScore4.exe',
        r'C:\Program Files (x86)\MuseScore 4\bin\MuseScore4.exe',
        # MuseScore Studio 4 其他可能路徑
        r'C:\Program Files\MuseScore Studio 4\bin\MuseScore4.exe',
        r'C:\Program Files (x86)\MuseScore Studio 4\bin\MuseScore4.exe',
        # 搜索所有用戶的 AppData
        os.path.expandvars(r'%LOCALAPPDATA%\Programs\MuseScore Studio 4\bin\MuseScore4.exe'),
        os.path.expandvars(r'%LOCALAPPDATA%\Programs\MuseScore 4\bin\MuseScore4.exe')
    ]
    
    # 檢查所有可能的路徑
    for path in possible_paths:
        if os.path.exists(path):
            print(f"找到 MuseScore：{path}")
            return path
    
    # 如果沒找到，搜索整個 Program Files 目錄
    program_files_dirs = [
        os.environ.get('ProgramFiles', r'C:\Program Files'),
        os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'),
        os.environ.get('LOCALAPPDATA', '')
    ]
    
    for directory in program_files_dirs:
        if not directory:
            continue
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower() == 'musescore4.exe':
                    path = os.path.join(root, file)
                    print(f"在系統中找到 MuseScore：{path}")
                    return path
    
    print("警告：無法找到 MuseScore，請手動提供路徑")
    return None

# 設置 MuseScore 路徑
musescore_path = find_musescore()

if musescore_path:
    print(f"使用 MuseScore 路徑：{musescore_path}")
    # 設置環境變量
    os.environ['MUSESCORE_PATH'] = musescore_path
    
    # 設置 music21 環境
    us = environment.UserSettings()
    us['musicxmlPath'] = musescore_path
    us['musescoreDirectPNGPath'] = musescore_path
    us['graphicsPath'] = musescore_path
else:
    print("警告：找不到 MuseScore")
    print("請按照以下步驟操作：")
    print("1. 確認 MuseScore Studio 4 已安裝")
    print("2. 在檔案總管中找到 MuseScore4.exe 的位置")
    print("3. 將完整路徑提供給我們")

def create_music(style='random'):
    try:
        # 創建樂譜
        score = stream.Score()
        
        # 添加標題和作曲者
        score.insert(0, metadata.Metadata())
        score.metadata.title = f'自動生成的{style}風格樂譜'
        score.metadata.composer = 'AI 作曲家'
        
        # 創建主要聲部
        part = stream.Part()
        
        # 定義不同風格的音符範圍、時值和表情
        styles = {
            'random': {
                'notes': ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5'],
                'durations': [4.0, 2.0, 1.0, 0.5],  # 全音符、二分音符、四分音符、八分音符
                'dynamics': ['p', 'mp', 'mf', 'f'],
                'articulations': [articulations.Staccato(), articulations.Accent(), None]
            },
            'lyrical': {
                'notes': ['C4', 'E4', 'G4', 'A4', 'C5'],
                'durations': [2.0, 1.5, 1.0],  # 二分音符、附點四分音符、四分音符
                'dynamics': ['p', 'mp'],
                'articulations': [articulations.Tenuto(), None]
            },
            'energetic': {
                'notes': ['G4', 'A4', 'B4', 'C5', 'D5', 'E5'],
                'durations': [0.5, 0.25],  # 八分音符、十六分音符
                'dynamics': ['f', 'ff'],
                'articulations': [articulations.Accent(), articulations.Staccato()]
            }
        }
        
        style_data = styles.get(style, styles['random'])
        
        # 添加基本元素
        part.append(clef.TrebleClef())
        part.append(meter.TimeSignature('4/4'))
        part.append(key.KeySignature(0))
        
        # 添加速度標記
        if style == 'lyrical':
            part.append(tempo.MetronomeMark(number=72, text='Andante'))
        elif style == 'energetic':
            part.append(tempo.MetronomeMark(number=120, text='Allegro'))
        else:
            part.append(tempo.MetronomeMark(number=96, text='Moderato'))
        
        # 生成音樂
        measures = 8  # 8小節
        for measure_num in range(measures):
            m = stream.Measure(number=measure_num + 1)
            
            # 每小節的時值總和
            current_sum = 0.0
            
            # 決定是否添加休止符
            if random.random() < 0.2:  # 20% 機率添加休止符
                rest_duration = random.choice([1.0, 2.0])
                r = note.Rest(quarterLength=rest_duration)
                m.append(r)
                current_sum += rest_duration
            
            # 填充剩餘的小節
            while current_sum < 4.0:
                # 選擇可用的時值
                available_durations = [d for d in style_data['durations'] 
                                    if current_sum + d <= 4.0]
                if not available_durations:
                    break
                
                duration = random.choice(available_durations)
                
                # 決定是音符還是休止符
                if random.random() < 0.1:  # 10% 機率為休止符
                    n = note.Rest(quarterLength=duration)
                else:
                    # 創建音符
                    note_str = random.choice(style_data['notes'])
                    n = note.Note(note_str, quarterLength=duration)
                    
                    # 添加力度標記
                    if random.random() < 0.3:  # 30% 機率添加力度
                        dynamic = random.choice(style_data['dynamics'])
                        n.dynamic = dynamic
                    
                    # 添加表情記號
                    if random.random() < 0.2:  # 20% 機率添加表情
                        articulation = random.choice(style_data['articulations'])
                        if articulation:
                            n.articulations.append(articulation)
                
                m.append(n)
                current_sum += duration
            
            # 如果小節未滿，添加休止符
            if current_sum < 4.0:
                r = note.Rest(quarterLength=4.0 - current_sum)
                m.append(r)
            
            # 添加小節線
            if measure_num == measures - 1:
                m.rightBarline = bar.Barline('final')
            else:
                m.rightBarline = bar.Barline('regular')
            
            part.append(m)
        
        # 添加反覆記號
        if random.random() < 0.3:  # 30% 機率添加反覆記號
            part.measure(1).leftBarline = bar.Repeat(direction='start')
            part.measure(measures).rightBarline = bar.Repeat(direction='end')
        
        score.append(part)
        return score
        
    except Exception as e:
        print(f"創建樂譜時發生錯誤：{str(e)}")
        raise

def get_next_filename(static_dir):
    """獲取下一個可用的文件名"""
    # 查找現有的 New*.png 文件
    existing_files = []
    for file in os.listdir(static_dir):
        if file.startswith('New') and file.endswith('.png'):
            try:
                # 提取數字部分
                num = file[3:-4]  # 去掉 'New' 和 '.png'
                if num:  # 如果有數字
                    existing_files.append(int(num))
                else:  # 如果是 'New.png'
                    existing_files.append(0)
            except ValueError:
                continue
    
    if not existing_files:  # 如果沒有現有文件
        return 'New.png'
    
    # 對現有文件重命名
    existing_files.sort()
    for i, num in enumerate(existing_files, 1):
        old_name = f'New{num if num > 0 else ""}.png'
        new_name = f'New{i}.png'
        old_path = os.path.join(static_dir, old_name)
        new_path = os.path.join(static_dir, new_name)
        if old_path != new_path and os.path.exists(old_path):
            try:
                if os.path.exists(new_path):
                    os.remove(new_path)
                os.rename(old_path, new_path)
                print(f"重命名 {old_name} 為 {new_name}")
            except Exception as e:
                print(f"重命名文件時出錯：{e}")
    
    return 'New.png'

def save_score(score, filename=None):
    try:
        print("\n=== 開始保存樂譜 ===")
        
        static_dir = STATIC_DIR
        print(f"靜態目錄：{static_dir}")
        
        # 確保目錄存在
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        xml_path = os.path.join(static_dir, 'temp.xml')
        png_path = os.path.join(static_dir, 'New.png')
        
        # 清理舊文件
        for path in [xml_path, png_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"已刪除：{path}")
                except Exception as e:
                    print(f"刪除文件失敗：{e}")
        
        # 保存 XML
        try:
            print("保存 XML...")
            score.write('musicxml', fp=xml_path)
            if not os.path.exists(xml_path):
                raise Exception("XML 文件未生成")
            
            # 檢查 XML 文件大小
            xml_size = os.path.getsize(xml_path)
            print(f"XML 文件大小：{xml_size} 字節")
            if xml_size < 100:
                raise Exception("XML 文件可能無效")
                
        except Exception as e:
            print(f"保存 XML 失敗：{e}")
            return None
        
        # 獲取 MuseScore 路徑
        musescore_exe = find_musescore()
        if not musescore_exe:
            print("找不到 MuseScore")
            return None
        
        # 轉換命令
        commands = [
            [musescore_exe, xml_path, "-o", png_path],        # 基本模式
            [musescore_exe, "-T", "0", xml_path, "-o", png_path],  # 無邊距模式
            [musescore_exe, "-j", xml_path, "-o", png_path]   # 無 GUI 模式
        ]
        
        for cmd in commands:
            try:
                print(f"執行命令：{' '.join(cmd)}")
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                print(f"命令返回碼：{process.returncode}")
                print(f"輸出：{process.stdout}")
                print(f"錯誤：{process.stderr}")
                
                # 檢查文件是否生成並且大小合適
                if os.path.exists(png_path):
                    png_size = os.path.getsize(png_path)
                    print(f"PNG 文件大小：{png_size} 字節")
                    if png_size > 1000:
                        print("PNG 生成成功")
                        return 'New.png'
                    else:
                        print("警告：PNG 文件太小")
                else:
                    print("警告：PNG 文件未生成")
                
                # 如果命令成功執行但文件未生成，等待一下
                if process.returncode == 0:
                    time.sleep(1)  # 等待1秒
                    if os.path.exists(png_path) and os.path.getsize(png_path) > 1000:
                        print("PNG 生成成功（延遲檢查）")
                        return 'New.png'
                
            except Exception as e:
                print(f"命令執行失敗：{e}")
        
        # 如果所有命令都失敗，嘗試使用 music21 直接轉換
        try:
            print("\n嘗試使用 music21 直接轉換...")
            score.write('png', fp=png_path)
            if os.path.exists(png_path) and os.path.getsize(png_path) > 1000:
                print("使用 music21 轉換成功")
                return 'New.png'
        except Exception as e:
            print(f"music21 轉換失敗：{e}")
        
        print("所有轉換方法都失敗")
        return None
        
    except Exception as e:
        print(f"保存過程錯誤：{e}")
        return None

@app.route('/')
def home():
    # 確保 static 目錄存在
    if not os.path.exists(STATIC_DIR):
        os.makedirs(STATIC_DIR)
    
    # 確保默認圖片存在
    default_image = os.path.join(STATIC_DIR, 'default_score.png')
    if not os.path.exists(default_image):
        init_static_folder()
    
    return render_template('music.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory(STATIC_DIR, filename)
    except Exception as e:
        print(f"提供靜態文件時出錯：{str(e)}")
        return jsonify({
            'success': False,
            'error': '無法讀取文件'
        }), 404

@app.route('/create_music/<style>')
def create_new_music(style='random'):
    try:
        print(f"\n開始生成{style}風格的樂譜...")
        
        # 生成樂譜
        score = create_music(style)
        if not score:
            return jsonify({
                'success': False,
                'error': '樂譜生成失敗'
            })
        
        # 保存樂譜
        filepath = save_score(score)
        if not filepath:
            return jsonify({
                'success': False,
                'error': '樂譜保存失敗'
            })
        
        # 添加時間戳防止快取
        timestamp = int(time.time())
        return jsonify({
            'success': True,
            'image_path': f'/static/{filepath}?t={timestamp}'
        })
        
    except Exception as e:
        print(f"生成音樂時發生錯誤：{str(e)}")
        return jsonify({
            'success': False,
            'error': '生成過程出錯'
        })

def init_static_folder():
    try:
        # 使用項目目錄下的 static 目錄
        static_dir = STATIC_DIR
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
            print(f"創建 static 目錄：{static_dir}")
        
        # 創建一個簡單的默認圖片
        default_image = os.path.join(static_dir, 'default_score.png')
        if not os.path.exists(default_image):
            # 創建一個白色背景的圖片
            img = Image.new('RGB', (800, 400), 'white')
            draw = ImageDraw.Draw(img)
            
            # 添加文字
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
                
            text = "點擊按鈕生成樂譜"
            text_width = draw.textlength(text, font=font)
            x = (800 - text_width) / 2
            y = 180
            
            draw.text((x, y), text, fill='black', font=font)
            
            # 保存圖片
            img.save(default_image)
            print("創建默認圖片成功")
            
    except Exception as e:
        print(f"初始化 static 資料夾時出錯：{str(e)}")

def check_musescore():
    musescore_exe = os.environ.get('MUSESCORE_PATH')
    if not musescore_exe:
        print("錯誤：未設置 MUSESCORE_PATH")
        return False
        
    if not os.path.exists(musescore_exe):
        print(f"錯誤：找不到 MuseScore：{musescore_exe}")
        return False
        
    try:
        # 測試 MuseScore 是否可用
        result = subprocess.run(
            [musescore_exe, "-v"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False
        )
        
        if result.returncode == 0:
            print(f"MuseScore 版本：{result.stdout.strip()}")
            return True
        else:
            print(f"MuseScore 測試失敗：{result.stderr}")
            return False
            
    except Exception as e:
        print(f"檢查 MuseScore 時出錯：{e}")
        return False

def check_static_directory():
    static_dir = STATIC_DIR
    print(f"檢查目錄：{static_dir}")
    
    try:
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        # 測試寫入權限
        test_file = os.path.join(static_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except Exception as e:
        print(f"目錄權限檢查失敗：{e}")
        return False

if __name__ == '__main__':
    print("開始初始化程序...")
    
    if not check_musescore():
        print("錯誤：MuseScore 設置不正確")
        sys.exit(1)
    
    if not check_static_directory():
        print("錯誤：static 目錄權限不足")
        sys.exit(1)
    
    init_static_folder()
    print("初始化完成，啟動 Flask 服務器...")
    app.run(debug=True) 