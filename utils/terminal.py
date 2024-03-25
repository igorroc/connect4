import colorama
import sys
import subprocess

CHAR_BAR = '█'
CHAR_PROGRESS = '-'
BAR_LEN = 100


def progress_bar(progress, total, color=colorama.Fore.YELLOW):
    percent = BAR_LEN * progress / total
    bar = CHAR_BAR * int(percent) + CHAR_PROGRESS * (BAR_LEN - int(percent))
    if progress == total:
        color = colorama.Fore.GREEN
    print(color + f"\r|{bar}| {percent:.2f}%", end="\r")


def clear_terminal_color():
    print(colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL)


def delay_loading(delay):
    import time
    newDelay = delay+1
    progress_bar(0, delay)
    for i in range(newDelay):
        progress_bar(i, delay)
        time.sleep(0.1)
    clear_terminal_color()


def server_loading():
    print('Iniciando servidor...')
    delay_loading(5)
    print('Criando socket...')
    delay_loading(7)


def clear_screen():
    operatingSystem = sys.platform
    if operatingSystem == 'win32':
        subprocess.run('cls', shell=True)
    else:
        subprocess.run('clear', shell=True)
