import os
import sys
import threading
import time
import webbrowser
import uvicorn

# Garante que os caminhos funcionem tanto em dev quanto empacotado no .exe (PyInstaller)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    BUNDLE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = BASE_DIR

sys.path.insert(0, BUNDLE_DIR)

def open_browser():
    time.sleep(1.8)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("=======================================================")
    print("   Curriculium AI - Dev Job Hunter & Resume Tailor")
    print("=======================================================")
    print("Iniciando servidor local em http://127.0.0.1:8000 ...")
    print("Para encerrar, feche esta janela.")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    from app import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
