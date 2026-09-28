import tkinter as tk
from tkinter import ttk

class VirtualLazyColumn(tk.Tk):
    def __init__(self, total_items=100000):
        super().__init__()
        self.title("Tkinter Manual Virtualization (LazyColumn)")
        self.geometry("450x500")
        
        # 1. SIAPKAN DATA RAKSASA (Simulasi Database)
        # Membuat 100.000 data dummy dalam bentuk List of Dict
        self.data_source = [
            {
                "id": i,
                "name": f"📦 Produk Premium #{i}",
                "price": f"Rp {150000 + (i * 500):,}",
                "status": "Tersedia" if i % 2 == 0 else "Stok Habis"
            }
            for i in range(total_items)
        ]
        
        # 2. PENGATURAN UKURAN & VIEWPORT
        self.total_data = len(self.data_source)
        self.row_height = 65  # Tinggi setiap baris UI (dalam pixel)
        self.visible_rows = 7  # Jumlah baris yang muat di layar secara vertikal
        self.current_top_index = 0  # Data index yang sedang berada di paling atas
        
        # 3. KONTROL UTAMA & SCROLLBAR
        # Menggunakan Scrollbar tiruan untuk mendeteksi posisi scroll data
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.on_scroll_bar)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Container utama untuk baris-baris UI
        self.list_container = ttk.Frame(self)
        self.list_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 4. INSTANSIASI WIDGET UI (POOL WIDGET)
        # Di sini keajaibannya: Kita HANYA membuat widget sebanyak yang terlihat di layar
        self.ui_pool = []
        for i in range(self.visible_rows):
            row_frame = ttk.Frame(self.list_container, padding=10, relief="groove")
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Sub-widget dalam satu baris (UI Kompleks)
            lbl_name = ttk.Label(row_frame, text="", font=("Arial", 11, "bold"))
            lbl_name.grid(row=0, column=0, sticky="w")
            
            lbl_price = ttk.Label(row_frame, text="", font=("Arial", 9), foreground="green")
            lbl_price.grid(row=1, column=0, sticky="w")
            
            lbl_status = ttk.Label(row_frame, text="", font=("Arial", 8, "italic"))
            lbl_status.grid(row=0, column=1, rowspan=2, padx=20, sticky="e")
            
            btn_action = ttk.Button(row_frame, text="Beli", width=8)
            btn_action.grid(row=0, column=2, rowspan=2, padx=5, sticky="e")
            
            # Mengatur kolom agar fleksibel
            row_frame.columnconfigure(0, weight=1)
            
            # Simpan referensi widget ke dalam POOL untuk di-update nanti
            self.ui_pool.append({
                "frame": row_frame,
                "name": lbl_name,
                "price": lbl_price,
                "status": lbl_status,
                "button": btn_action
            })
            
        # Bind mouse wheel untuk scroll menggunakan mouse
        self.list_container.bind_all("<MouseWheel>", self.on_mouse_wheel)
        
        # Render tampilan awal & inisialisasi posisi scrollbar
        self.update_ui_display()
        self.update_scrollbar_position()

    def update_ui_display(self):
        """Fungsi krusial yang memperbarui ISI widget lama dengan DATA baru"""
        for i in range(self.visible_rows):
            data_index = self.current_top_index + i
            ui = self.ui_pool[i]
            
            # Jika data_index masih dalam jangkauan database
            if data_index < self.total_data:
                item_data = self.data_source[data_index]
                
                # Update isi widget dengan fungsi .configure()
                ui["name"].configure(text=item_data["name"])
                ui["price"].configure(text=item_data["price"])
                ui["status"].configure(text=item_data["status"])
                
                # Contoh kustomisasi logika UI dinamis
                if item_data["status"] == "Stok Habis":
                    ui["status"].configure(foreground="red")
                    ui["button"].configure(state="disabled")
                else:
                    ui["status"].configure(foreground="blue")
                    ui["button"].configure(state="normal")
                
                # Masukkan fungsi klik unik untuk setiap data meskipun tombolnya sama
                ui["button"].configure(command=lambda d=item_data: self.action_click(d))
                
                # Tampilkan frame baris jika sebelumnya sempat disembunyikan
                ui["frame"].pack(fill=tk.X, padx=5, pady=2)
            else:
                # Sembunyikan widget sisa jika jumlah total data kurang dari kapasitas layar
                ui["frame"].pack_forget()

    def update_scrollbar_position(self):
        """Menyesuaikan posisi slider scrollbar secara proporsional"""
        if self.total_data > self.visible_rows:
            first = self.current_top_index / self.total_data
            last = (self.current_top_index + self.visible_rows) / self.total_data
            self.scrollbar.set(first, last)
        else:
            self.scrollbar.set(0, 1)

    def on_scroll_bar(self, action, value, type=None):
        """Menangani pergerakan saat scrollbar ditarik dengan mouse"""
        if action == "moveto":
            # Konversi nilai float scrollbar (0.0 - 1.0) menjadi index data
            target_index = int(float(value) * self.total_data)
            max_index = max(0, self.total_data - self.visible_rows)
            self.current_top_index = min(target_index, max_index)
            
            self.update_ui_display()
            self.update_scrollbar_position()

    def on_mouse_wheel(self, event):
        """Menangani pergerakan saat layar di-scroll menggunakan mouse wheel"""
        # Windows menggunakan event.delta, biasanya bernilai kelipatan 120
        direction = -1 if event.delta > 0 else 1
        
        new_index = self.current_top_index + direction
        max_index = max(0, self.total_data - self.visible_rows)
        
        if 0 <= new_index <= max_index:
            self.current_top_index = new_index
            self.update_ui_display()
            self.update_scrollbar_position()

    def action_click(self, item):
        print(f"Mengklik: {item['name']} dengan harga {item['price']}")

if __name__ == "__main__":
    # Menjalankan aplikasi dengan 100.000 data
    app = VirtualLazyColumn(total_items=100000)
    app.mainloop()
