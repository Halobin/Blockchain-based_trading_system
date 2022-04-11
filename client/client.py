from tkinter import *
from LoginPage import *
from PIL import ImageTk, Image

root = Tk()
root.title('基于区块链的交易系统')
image = Image.open("fengmian.jpg")
im = ImageTk.PhotoImage(image)
LoginPage(root,im)
root.mainloop()
