import os

script_path = os.path.dirname(os.path.abspath(__file__)) # 获取当前脚本的绝对路径
print("script_path:", script_path)
script_dir = os.path.dirname(script_path) # 获取当前脚本所在目录的绝对路径
print("script_dir:", script_dir)
jpg_path = os.path.join(script_path, "resource", "images", "tong_resized.jpg")
print("jpg_path:", jpg_path)
gif_path = os.path.join(script_path, "resource", "images", "tong.gif")
print("gif_path:", gif_path)
qss_path = os.path.join(script_path, "resource", "qss")
print("qss_path:", qss_path)