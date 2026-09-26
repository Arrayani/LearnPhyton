import tkinter
import sqlite3
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

# ============================================================
# VARIABEL GLOBAL
# ============================================================
id_terpilih = None
timer_id = None  # Untuk debounce format ribuan

# ============================================================
# 1. KONEKSI DATABASE (DENGAN TRY-EXCEPT)
# ============================================================
try:
    koneksi = sqlite3.connect('NotaTel.db')
    cursor = koneksi.cursor()
except sqlite3.Error as e:
    messagebox.showerror("Database Error", f"Gagal membuka database: {e}")
    exit()

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

# ============================================================
# 2. FUNGSI FORMAT RIBUAN (OPTIMASI + SKIP JIKA SAMA)
# ============================================================
def format_ribuan(widget):
    teks_asal = widget.get()
    posisi_kursor = widget.index(tkinter.INSERT)
    angka_saja = "".join([c for c in teks_asal if c.isdigit()])

    if not angka_saja:
        if teks_asal:
            widget.delete(0, tkinter.END)
        return

    nilai_int = int(angka_saja)
    teks_baru = f"{nilai_int:,}".replace(",", ".")

    # ⚡ Skip jika teks sudah sama (hemat proses)
    if teks_baru == teks_asal:
        return

    titik_sebelum = teks_asal[:posisi_kursor].count(".")
    titik_sesudah = teks_baru[:posisi_kursor].count(".")
    selisih_titik = titik_sesudah - titik_sebelum

    widget.delete(0, tkinter.END)
    widget.insert(0, teks_baru)
    widget.icursor(posisi_kursor + selisih_titik)

# ============================================================
# 3. FUNGSI DEBOUNCE UNTUK KEYRELEASE
# ============================================================
def on_key_release(event):
    global timer_id
    widget = event.widget
    if timer_id is not None:
        widget.after_cancel(timer_id)
    # Tunda 30ms sebelum memformat (mengatasi delay saat mengetik cepat)
    timer_id = widget.after(30, lambda: format_ribuan(widget))

# ============================================================
# 4. FUNGSI TAMPIL / PERBARUI TABEL
# ============================================================
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

        tabel.insert("", tkinter.END, values=(
            id_brg, merk, nama, varian, unit,
            modal_format, jual_format, stok_format,
            waktu_created, waktu_update
        ))

# ============================================================
# 5. FUNGSI KLIK BARIS TABEL (DIPERBAIKI)
# ============================================================
def pilih_baris(event):
    global id_terpilih

    item_terpilih = tabel.focus()
    if not item_terpilih:
        return  # Keluar dulu jika tidak ada item terpilih

    # Baru clear form setelah validasi lolos
    clear_form()

    data = tabel.item(item_terpilih, 'values')
    id_terpilih = data[0]

    merk_entry.insert(0, data[1])
    namaBrg_entry.insert(0, data[2])
    varian_entry.insert(0, data[3])
    unit_combobox.set(data[4])
    hrgmodal_entry.insert(0, data[5])
    hrgjual_entry.insert(0, data[6])
    stok_entry.insert(0, data[7])

# ============================================================
# 6. FUNGSI SIMPAN DATA (INSERT)
# ============================================================
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

# ============================================================
# 7. FUNGSI HAPUS DATA
# ============================================================
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

# ============================================================
# 8. FUNGSI CLEAR FORM
# ============================================================
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

# ============================================================
# 9. INTERFACE TKINTER
# ============================================================
window = tkinter.Tk()
window.title("Data Entry Form & View - NotaTel")
window.geometry("900x650")

frame = tkinter.Frame(window)
frame.pack(pady=10)

# --- Form Input ---
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

# ⚡ Gunakan debounce untuk KeyRelease
hrgmodal_entry.bind("<KeyRelease>", on_key_release)
hrgjual_entry.bind("<KeyRelease>", on_key_release)
stok_entry.bind("<KeyRelease>", on_key_release)

# --- Tombol ---
btn_frame = tkinter.Frame(frame)
btn_frame.grid(row=1, column=0, pady=10)

btn_enter = tkinter.Button(btn_frame, text="Enter data", command=enter_data, bg="#2ecc71", fg="white", width=15)
btn_enter.grid(row=0, column=0, padx=5)

btn_delete = tkinter.Button(btn_frame, text="Delete Selected Data", command=delete_data, bg="#e74c3c", fg="white", width=20)
btn_delete.grid(row=0, column=1, padx=5)

# --- Tabel Treeview ---
tabel_frame = tkinter.LabelFrame(frame, text="Daftar Stok Produk")
tabel_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

# Agar tabel responsif terhadap resize
tabel_frame.grid_rowconfigure(0, weight=1)
tabel_frame.grid_columnconfigure(0, weight=1)

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

scrollbar = ttk.Scrollbar(tabel_frame, orient="vertical", command=tabel.yview)
tabel.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky="ns")

tabel.bind("<ButtonRelease-1>", pilih_baris)

# Tampilkan data saat pertama kali dibuka
perbarui_tabel()

window.mainloop()
koneksi.close()
