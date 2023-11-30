chatting group using tkinter Python
### chatting group dengan Python dengan Tkinter GUI di sisi klien.

## Mulai

### Persyaratan
Python 3.4 atau lebih tinggi

Modul:
```
Socket
tkinter
threading
Select
Time
queue
PIL
Customtkinter
```
## Penggunaan

### Meluncurkan
Untuk menggunakan secara lokal, Anda perlu menjalankan file server terlebih dahulu, misalnya `python server_multithreaded.py`, lalu Anda dapat menjalankan `client.py` di terminal terpisah.
Ada 3 versi server:
     * `server_multi.py` - thread utama hanya mendengarkan koneksi baru, lalu membuat thread baru untuk setiap klien baru
     * `server_multithreaded.py` - memiliki 3 thread - pendengar, penerima, dan pengirim
     * `server_select.py` - memiliki 1 thread yang menggunakan select.select()


### Keluar
Untuk keluar dari klien, cukup klik tombol 'Keluar' atau 'x' di pojok kanan atas.
Untuk keluar dari server:
     * `server_multithreaded.py` dan `server_multi.py` - ketik 'quit' di terminal, lalu tekan Enter
     * `server_select.py` - Anda perlu menggunakan Ctrl+C di terminal (SIGINT)
     

### Protokol perpesanan

Server ini menggunakan protokol komunikasi sederhana, yaitu sebagai berikut:

* templat: `tipe_tindakan;asal;target;isi_pesan`
* pengguna1 mengirim pesan ke pengguna2: `pesan;pengguna1;pengguna2;message_contents`
* pengguna mengirim pesan ke semua pengguna: `pesan;pengguna;SEMUA;isi_pesan`
* pengguna masuk atau keluar: `login;pengguna` / `keluar;pengguna`
* server memberi tahu pengguna tentang perubahan dalam daftar login `login;pengguna1;pengguna2;pengguna3;[...];SEMUA`

