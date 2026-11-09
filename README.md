Nama : Nefi

NPM : 2506657125

Kelas : PBP C

### Tugas 1
1. Ya, menggunakan. Elemen seperti <section> tetapi di bagian header belum terlalu paham dan notice bagaimana cara menggunakan header, lalu saat klik bagian skills di header masih muncul error
2. Tantangan saya mengerjakan css adalah saya sulit menempatkan tata letak bagian kotak kotaknya agar sesuai dengan keinginan saya
3. Saya hanya bisa mendesign sesuai yang sudah template berikan dan belum terlalu mengulik lebih lanjut bagaimana caranya mendesign diluar template

Saya memakai Claude AI untuk membantu mengatur tata letak design dan membantu saya untuk memberikan pengertian tentang element section

### Tugas 2
1. Saat membuka halaman portofolio, diujung kanan atas ada pilihan navigation bar yang berisi profile, experience, dan certification yang masing masing pilihan bisa di klik untuk mengetahui detail lebih lanjut. Urls.py sendiri punya peran sebagai peta rute untuk menentukan URL yang akan diarahkan ke fungsi. Urls.py ada dua folder yaitu folder proyek dan folder main. Folder proyek adalah pintu masuk utama yang akan ngeforward semua permintaan user ke urls.py di folder aplikasi main. Di main/urls.py, tiap alamat akan dicocokkan dengan nama fungsi yang ada di views.py.
2. Data lebih baik jika disimpan di model karena untuk mempermudah kalau ingin menambah atau mengganti data jadi tidak perlu edit file HTML satu per satu. Ini juga membuat kode lebih rapi karena tugasnya terpisah dan tertulis dengan jelas.
3. Kalau makemigrations membuat file yang mencatat perubahan di model tetapi belum langsung diterapkan ke database, sedangkan migrate adalah langkah selanjutnya untuk menerapkan perubahan sehingga kolom thumbnail beneran ditambahin ke tabel yang diinginkan di database.

### Tugas 3
1. Penggunaan ModelForm memudahkan saya agar tidak perlu menulis setiap field di HTML karena form tersebut sudah otomatis dari model. Isi dalam ModelForm juga sudah dicek secara otomatis dan {% csrf_token %} wajib ada supaya form hanya bisa dikirim dari website sendiri, bukan dari website lain. Jika tokennya tidak ada, Django akan menolak request (error 403).
2.  Format data JSON lebih singkat dan lebih mudah dibaca daripada XML, karena XML harus memakai tag pembuka dan penutup. JSON juga mirip objek di JavaScript, jadi akan memudahkan jika dipakai di browser.
3.  Saat URL dibuka, view akan mengambil data Certification dari database dan mengubahnya menjadi JSON. Serialization diperlukan karena data dari database berbentuk objek Python, sedangkan yang bisa dikirim lewat HTTP berupa teks.

### Tugas 5
1. Debouncing adalah teknik menunda eksekusi fungsi sampai pengguna berhenti melakukan aksi selama jeda tertentu. Teknik ini penting digunakan dalam fitur search karena setiap ketikan me-reset timer, jadi request baru dikirim setelah pengguna berhenti mengetik. Tanpa debouncing, mengetik "python" bisa mengirim 6 request sekaligus. Hal ini membebani server, dan respons yang datang tidak berurutan bisa bikin hasil lama menimpa hasil terbaru. 
2. fetch() tidak langsung memberi data melainkan memberi Promise, yaitu saat datanya datang nanti. Sedangkan await membuat kode menunggu sampai datanya datang lalu lanjut ke baris berikutnya. Jika tidak menggunakan await, kode akan jalan duluan sebelum datanya siap dan akan muncul tulisan error atau undefined.
3. Serangan XSS adalah serangan di mana user menyelipkan kode ke dalam data dan saat data itu ditampilkan ke user lain, kodenya ikut dijalankan ke browser user lain tersebut. Hal ini rentan dipakai untuk mencuri sesi login. Sedangkan dari template dari django sudah otomatis mengamankan teks yang ditampilkan ke browser.

### Tugas 6
1. REST adalah sebuah konsep dalam membuat API agar aplikasi dapat saling berkomunikasi dan bertukar data melalui HTTP. API yang RESTful tidak cukup hanya mengembalikan data dalam format JSON karena API juga harus mengikuti prinsip REST, seperti:
- Menggunakan HTTP method sesuai fungsinya (GET, POST, PUT, PATCH, DELETE).
- Memiliki URL yang mewakili sumber daya.
- Bersifat stateless, artinya setiap request harus membawa informasi yang dibutuhkan tanpa bergantung pada riwayat request sebelumnya.

Perbedaan PUT dan PATCH adalah PUT digunakan untuk mengganti seluruh data, sedangkan PATCH digunakan untuk mengubah sebagian data saja. Contohnya seperti ada data mahasiswa dengan nama, umur, dan alamat. Jika ingin mengganti seluruh data mahasiswa maka akan menggunakan PUT, sedangkan jika hanya ingin mengubah alamat tanpa mengubah nama dan umur menggunakan PATCH.

2. Serializer adalah fitur pada Django REST Framework yang berfungsi untuk mengubah data dari model Django menjadi format yang dapat dikirim melalui API, seperti JSON. 

Keuntungan menggunakan serializer dibandingkan membuat dictionary secara manual dengan JsonResponse adalah lebih praktis dalam mengubah data menjadi JSON, dapat melakukan validasi data secara otomatis, serta dapat mengurangi penulisan kode yang berulang. Jadi, serializer membuat proses pengolahan dan validasi data API menjadi lebih mudah dibandingkan membuat dictionary secara manual.

3. Autentikasi adalah proses untuk memastikan identitas pengguna atau mengetahui siapa yang sedang mengakses API, sedangkan Otorisasi adalah proses menentukan apakah pengguna memiliki izin untuk mengakses atau melakukan tindakan tertentu. Jika hanya mengandalkan tombol hapus disembunyikan, pengguna masih bisa mencoba mengirim request langsung melalui browser atau aplikasi lain. Oleh karena itu, server harus tetap memeriksa izin setiap kali ada request agar data tidak dapat diakses atau diubah oleh orang yang tidak berwenang.

4. Pada Django REST Framework yang menggunakan SessionAuthentication, browser secara otomatis mengirimkan cookie session ketika pengguna mengakses server. Karena itu, token CSRF tetap diperlukan untuk melindungi permintaan yang mengubah data, seperti:
- POST untuk menambahkan data.
- PUT untuk mengganti data.
- PATCH untuk mengubah sebagian data.
- DELETE untuk menghapus data.

Token CSRF sendiri digunakan untuk memastikan bahwa permintaan tersebut benar-benar berasal dari pengguna atau halaman yang sah, bukan dari website lain yang mencoba menyalahgunakan session pengguna.

force_authenticate tidak cukup untuk membuktikan perlindungan CSRF karena force_authenticate merupakan fitur testing yang langsung mengatur pengguna sebagai pengguna yang sudah terautentikasi tanpa melalui proses autentikasi session dan pemeriksaan CSRF seperti pada request sebenarnya. Jadi, pengujian menggunakan force_authenticate hanya membuktikan bahwa autentikasi pengguna dapat dilakukan, bukan membuktikan bahwa perlindungan CSRF berjalan dengan benar.