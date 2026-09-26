import tkinter
import sqlite3
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

# Variabel global untuk menyimpan ID baris yang sedang dipilih/diklik
id_terpilih = None

# 1. Hubungkan ke database dan buat tabel
koneksi = sqlite3.connect('NotaTel.db')
cursor = koneksi.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS produk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        merk TEXT NOT NULL,
        namaBrg TEXT,
        varian TEXT,
        unit TEXT,
        hrgmodal INTEGER,
        hrgjual INTEGER,
        stok INTEGER,
        waktu_created TEXT,
        waktu_update TEXT
    )
''')
koneksi.commit() 

# --- FUNGSI FORMAT VISUAL RIBUAN (SUDAH DIPERBAIKI AGAR KURSOR MULUS) ---
def format_ribuan(event):
    widget = event.widget
    teks_asal = widget.get()
    
    # Simpan posisi kursor saat ini
    posisi_kursor = widget.index(tkinter.INSERT)
    
    # Ambil angka saja
    angka_saja = "".join([c for c in teks_asal if c.isdigit()])
    
    if angka_saja:
        nilai_int = int(angka_saja)
        teks_baru = f"{nilai_int:,}".replace(",", ".")
        
        # Hitung jumlah titik sebelum diformat ulang pada teks bagian kiri kursor
        titik_sebelum = teks_asal[:posisi_kursor].count(".")
        
        widget.delete(0, tkinter.END)
        widget.insert(0, teks_baru)
        
        # Hitung jumlah titik setelah diformat ulang pada teks bagian kiri kursor
        titik_sesudah = teks_baru[:posisi_kursor].count(".")
        selisih_titik = titik_sesudah - titik_sebelum
        
        # Kembalikan kursor ke posisi yang tepat
        widget.icursor(posisi_kursor + selisih_titik)
    else:
        widget.delete(0, tkinter.END)

# --- FUNGSI TAMPIL / TAMPILKAN ULANG DATA PADA TREEVIEW ---
def perbarui_tabel():
    for baris in tabel.get_children():
        tabel.delete(baris)
    
    cursor.execute("SELECT * FROM produk")
    data_produk = cursor.fetchall()
    
    for produk in data_produk:
        id_brg, merk, nama, varian, unit, modal, jual, stok, waktu_created, waktu_update = produk
        modal_format = f"{modal:,}".replace(",", ".")
        jual_format = f"{jual:,}".replace(",", ".")
        stok_format = f"{stok:,}".replace(",", ".")

        tabel.insert("", tkinter.END, values=(id_brg, merk, nama, varian, unit, modal_format, jual_format, stok_format, waktu_created, waktu_update))

# --- FUNGSI KLIK BARIS TABEL ---
def pilih_baris(event):
    global id_terpilih
    clear_form()
    
    item_terpilih = tabel.focus()
    if not item_terpilih:
        return
        
    data = tabel.item(item_terpilih, 'values')
    
    # Simpan ID unik barang ke variabel global
    id_terpilih = data[0]
    
    # Masukkan data dari tabel visual kembali ke kolom Entry form atas
    merk_entry.insert(0, data[1])
    namaBrg_entry.insert(0, data[2])
    varian_entry.insert(0, data[3])
    unit_combobox.set(data[4])
    hrgmodal_entry.insert(0, data[5])
    hrgjual_entry.insert(0, data[6])
    stok_entry.insert(0, data[7])

# --- FUNGSI UTAMA & PEMBERSIHAN DATA SQL ---
def enter_data():        
    merk = merk_entry.get().strip()
    nama_barang = namaBrg_entry.get().strip()
    varian = varian_entry.get().strip()
    unit = unit_combobox.get()

    modal_raw = hrgmodal_entry.get().replace(".", "")
    jual_raw = hrgjual_entry.get().replace(".", "")
    stok_raw = stok_entry.get().replace(".", "")
    waktu_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    waktu_update = waktu_created  
    
    if not merk or not nama_barang or not varian or not unit or not modal_raw or not jual_raw or not stok_raw:
        messagebox.showwarning("Peringatan", "Semua kolom input wajib diisi! Tidak boleh ada yang kosong.")
        return 

    try:
        hrg_modal = int(modal_raw)
        hrg_jual = int(jual_raw)
        stok = int(stok_raw)
        
        if hrg_jual < hrg_modal:
            messagebox.showerror("Kesalahan Harga", "Harga Jual tidak boleh kurang dari Harga Modal!")
            return

        data_baru = (merk, nama_barang, varian, unit, hrg_modal, hrg_jual, stok, waktu_created, waktu_update)
        cursor.execute('''
            INSERT INTO produk (merk, namaBrg, varian, unit, hrgmodal, hrgjual, stok, waktu_created, waktu_update)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data_baru)
        
        koneksi.commit()
        messagebox.showinfo("Sukses", "Data berhasil disimpan!")
        
        clear_form()
        perbarui_tabel()
            
    except ValueError:
        messagebox.showerror("Error", "Gagal memproses data numerik!")

