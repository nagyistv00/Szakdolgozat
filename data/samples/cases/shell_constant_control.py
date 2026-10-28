import subprocess


def fixed_value():
    return subprocess.run("echo fixed", shell=True, check=True)
