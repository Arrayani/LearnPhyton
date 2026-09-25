import tkinter
import sqlite3
from tkinter import ttk
from tkinter import messagebox
from sqlite3 import Error



# Drop the table if it already exists (to start fresh)
#cursor_obj.execute("DROP TABLE IF EXISTS produk")

# 1. Membuat atau menghubungkan ke database bernama 'toko.db'
koneksi = sqlite3.connect('NotaTel.db')
# 2. Membuat objek cursor untuk mengeksekusi perintah SQL
cursor = koneksi.cursor()

# Drop the table if it already exists (to start fresh)
cursor.execute("DROP TABLE IF EXISTS produk")


# 3. Membuat tabel baru bernama 'produk' jika belum ada
cursor.execute('''
    CREATE TABLE IF NOT EXISTS produk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        merk TEXT NOT NULL,
        namaBrg TEXT,
        varian TEXT,
        unit TEXT,
        hrgmodal INTEGER,
        hrgjual INTEGER,
        stok INTEGER    
    )
''')
print("Tabel berhasil dibuat!")
koneksi.commit()  # Menyimpan perubahan (wajib dilakukan setelah membuat tabel)

def delete_data():
        print("Menghapus Data: ")
        ##Menghapus data dari tabel produk berdasarkan merk
        id_to_delete = "Onemed"
        if id_to_delete:
            # cursor.execute("DELETE FROM produk WHERE merk = ?", (id_to_delete,))
            cursor.execute("DELETE FROM produk") #ini mendelete semua isi table, bukan destroy
        koneksi.commit()
        print(f"Data dengan ID {id_to_delete} berhasil dihapus!")
        # else:
        # print("ID tidak boleh kosong!")
        # 5. Membaca data dari tabel (SELECT)
        cursor.execute("SELECT * FROM produk")
        semua_data = cursor.fetchall()
        for baris in semua_data:
            print(baris)    

def enter_data():        
    with  koneksi:
        # cursor = koneksi.cursor()                                       
        print("Memasukan Data: ")
        data_baru = ("Onemed","Thermometer Digital" ,"Biru","Pcs", 100000, 150000, 10)
        cursor.execute('''
            INSERT INTO produk (merk, namaBrg, varian, unit, hrgmodal, hrgjual, stok)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', data_baru)

    # Menyimpan perubahan (wajib dilakukan setelah melakukan INSERT/UPDATE/DELETE)
        koneksi.commit()
        print("Data berhasil dimasukkan!")         

        # 5. Membaca data dari tabel (SELECT)
        cursor.execute("SELECT * FROM produk")
        semua_data = cursor.fetchall()
        for baris in semua_data:
            print(baris)    
# # 6. Menutup koneksi database setelah selesai digunakan
# koneksi.close()


window = tkinter.Tk()
window.title("Data Entry Form")
window.geometry("500x500")

frame = tkinter.Frame(window)
frame.pack()

# Saving User Info
user_info_frame =tkinter.LabelFrame(frame, text="Informasi Barang",font=('Arial 16 bold'))
user_info_frame.grid(row= 0, column=0, padx=20, pady=20,ipadx=5,ipady=10)

merk_label = tkinter.Label(user_info_frame, text="Merk",font=('Arial 12 '))
merk_label.grid(row=0, column=0,sticky=tkinter.W)
namaBrg_label = tkinter.Label(user_info_frame, text="Nama Barang",font=('Arial 12 '))
namaBrg_label.grid(row=1, column=0,sticky=tkinter.W)
varian_label = tkinter.Label(user_info_frame, text="Varian",font=('Arial 12 '))
varian_label.grid(row=2, column=0,sticky=tkinter.W)
unit_label = tkinter.Label(user_info_frame, text="Unit",font=('Arial 12 '))   
unit_label.grid(row=3, column=0,sticky=tkinter.W)
hrgmodal_label = tkinter.Label(user_info_frame, text="Harga Modal",font=('Arial 12 '))
hrgmodal_label.grid(row=4, column=0,sticky=tkinter.W)
hrgjual_label = tkinter.Label(user_info_frame, text="Harga Jual",font=('Arial 12 '))
hrgjual_label.grid(row=5, column=0,sticky=tkinter.W)     
stok_label = tkinter.Label(user_info_frame, text="Stok",font=('Arial 12 '))
stok_label.grid(row=6, column=0,sticky=tkinter.W)    



merk_entry = tkinter.Entry(user_info_frame)
merk_entry.grid(row=0, column=1)
namaBrg_entry = tkinter.Entry(user_info_frame)
namaBrg_entry.grid(row=1, column=1) 
varian_entry = tkinter.Entry(user_info_frame)
varian_entry.grid(row=2, column=1)
hrgmodal_entry = tkinter.Entry(user_info_frame)
hrgmodal_entry.grid(row=4, column=1)
hrgjual_entry = tkinter.Entry(user_info_frame)
hrgjual_entry.grid(row=5, column=1)
unit_combobox = ttk.Combobox(user_info_frame, values=["", "Mr.", "Ms.", "Dr."])
unit_combobox.grid(row=3, column=1)
stok_entry = tkinter.Entry(user_info_frame)
stok_entry.grid(row=6, column=1)

# # Button
button_Enter = tkinter.Button(frame, text="Enter data", command= enter_data,font=('Arial 12 '))
button_Enter.grid(row=7, column=0, sticky="news", padx=20, pady=10)

# # Button
button_Delete = tkinter.Button(frame, text="Delete data", command= delete_data,font=('Arial 12 '))
button_Delete.grid(row=8, column=0, sticky="news", padx=20, pady=10)
 
window.mainloop()
koneksi.close()  # Menutup koneksi database setelah selesai digunakan
