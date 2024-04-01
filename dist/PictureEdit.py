import os
import sys
import shutil
from datetime import datetime
from enum import Enum, auto

import tkinter, tkinter.filedialog
from PIL import Image
import cv2

FACE_ICON_FILE = 'smile.png' # アイコン画像
WM_FILE = 'watermark.png' # ウォーターマーク画像
CASCADE_FILE = 'haarcascade_frontalface_default.xml' # カスケードファイル

class Mode(Enum):
    BLG = auto() # ブログ用
    TMB = auto() # サムネイル用

def mask_face(img_cv, cascada, img_pil, mask):
    """"顔をアイコン画像で隠す
    :param img_cv : 元画像(OpenCV)
    :param cascade : カスケードファイル
    :param Img_pil : 元画像(PIL)
    :param mask : 顔を隠す用の元画像(PIL)
    """

    # 顔認識を実行
    faces = cascade.detectMultiScale(img_cv, scaleFactor=1.4)

    # 認識された顔にアイコンを張り付け
    for(x, y, w, h) in faces:
        mask = mask.resize((w, h))
        img_pil.paste(mask, (x,y), mask)

def make_img(img, img_name, mode, watermark, output_path):
    """画像をリサイズし、ウォーターマークを張り付け、別名で保存する
    :param img : 画像(PIL)
    :param img_name : 画像(PIL)ファイル名
    :param mode : Mode.BLGならブログ用、Mode.TMBならサムネイル用
    :param watermark : ウォーターマーク画像(PIL)
    :param output_path : 出力先フォルダーのパス
    """
    BLG_CHAR = '_s' # ブログ画像のファイル名に付加する文字列
    TMB_CHAR = '_tmb' # サムネイル画像のファイル名に付加する文字列
    MAX_W_BLG = 600 # ブログ画像の幅の上限
    MAX_H_BLG = 600 # ブログ画像の高さの上限
    MAX_W_TMB = 300 # サムネイル画像の幅の上限
    MAX_H_TMB = 300 # サムネイル画像の高さの上限

    # サイズ、ファイル名の末尾に付加する文字列を設定
    if(mode == Mode.BLG): # ブログ用
        w, h = MAX_W_BLG, MAX_H_BLG
        add_chr = BLG_CHAR
    elif(mode == Mode.TMB): # サムネイル用
        w, h = MAX_W_TMB, MAX_H_TMB
        add_chr = TMB_CHAR
    else:
        return None

    # リサイズ
    img.thumbnail((w, h))

    # ウォーターマークを追加
    w_img, h_img = img.size
    w_wm, h_wm = watermark.size
    img.paste(watermark, (w_img - w_wm, h_img - h_wm), watermark)

    # ファイル名に文字列を付加して保存
    fname, ext = os.path.splitext(img_name)
    print(fname)
    img.save(os.path.join(output_path, fname + add_chr + ext))

# 顔アイコン画像とウォーターマーク画像読込み
face_icon = Image.open(FACE_ICON_FILE)
watermark = Image.open(WM_FILE)

# 認識器生成
cascade = cv2.CascadeClassifier(CASCADE_FILE)

# 加工前の画像フォルダー選択
root = tkinter.Tk()
root.withdraw()
msg = '画像フォルダーを選択してください'
img_dir_path = tkinter.filedialog.askdirectory(title=msg)
if(not img_dir_path): # [キャンセル]クリック時の処理
    print('フォルダーを選んでください')
    sys.exit()

# 加工後の画像を保存するためのディレクトリ'output'を加工前の画像フォルダー内に作成
os.makedirs(os.path.join(img_dir_path, 'output'), exist_ok=True)
# ブログ画像を保存するためのディレクトリ'blog'を'output'内に作成
os.makedirs(os.path.join(img_dir_path, 'output', 'blog'), exist_ok=True)
# サムネイル画像を保存するためのディレクトリ'thumbnail'を'output'内に作成
os.makedirs(os.path.join(img_dir_path, 'output', 'thumbnail'), exist_ok=True)

picList = []
for file in os.listdir(img_dir_path):
    splits = os.path.splitext(file)
    if '.png' in splits[1]:
        picList.append(file)
    elif '.jpg' in splits[1]:
        picList.append(file)
    else:
        pass

# 加工元画像フォルダー内のファイル1つずつ処理
for img_file in picList:
    # 元画像読込(PIL)
    img_path = os.path.join(img_dir_path, img_file)
    img_pil = Image.open(img_path)

    # 顔認識用にOpenCVで元画像をグレースケールで別途読込
    img_cv = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    # 顔を隠す
    mask_face(img_cv, cascade, img_pil, face_icon)

    # ブログ用画像とサムネイル用画像を作成
    make_img(img_pil.copy(), img_file, Mode.BLG, watermark, os.path.join(img_dir_path, 'output', 'blog'))
    make_img(img_pil, img_file, Mode.TMB, watermark, os.path.join(img_dir_path, 'output', 'thumbnail'))

    # 画像(PIL)を閉じる
    img_pil.close()
