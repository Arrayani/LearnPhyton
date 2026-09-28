import tkinter
import sqlite3
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

# ============================================================
# VARIABEL GLOBAL
# ============================================================
timer_id = None       # Untuk debounce format ribuan
id_terakhir = None    # ID data yang sedang ditampilkan di preview
mode_edit = False     # True jika sedang dalam mode edit

# ============================================================
# 1. KONEKSI DATABASE
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
# 2. FUNGSI FORMAT RIBUAN
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

    if teks_baru == teks_asal:
        return

    titik_sebelum = teks_asal[:posisi_kursor].count(".")
    titik_sesudah = teks_baru[:posisi_kursor].count(".")
    selisih_titik = titik_sesudah - titik_sebelum

    widget.delete(0, tkinter.END)
    widget.insert(0, teks_baru)
    widget.icursor(posisi_kursor + selisih_titik)

def on_key_release(event):
    global timer_id
    widget = event.widget
    if timer_id is not None:
        widget.after_cancel(timer_id)
    timer_id = widget.after(30, lambda: format_ribuan(widget))

# ============================================================
# 3. FUNGSI TAMPILKAN PREVIEW
# ============================================================
def tampilkan_preview(id_data):
    cursor.execute("SELECT * FROM produk WHERE id = ?", (id_data,))
    data = cursor.fetchone()

    if data:
        id_brg, merk, nama, varian, unit, modal, jual, stok, created, updated = data
        modal_fmt = f"{modal:,}".replace(",", ".")
        jual_fmt = f"{jual:,}".replace(",", ".")
        stok_fmt = f"{stok:,}".replace(",", ".")

        teks_preview = (
            f"ID: {id_brg}  |  {merk} - {nama} ({varian})\n"
            f"Unit: {unit}  |  Modal: Rp {modal_fmt}  |  Jual: Rp {jual_fmt}  |  Stok: {stok_fmt}\n"
            f"Dibuat: {created}  |  Diupdate: {updated}"
        )
        label_preview.config(text=teks_preview, fg="black")
    else:
        label_preview.config(text="(Data tidak ditemukan)", fg="gray")

# ============================================================
# 4. FUNGSI SIMPAN DATA (INSERT / UPDATE)
# ============================================================
def enter_data():
    global id_terakhir, mode_edit

    merk = merk_entry.get().strip()
    nama_barang = namaBrg_entry.get().strip()
    varian = varian_entry.get().strip()
    unit = unit_combobox.get()

    modal_raw = hrgmodal_entry.get().replace(".", "")
    jual_raw = hrgjual_entry.get().replace(".", "")
    stok_raw = stok_entry.get().replace(".", "")

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

        if mode_edit and id_terakhir:
            waktu_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE produk
                SET merk=?, namaBrg=?, varian=?, unit=?, hrgmodal=?, hrgjual=?, stok=?, waktu_update=?
                WHERE id=?
            ''', (merk, nama_barang, varian, unit, hrg_modal, hrg_jual, stok, waktu_update, id_terakhir))
            koneksi.commit()
            messagebox.showinfo("Sukses", "Data berhasil diperbarui!")
            mode_edit = False
            btn_enter.config(text="Enter data")
        else:
            waktu_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            waktu_update = waktu_created
            cursor.execute('''
                INSERT INTO produk (merk, namaBrg, varian, unit, hrgmodal, hrgjual, stok, waktu_created, waktu_update)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (merk, nama_barang, varian, unit, hrg_modal, hrg_jual, stok, waktu_created, waktu_update))
            koneksi.commit()
            id_terakhir = cursor.lastrowid
            messagebox.showinfo("Sukses", "Data berhasil disimpan!")

        tampilkan_preview(id_terakhir)
        clear_form()

    except ValueError:
        messagebox.showerror("Error", "Gagal memproses data numerik!")

# ============================================================
# 5. FUNGSI HAPUS DATA
# ============================================================
def delete_data():
    global id_terakhir

    if not id_terakhir:
        messagebox.showwarning("Peringatan", "Tidak ada data yang bisa dihapus. Silakan input data terlebih dahulu.")
        return

    tanya = messagebox.askyesno("Konfirmasi Hapus", "Apakah Anda yakin ingin menghapus data yang sedang ditampilkan?")
    if tanya:
        cursor.execute("DELETE FROM produk WHERE id = ?", (id_terakhir,))
        koneksi.commit()
        messagebox.showinfo("Sukses", "Data berhasil dihapus!")
        id_terakhir = None
        label_preview.config(text="(Belum ada data yang ditampilkan)", fg="gray")
        clear_form()

