from tkinter import *
import tkinter as tk
from PIL import Image, ImageTk
root = tk.Tk()

from PIL import Image
# im = Image.open("images.ico")
# im = Image.open('images.png')

root.geometry("400x400")
root.image_names
# bg=PhotoImage(file='images.png')
bg=ImageTk.PhotoImage(file="photo.jpeg")
# Show image using label
label1 = Label( root, image = bg)
label1.place(x = 0, y = 0)

label2 = Label( root, text = "Welcome")
label2.pack(pady = 50)

# Create Frame
frame1 = Frame(root,bg = "#88cffa")
frame1.pack(pady = 20 )

# Add buttons
button1 = Button(frame1,text="Exit")
button1.pack(pady=20)

button2 = Button( frame1, text = "Start")
button2.pack(pady = 20)

button3 = Button( frame1, text = "Reset")
button3.pack(pady = 20)

# im.show()

# print(im.format, im.size, im.mode)
root.mainloop()