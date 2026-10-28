import subprocess


def show_value(user_text):
    return subprocess.run(f"echo {user_text}", shell=True, check=True)
