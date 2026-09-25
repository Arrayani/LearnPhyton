import tkinter
import sqlite3
from tkinter import ttk
from tkinter import messagebox

# 1. Hubungkan ke database dan buat tabel
koneksi = sqlite3.connect('NotaTel.db')
#cursor = koneksi.cursor()
drop_table_query = "DROP TABLE IF EXISTS produk"
koneksi.execute(drop_table_query)
