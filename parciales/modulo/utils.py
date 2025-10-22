import os
import shutil
import time
import subprocess
import json

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def timestamp():
    return time.strftime("%Y%m%d_%H%M%S")

def backup_file(src, backup_dir):
    ensure_dir(backup_dir)
    base = os.path.basename(src)
    dst = os.path.join(backup_dir, f"{timestamp()}_{base}")
    shutil.copy2(src, dst)
    return dst

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def read_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_subprocess(cmd, cwd=None, timeout=60):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd, timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return -1, "", str(e)

def git_commit_all(message, repo_dir="."):
    # tries git; if not available, silently skip (we still have backups)
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_dir, capture_output=True, text=True, timeout=5)
    except Exception:
        return False, "git not available"
    try:
        subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True, text=True, timeout=10)
        proc = subprocess.run(["git", "commit", "-m", message], cwd=repo_dir, capture_output=True, text=True, timeout=10)
        return proc.returncode == 0, proc.stdout + proc.stderr
    except Exception as e:
        return False, str(e)
