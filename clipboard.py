import pyperclip
import time


def clipboard_loop(file):
    with open(file, "r") as file:
        lines = file.readlines()
    for i in range(3, 0,-1):
        print(i)
        time.sleep(1)

    for line in lines:
        if line.strip():
            pyperclip.copy(line.strip())
            print(f"\"{line.strip()}\" copied to clipboard.")
            time.sleep(2.5)

if __name__ == '__main__':
    clipboard_loop('excel.txt')