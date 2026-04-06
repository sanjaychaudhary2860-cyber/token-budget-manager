import os
import sys
from smart_upgrader.logger import log

# 8GB RAM ke liye limits
MAX_RAM_PERCENT = 75
MAX_CPU_PERCENT = 80

def get_ram_usage() -> dict:
    try:
        import psutil
        mem = psutil.virtual_memory()
        return {
            "total_gb":     round(mem.total / (1024**3), 1),
            "used_gb":      round(mem.used  / (1024**3), 1),
            "free_gb":      round(mem.available / (1024**3), 1),
            "percent_used": mem.percent
        }
    except ImportError:
        return {
            "total_gb": 8.0,
            "used_gb":  4.0,
            "free_gb":  4.0,
            "percent_used": 50
        }

def get_cpu_usage() -> float:
    try:
        import psutil
        return psutil.cpu_percent(interval=1)
    except ImportError:
        return 30.0

def is_safe_to_run() -> tuple:
    ram = get_ram_usage()
    cpu = get_cpu_usage()

    if ram["percent_used"] > MAX_RAM_PERCENT:
        return False, f"RAM bahut zyada use ho rahi hai: {ram['percent_used']}%"
    if cpu > MAX_CPU_PERCENT:
        return False, f"CPU bahut busy hai: {cpu}%"
    return True, "System ready hai"

def show_resources():
    ram = get_ram_usage()
    cpu = get_cpu_usage()
    print(f"\n💻 System Resources:")
    print(f"   RAM: {ram['used_gb']}GB / {ram['total_gb']}GB ({ram['percent_used']}%)")
    print(f"   CPU: {cpu}%")
    print(f"   Free: {ram['free_gb']}GB")

def install_psutil():
    try:
        import psutil
        return True
    except ImportError:
        log("psutil install kar raha hun...", "INFO")
        os.system(f"{sys.executable} -m pip install psutil -q")
        return True