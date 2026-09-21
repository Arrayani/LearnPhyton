from tkinter import *
import tkinter as tk

from PIL import Image, ImageTk
#ImageTk,Image

#root = Tk()
root = tk.Tk()

root.title('Menambahkan icon di ujung kiri atas')
#CATATAN, DI LINUX GA BISA NARO GAMBAR ICON, KALO DI WINDOWS BISA, KALO DI LINUX MUNCUL NYA DI BAGIAN BAWAH SEBAGAI 
#ICON PROGRAM YANG SEDANG DI BUKA
icon = tk.PhotoImage(file='/home/roni/Documents/Python/images.png')
bg=ImageTk.PhotoImage(file="photo.jpeg")
root.iconphoto(True,icon)
# root.iconbitmap('/home/roni/Documents/Python/images.ico')
# root.iconbitmap('images.ico')

# button_quit = Button(root, text="Exit Program", command=root.quit)
# button_quit.pack()

# my_img = Image.open('images.ico')

# frame = Frame(root, width=400, height=600, background='white')
# frame.pack_propagate(0)    
# frame.pack()
# my_img = PhotoImage(file='images.png')
#make_label(frame,my_img)


# my_img = Image.open("/home/roni/Documents/Python/images.ico")
# my_label = Label(image=my_img)
# my_label.pack()
root.mainloop()
