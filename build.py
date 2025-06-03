import os
import subprocess
import shutil

def build_app():
    # 运行PyInstaller构建
    subprocess.run(['pyinstaller', 'main.spec'], check=True)
    
    # 确保dist目录存在
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    # 复制config文件夹到dist目录
    if os.path.exists('app/config'):
        shutil.copytree('app/config', 'dist/config', dirs_exist_ok=True)
    
    print("构建完成，config文件夹已复制到dist目录")

if __name__ == '__main__':
    build_app()