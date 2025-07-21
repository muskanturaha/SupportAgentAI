import subprocess, threading, webbrowser, time

def launcher(cmd):
    subprocess.run(cmd, shell=True)

webbrowser.open("http://localhost:8501")

threads=[
    threading.Thread(target=launcher,
        args=("uvicorn webhook_server:app --port 8000 --reload",)),
    threading.Thread(target=launcher,
        args=("python fake_support_sender.py",)),
    threading.Thread(target=launcher,
        args=("streamlit run dashboard.py",))
]

for t in threads: t.start()
for t in threads: t.join()
