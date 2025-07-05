import os
import sys
sys.path.append(os.path.dirname(__file__))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "savvy-theory-465003-h3-6dd2380177b2.json"
from synthesize import synthesize_text

voice_dir = os.path.join(os.path.dirname(__file__), "Voice")
if not os.path.exists(voice_dir):
    os.makedirs(voice_dir)

lines = [
    ("50分のタイマーを開始します", "timer_start.mp3"),
    ("49分のタイマーを開始します", "timer_start_49m.mp3"),
    ("48分のタイマーを開始します", "timer_start_48m.mp3"),
    ("47分のタイマーを開始します", "timer_start_47m.mp3"),
    ("46分のタイマーを開始します", "timer_start_46m.mp3"),
    ("45分のタイマーを開始します", "timer_start_45m.mp3"),
    ("44分のタイマーを開始します", "timer_start_44m.mp3"),
    ("43分のタイマーを開始します", "timer_start_43m.mp3"),
    ("42分のタイマーを開始します", "timer_start_42m.mp3"),
    ("41分のタイマーを開始します", "timer_start_41m.mp3"),
    ("40分のタイマーを開始します", "timer_start_40m.mp3"),
    ("39分以下のタイマーを開始します", "timer_start_39m.mp3"),
    # 以下は既存
    ("残り40分です", "remain_40m.mp3"),
    ("残り30分です", "remain_30m.mp3"),
    ("残り20分です", "remain_20m.mp3"),
    ("残り10分です", "remain_10m.mp3"),
    ("残り5分です", "remain_5m.mp3"),
    ("残り1分です", "remain_1m.mp3"),
    ("残り10秒です", "remain_10s.mp3"),
    ("9秒", "remain_9s.mp3"),
    ("8秒", "remain_8s.mp3"),
    ("7秒", "remain_7s.mp3"),
    ("6秒", "remain_6s.mp3"),
    ("5秒", "remain_5s.mp3"),
    ("4秒", "remain_4s.mp3"),
    ("3秒", "remain_3s.mp3"),
    ("2秒", "remain_2s.mp3"),
    ("1秒", "remain_1s.mp3"),
    ("終了です。", "end.mp3"),
]

for text, fname in lines:
    outpath = os.path.join(voice_dir, fname)
    synthesize_text(text, outpath)
    print(f"生成: {outpath}")