# ============================================================
# 6. FUNGSI EDIT DATA
# ============================================================
def edit_data():
    global id_terakhir, mode_edit

    if not id_terakhir:
        messagebox.showwarning("Peringatan", "Tidak ada data yang bisa diedit. Silakan input data terlebih dahulu.")
        return

    cursor.execute("SELECT * FROM produk WHERE id = ?", (id_terakhir,))
    data = cursor.fetchone()

    if not data:
        messagebox.showerror("Error", "Data tidak ditemukan di database!")
        return

    id_brg, merk, nama, varian, unit, modal, jual, stok, created, updated = data

    clear_form()
    merk_entry.insert(0, merk)
    namaBrg_entry.insert(0, nama)
    varian_entry.insert(0, varian)
    unit_combobox.set(unit)
    hrgmodal_entry.insert(0, f"{modal:,}".replace(",", "."))
    hrgjual_entry.insert(0, f"{jual:,}".replace(",", "."))
    stok_entry.insert(0, f"{stok:,}".replace(",", "."))

    mode_edit = True
    btn_enter.config(text="Update data")
    messagebox.showinfo("Mode Edit", "Silakan ubah data di form, lalu klik 'Update data'.")

# ============================================================
# 7. FUNGSI CLEAR FORM
# ============================================================
def clear_form():
    merk_entry.delete(0, tkinter.END)
    namaBrg_entry.delete(0, tkinter.END)
    varian_entry.delete(0, tkinter.END)
    unit_combobox.set('')
    hrgmodal_entry.delete(0, tkinter.END)
    hrgjual_entry.delete(0, tkinter.END)
    stok_entry.delete(0, tkinter.END)

# ============================================================
# 8. FUNGSI WINDOW "LIHAT SEMUA DATA"
# ============================================================
def buka_window_semua_data():
    """Membuka window Toplevel berisi tabel semua produk."""

    win = tkinter.Toplevel(window)
    win.title("Daftar Semua Produk - NotaTel")
    win.geometry("1000x500")
    win.transient(window)  # Selalu di atas window utama
    win.grab_set()         # Fokus ke window ini

    # --- Frame Tabel ---
    tabel_frame = tkinter.LabelFrame(win, text="Daftar Semua Produk")
    tabel_frame.pack(padx=10, pady=10, fill="both", expand=True)

    tabel_frame.grid_rowconfigure(0, weight=1)
    tabel_frame.grid_columnconfigure(0, weight=1)

    kolom = ("id", "merk", "nama", "varian", "unit", "modal", "jual", "stok", "waktu_created", "waktu_update")
    tabel_semua = ttk.Treeview(tabel_frame, columns=kolom, show="headings", height=15)

    # Heading
    tabel_semua.heading("id", text="ID")
    tabel_semua.heading("merk", text="Merk")
    tabel_semua.heading("nama", text="Nama Barang")
    tabel_semua.heading("varian", text="Varian")
    tabel_semua.heading("unit", text="Unit")
    tabel_semua.heading("modal", text="Harga Modal")
    tabel_semua.heading("jual", text="Harga Jual")
    tabel_semua.heading("stok", text="Stok")
    tabel_semua.heading("waktu_created", text="Dibuat")
    tabel_semua.heading("waktu_update", text="Diupdate")

    # Kolom
    tabel_semua.column("id", width=40, anchor="center")
    tabel_semua.column("merk", width=100)
    tabel_semua.column("nama", width=150)
    tabel_semua.column("varian", width=80)
    tabel_semua.column("unit", width=60, anchor="center")
    tabel_semua.column("modal", width=90, anchor="e")
    tabel_semua.column("jual", width=90, anchor="e")
    tabel_semua.column("stok", width=60, anchor="center")
    tabel_semua.column("waktu_created", width=120)
    tabel_semua.column("waktu_update", width=120)

    tabel_semua.grid(row=0, column=0, sticky="nsew")

    # Scrollbar
    scrollbar = ttk.Scrollbar(tabel_frame, orient="vertical", command=tabel_semua.yview)
    tabel_semua.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky="ns")

    # --- Fungsi Load Data ---
    def muat_data():
        for baris in tabel_semua.get_children():
            tabel_semua.delete(baris)

        cursor.execute("SELECT * FROM produk ORDER BY id DESC")
        data_produk = cursor.fetchall()

        for produk in data_produk:
            id_brg, merk, nama, varian, unit, modal, jual, stok, created, updated = produk
            modal_fmt = f"{modal:,}".replace(",", ".")
            jual_fmt = f"{jual:,}".replace(",", ".")
            stok_fmt = f"{stok:,}".replace(",", ".")

            tabel_semua.insert("", tkinter.END, values=(
                id_brg, merk, nama, varian, unit,
                modal_fmt, jual_fmt, stok_fmt,
                created, updated
            ))

    # --- Fungsi Klik Baris → Muat ke Form Utama ---
    def pilih_dari_semua(event):
        global id_terakhir

        item = tabel_semua.focus()
        if not item:
            return

        data = tabel_semua.item(item, 'values')
        id_terakhir = data[0]

        # Tampilkan preview di window utama
        tampilkan_preview(id_terakhir)

        # Tutup window dan beri tahu pengguna
        win.destroy()
        messagebox.showinfo("Data Dipilih", f"Data ID {id_terakhir} dimuat ke preview.")

    tabel_semua.bind("<Double-Button-1>", pilih_dari_semua)  # Double-click

    # --- Tombol ---
    btn_frame = tkinter.Frame(win)
    btn_frame.pack(pady=5)

    btn_refresh = tkinter.Button(btn_frame, text="Refresh", command=muat_data, bg="#3498db", fg="white", width=12)
    btn_refresh.grid(row=0, column=0, padx=5)

    btn_tutup = tkinter.Button(btn_frame, text="Tutup", command=win.destroy, bg="#95a5a6", fg="white", width=12)
    btn_tutup.grid(row=0, column=1, padx=5)

    # Muat data pertama kali
    muat_data()

