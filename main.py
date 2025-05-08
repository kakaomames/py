from flask import Flask, request
import subprocess
import os

app = Flask(__name__)
APK_DIR = "/tmp/apk"
os.makedirs(APK_DIR, exist_ok=True)

@app.route('/')
def index():
    return '''
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="apk">
        <input type="submit" value="アップロードして起動">
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    apk_file = request.files['apk']
    apk_path = os.path.join(APK_DIR, apk_file.filename)
    apk_file.save(apk_path)

    subprocess.run(["sudo", "waydroid", "init"], check=False)
    subprocess.run(["sudo", "waydroid", "start"], check=False)

    subprocess.run(["sleep", "10"])
    subprocess.run(["waydroid", "shell", "pm", "install", apk_path])

    return "Waydroid に APK をインストールしました！"

if __name__ == '__main__':
    # Xvfb 起動
    subprocess.Popen(["Xvfb", ":1"])
    os.environ["DISPLAY"] = ":1"

    # scrcpy 起動
    subprocess.Popen([
        "scrcpy",
        "--no-control",
        "--display-buffer=0",
        "--fullscreen",
        "--window-title=App",
        "--max-fps=30"
    ])

    # ffmpeg によるストリーム送信
    subprocess.Popen([
        "ffmpeg",
        "-f", "x11grab",
        "-i", ":1",
        "-r", "30",
        "-vcodec", "libx264",
        "-preset", "ultrafast",
        "-f", "mpegts",
        "http://localhost:8090"
    ])

    # Flask アプリ起動
    app.run(host='0.0.0.0', port=8080)
