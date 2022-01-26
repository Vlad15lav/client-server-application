import tkinter as tk
from base.interface import MainForm

def main():
    root = tk.Tk()
    MainForm(root)
    root.mainloop()

if __name__ == '__main__':
    main()