# --- FUNGSI HAPUS: BERDASARKAN ID DI TREEVIEW ---
def delete_data():
    global id_terpilih
    
    if id_terpilih:
        tanya = messagebox.askyesno("Konfirmasi Hapus", "Apakah Anda yakin ingin menghapus data produk terpilih?")
        if tanya:
            cursor.execute("DELETE FROM produk WHERE id = ?", (id_terpilih,))
            koneksi.commit()
            messagebox.showinfo("Sukses", "Data produk berhasil dihapus dari database!")
            
            clear_form()
            perbarui_tabel()
    else:
        messagebox.showwarning("Peringatan", "Silakan klik/pilih salah satu baris pada tabel terlebih dahulu untuk menghapus!")

def clear_form():
    global id_terpilih
    id_terpilih = None 
    merk_entry.delete(0, tkinter.END)
    namaBrg_entry.delete(0, tkinter.END)
    varian_entry.delete(0, tkinter.END)
    unit_combobox.set('')
    hrgmodal_entry.delete(0, tkinter.END)
    hrgjual_entry.delete(0, tkinter.END)
    stok_entry.delete(0, tkinter.END)

# --- INTERFACE TKINTER ---
window = tkinter.Tk()
window.title("Data Entry Form & View - NotaTel")
window.geometry("900x650") # Sedikit diperlebar agar muat semua kolom

frame = tkinter.Frame(window)
frame.pack(pady=10)

user_info_frame = tkinter.LabelFrame(frame, text="Informasi Barang")
user_info_frame.grid(row=0, column=0, padx=20, pady=10)

labels = ["Merk", "Nama Barang", "Varian", "Unit", "Harga Modal (Rp)", "Harga Jual (Rp)", "Stok"]
for i, teks in enumerate(labels):
    tkinter.Label(user_info_frame, text=teks).grid(row=i, column=0, sticky="w", padx=5, pady=2)

merk_entry = tkinter.Entry(user_info_frame, width=30)
namaBrg_entry = tkinter.Entry(user_info_frame, width=30)
varian_entry = tkinter.Entry(user_info_frame, width=30)
unit_combobox = ttk.Combobox(user_info_frame, values=["Pcs", "Box", "Pack", "Unit"], state="readonly", width=28)
hrgmodal_entry = tkinter.Entry(user_info_frame, width=30)
hrgjual_entry = tkinter.Entry(user_info_frame, width=30)
stok_entry = tkinter.Entry(user_info_frame, width=30)

entries = [merk_entry, namaBrg_entry, varian_entry, unit_combobox, hrgmodal_entry, hrgjual_entry, stok_entry]
for i, entry in enumerate(entries):
    entry.grid(row=i, column=1, padx=5, pady=2)

hrgmodal_entry.bind("<KeyRelease>", format_ribuan)
hrgjual_entry.bind("<KeyRelease>", format_ribuan)
stok_entry.bind("<KeyRelease>", format_ribuan)

btn_frame = tkinter.Frame(frame)
btn_frame.grid(row=1, column=0, pady=10)

btn_enter = tkinter.Button(btn_frame, text="Enter data", command=enter_data, bg="#2ecc71", fg="white", width=15)
btn_enter.grid(row=0, column=0, padx=5)

btn_delete = tkinter.Button(btn_frame, text="Delete Selected Data", command=delete_data, bg="#e74c3c", fg="white", width=20)
btn_delete.grid(row=0, column=1, padx=5)

tabel_frame = tkinter.LabelFrame(frame, text="Daftar Stok Produk")
tabel_frame.grid(row=2, column=0, padx=10, pady=10)

kolom = ("id", "merk", "nama", "varian", "unit", "modal", "jual", "stok", "waktu_created", "waktu_update")
tabel = ttk.Treeview(tabel_frame, columns=kolom, show="headings", height=10)

tabel.heading("id", text="ID")
tabel.heading("merk", text="Merk")
tabel.heading("nama", text="Nama Barang")
tabel.heading("varian", text="Varian")
tabel.heading("unit", text="Unit")
tabel.heading("modal", text="Harga Modal")
tabel.heading("jual", text="Harga Jual")
tabel.heading("stok", text="Stok")
# DI PERBAIKI DISINI (Sebelumnya "created" & "update" tidak sinkron dengan variabel `kolom`)
tabel.heading("waktu_created", text="Dibuat")
tabel.heading("waktu_update", text="Diupdate")

tabel.column("id", width=40, anchor="center")
tabel.column("merk", width=100)
tabel.column("nama", width=150)
tabel.column("varian", width=80)
tabel.column("unit", width=60, anchor="center")
tabel.column("modal", width=90, anchor="e")
tabel.column("jual", width=90, anchor="e")
tabel.column("stok", width=60, anchor="center")
tabel.column("waktu_created", width=120)
tabel.column("waktu_update", width=120)

tabel.grid(row=0, column=0, sticky="nsew")

# Daftarkan fungsi klik baris agar bisa mengambil data ID
tabel.bind("<ButtonRelease-1>", pilih_baris)

# Tampilkan data database langsung saat aplikasi pertama kali dibuka
perbarui_tabel()

window.mainloop()
koneksi.close()
