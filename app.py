"""
app.py
یک فایل واحد برای روشن کردن کل پروژه (هم bot.py و هم helper.py با هم).
مناسب برای اجرای لوکال (python app.py) و همچنین اجرای روی Render
به‌عنوان یک سرویس تکی (Start Command: python app.py) به‌جای دو سرویس جدا.

self.py نیازی به اجرای دستی نداره؛ خودِ bot.py هر وقت لازم باشه
اون رو به‌صورت زیرپردازش (subprocess) اجرا می‌کنه.
"""

import os
import sys
import signal
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# نام فایل‌هایی که باید هم‌زمان اجرا بشن
SERVICES = [
    {"name": "bot", "file": "bot.py"},
    {"name": "helper", "file": "helper.py"},
]

processes = {}
_shutting_down = False


def start_service(service):
    path = os.path.join(BASE_DIR, service["file"])
    print(f"🚀 در حال اجرای {service['name']} ({service['file']}) ...")
    proc = subprocess.Popen(
        [sys.executable, path],
        cwd=BASE_DIR,
    )
    processes[service["name"]] = proc
    return proc


def stop_all():
    global _shutting_down
    _shutting_down = True
    for name, proc in processes.items():
        if proc.poll() is None:
            print(f"🛑 در حال متوقف کردن {name} ...")
            proc.terminate()
    # فرصت بده تا تمیز بسته بشن
    deadline = time.time() + 10
    for name, proc in processes.items():
        remaining = max(0, deadline - time.time())
        try:
            proc.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            print(f"⚠️ {name} بسته نشد، در حال kill اجباری ...")
            proc.kill()


def handle_signal(signum, frame):
    print("\n📴 سیگنال توقف دریافت شد ...")
    stop_all()
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    for service in SERVICES:
        start_service(service)

    print("✅ همه‌ی سرویس‌ها اجرا شدن. برای توقف Ctrl+C بزنید.")

    # حلقه‌ی نظارت: اگر یکی از دو پردازش به‌طور غیرمنتظره بسته شد، دوباره روشنش کن
    while True:
        time.sleep(5)
        if _shutting_down:
            break
        for service in SERVICES:
            name = service["name"]
            proc = processes.get(name)
            if proc is not None and proc.poll() is not None:
                code = proc.returncode
                print(f"⚠️ سرویس {name} با کد {code} متوقف شد. در حال راه‌اندازی مجدد ...")
                time.sleep(2)
                start_service(service)


if __name__ == "__main__":
    main()
