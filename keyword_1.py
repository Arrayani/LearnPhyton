import tkinter as tk

def buka_jendela_input():
    jendela_anak = tk.Toplevel(root)
    jendela_anak.title("Jendela Input")
    jendela_anak.geometry("300x150")
    
    # Membuat modal window agar fokus
    jendela_anak.focus_set()
    jendela_anak.grab_set()
    
    label_petunjuk = tk.Label(jendela_anak, text="Masukkan nama Anda:")
    label_petunjuk.pack(pady=10)
    
    # Kolom input (Entry) di jendela anak
    input_teks = tk.Entry(jendela_anak, width=25)
    input_teks.pack(pady=5)
    input_teks.focus()  # Langsung arahkan kursor ketik ke sini
    
    # Fungsi yang dipicu saat tombol Kirim diklik
    def kirim_data():
        # Mengambil teks dari Entry dan menyimpannya ke StringVar milik jendela utama
        data_dari_anak.set(input_teks.get())
        # Menutup jendela anak
        jendela_anak.destroy()
        
    tombol_kirim = tk.Button(jendela_anak, text="Kirim ke Utama", command=kirim_data)
    tombol_kirim.pack(pady=10)

# --- JENDELA UTAMA ---
root = tk.Tk()
root.title("Jendela Utama")
root.geometry("400x250")

# 1. Membuat StringVar sebagai wadah penampung data antar jendela
data_dari_anak = tk.StringVar()
data_dari_anak.set("Belum ada data") # Nilai awal

# 2. Label untuk menampilkan data yang diterima
label_utama = tk.Label(root, text="Data Diterima:", font=("Arial", 12))
label_utama.pack(pady=20)

# Label ini otomatis berubah mengikuti isi dari data_dari_anak (menggunakan textvariable)
label_hasil = tk.Label(root, textvariable=data_dari_anak, font=("Arial", 14, "bold"), fg="blue")
label_hasil.pack(pady=5)

# Tombol untuk membuka jendela input
tombol_buka = tk.Button(root, text="Buka Jendela Input", command=buka_jendela_input)
tombol_buka.pack(pady=20)

root.mainloop()
