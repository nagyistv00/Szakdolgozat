import subprocess
import sys


def show_value(user_text):
    return subprocess.run([sys.executable, "-c", "import sys; print(sys.argv[1])", user_text], shell=False, check=True)
