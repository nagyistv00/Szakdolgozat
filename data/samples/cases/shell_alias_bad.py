from subprocess import run as launch


def show_value(user_text):
    command = "echo " + user_text
    return launch(command, shell=True, check=True)