# ============================================================
# 9. INTERFACE TKINTER (WINDOW UTAMA)
# ============================================================
window = tkinter.Tk()
window.title("Data Entry Form - NotaTel")
window.geometry("500x650")

frame = tkinter.Frame(window)
frame.pack(pady=15)

# --- Form Input ---
user_info_frame = tkinter.LabelFrame(frame, text="Informasi Barang")
user_info_frame.grid(row=0, column=0, padx=20, pady=5)

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

hrgmodal_entry.bind("<KeyRelease>", on_key_release)
hrgjual_entry.bind("<KeyRelease>", on_key_release)
stok_entry.bind("<KeyRelease>", on_key_release)

# --- Tombol Aksi ---
btn_frame = tkinter.Frame(frame)
btn_frame.grid(row=1, column=0, pady=10)

btn_enter = tkinter.Button(btn_frame, text="Enter data", command=enter_data, bg="#2ecc71", fg="white", width=12)
btn_enter.grid(row=0, column=0, padx=3)

btn_edit = tkinter.Button(btn_frame, text="Edit", command=edit_data, bg="#f39c12", fg="white", width=10)
btn_edit.grid(row=0, column=1, padx=3)

btn_delete = tkinter.Button(btn_frame, text="Hapus", command=delete_data, bg="#e74c3c", fg="white", width=10)
btn_delete.grid(row=0, column=2, padx=3)

# --- Tombol Lihat Semua Data ---
btn_lihat_semua = tkinter.Button(
    frame,
    text="📋 Lihat Semua Data",
    command=buka_window_semua_data,
    bg="#3498db",
    fg="white",
    width=30
)
btn_lihat_semua.grid(row=2, column=0, pady=5)

# --- Preview Data ---
preview_frame = tkinter.LabelFrame(frame, text="Data Terakhir Diinput")
preview_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

label_preview = tkinter.Label(
    preview_frame,
    text="(Belum ada data yang ditampilkan)",
    fg="gray",
    justify="left",
    anchor="w",
    wraplength=420
)
label_preview.pack(padx=10, pady=10, fill="x")

window.mainloop()
koneksi.close()
