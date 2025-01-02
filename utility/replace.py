import pyperclip
import keyboard
import time

def format_for_paste():
    try:
        clipboard_content = pyperclip.paste()
        clipboard_content=clipboard_content.replace('\r\n','\n')
        modified_content = clipboard_content.replace('"',"'").replace('\n', '')#'\\n')
        pyperclip.copy(modified_content)
        print("Clipboard content modified and updated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


while True:
    keyboard.wait('ctrl+shift+1')

    format_for_paste()

    time.sleep(10)