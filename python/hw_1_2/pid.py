#!/usr/bin/env python3

def get_pid_from_str(text):
    # split the text
    words = text.split()
    return words[1]


if __name__ == "__main__":
    text = "152321 15151 21321 156151 hello"
    print(get_pid_from_str(text))