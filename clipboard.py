import pyperclip
import time


def clipboard_loop(file, start, sleep):
    with open(file, "r") as file:
        lines = file.readlines()

    for i in range(3, 0,-1):
        print(i)
        time.sleep(1)

    go = False if start else True

    for line in lines:
        if start:
            if line.strip() == start:
                go = True

        if line.strip() and go:
            pyperclip.copy(line.strip())
            print(f"\"{line.strip()}\" copied to clipboard.")
            time.sleep(sleep)

def clipboard_debug(file):
    with open(file, "r") as file:
        lines = file.readlines()


    for line in lines:
        if line.strip():
            pyperclip.copy(line.strip())
            print(f"\"{line.strip()}\" copied to clipboard.")
            input()

if __name__ == '__main__':
    clipboard_loop('excel.txt', start="", sleep=1.5)

    # clipboard_debug('excel.txt')