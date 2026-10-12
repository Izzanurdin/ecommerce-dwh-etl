# 🛒 E-Commerce Data Warehouse & ETL Pipeline

Proyek ini membangun **Data Warehouse (DWH)** menggunakan pendekatan **Star Schema** dengan dataset E-Commerce dari Kaggle.

Seluruh proses **ETL (Extract, Transform, Load)** diimplementasikan menggunakan Python untuk:

* 🧹 Membersihkan dan mentransformasi data mentah
* 🧪 Menghasilkan data pelanggan dan transaksi sintetis
* 🔗 Menghubungkan transaksi dengan produk asli dari dataset Kaggle
* 🏗️ Membentuk tabel **Fact** dan **Dimension**
* 📥 Memuat data final ke database Data Warehouse
* 📊 Menyiapkan data agar dapat digunakan untuk analisis penjualan

---

## 📌 1. Gambaran Singkat Proyek

### 🎯 Tujuan

Data Warehouse dirancang untuk menjawab beberapa pertanyaan analitik utama:

1. **Bagaimana tren penjualan dan pendapatan dari waktu ke waktu?**
2. **Bagaimana performa diskon terhadap jumlah produk yang terjual?**
3. **Siapa pelanggan dengan nilai transaksi tertinggi berdasarkan membership?**
4. **Kategori produk mana yang menghasilkan pendapatan terbesar?**

### 🔄 Gambaran Alur Data

```text
        DATASET KAGGLE
             │
             ▼
       ┌─────────────┐
       │   EXTRACT   │
       └──────┬──────┘
              │
              ▼
       ┌─────────────┐
       │  CLEANSE &  │
       │ TRANSFORM   │
       └──────┬──────┘
              │
              ▼
        DATA PRODUK
        YANG BERSIH
              │
              ├──────────────┐
              │              │
              ▼              ▼
      GENERATE DUMMY     DIM PRODUK
       CUSTOMER &            │
       TRANSACTION           │
              │              │
              └──────┬───────┘
                     ▼
              ┌─────────────┐
              │  LOAD KE    │
              │ DATA WAREHOUSE│
              └──────┬──────┘
                     │
                     ▼
              ⭐ STAR SCHEMA
```

> **Intinya:** Dataset Kaggle digunakan sebagai **Master Data Produk**, sedangkan data pelanggan dan transaksi dibuat secara sintetis agar dapat membangun struktur Data Warehouse yang lengkap.

---

# ⚠️ 2. Dataset & Strategi Data

## 📦 Dataset Utama

Dataset produk yang digunakan berasal dari:

🔗 **[Kaggle — E-Commerce Data (SHEIN)](https://www.kaggle.com/datasets/oleksiimartusiuk/e-commerce-data-shein/data)**

Dataset ini digunakan terutama sebagai sumber **Master Data Produk**.

---

## 🧹 Karakteristik Data Mentah

Dataset Kaggle memiliki beberapa masalah yang sengaja digunakan sebagai bagian dari proses **Data Cleansing**.

| Masalah                    | Kondisi Data                            | Solusi                                   |
| -------------------------- | --------------------------------------- | ---------------------------------------- |
| Product ID tidak eksplisit | ID terdapat di URL                      | Ekstraksi menggunakan Regex              |
| Harga berupa String        | Contoh: `$12.50`                        | Hapus simbol `$`, lalu convert ke Float  |
| Missing Value              | Beberapa kolom memiliki nilai kosong    | Handle Null                              |
| Duplikasi                  | Terdapat kemungkinan ID produk duplikat | Deduplicate berdasarkan Product ID       |
| Kategori tidak eksplisit   | Kategori mengikuti nama file            | Kategori diambil dari metadata/nama file |

---

## 🔀 Hybrid Dataset Strategy

Dataset Kaggle pada dasarnya merupakan **Master Data Katalog Produk**, bukan dataset transaksi lengkap.

Karena Data Warehouse membutuhkan **Fact Table** dan **Dimension Table**, proyek ini menggunakan pendekatan **Hybrid Dataset**:

### Data asli dari Kaggle

Digunakan untuk:

* Product ID
* Nama produk
* Harga
* Rating/data produk lainnya
* Kategori produk

### Data sintetis / Dummy

Dibuat menggunakan Python untuk:

* Data pelanggan
* Membership pelanggan
* Transaksi
* Quantity terjual
* Diskon
* Tanggal transaksi

### Hubungan Data

```text
Kaggle
  │
  ▼
Produk Asli
  │
  │ Product ID
  ▼
Data Cleansing
  │
  ▼
Clean Product Data
  │
  ├───────────────┐
  │               │
  ▼               ▼
Dim Produk    Dummy Transaction
                  │
                  ▼
             Fact Penjualan
```

> ⚠️ **Penting:** Data transaksi merupakan **data sintetis**, bukan transaksi aktual yang berasal dari Kaggle.

---

# 🏗️ 3. Arsitektur Data Warehouse

Proyek menggunakan **Star Schema** untuk mengoptimalkan kebutuhan analitik.

## ⭐ Struktur Star Schema

Data Warehouse terdiri dari:

### Dimension Tables

* `dim_produk`
* `dim_pelanggan`
* `dim_waktu`

### Fact Tables

* `fact_penjualan`
* `fact_performa_diskon`

Setiap tabel fakta terhubung dengan tabel dimensi menggunakan **Surrogate Key (SK)** berupa integer unik.

---

## 🧩 Struktur Konseptual

Secara konseptual, Data Warehouse terdiri dari **3 Dimension Table** dan **2 Fact Table**.

### ⭐ Struktur Utama

```text
                         ┌─────────────────┐
                         │   dim_waktu     │
                         │─────────────────│
                         │ waktu_sk (PK)   │
                         │ tanggal         │
                         │ hari            │
                         │ bulan           │
                         │ tahun           │
                         └────────┬────────┘
                                  │
                                  │
                                  ▼
┌─────────────────┐       ┌─────────────────────┐       ┌─────────────────┐
│  dim_produk     │──────►│   fact_penjualan    │◄──────│ dim_pelanggan   │
│─────────────────│       │─────────────────────│       │─────────────────│
│ produk_sk (PK)  │       │ penjualan_sk (PK)   │       │ pelanggan_sk(PK)│
│ product_id      │       │ produk_sk (FK)      │       │ customer_id     │
│ nama_produk     │       │ pelanggan_sk (FK)   │       │ membership      │
│ kategori        │       │ waktu_sk (FK)       │       │ ...             │
│ harga           │       │ qty                 │       └─────────────────┘
│ ...             │       │ harga_satuan        │
└─────────────────┘       │ total_penjualan     │
                          └──────────┬──────────┘
                                     │
                                     │
                                     │
                          ┌──────────▼──────────┐
                          │ fact_performa_diskon│
                          │─────────────────────│
                          │ diskon_sk (PK)      │
                          │ produk_sk (FK)      │
                          │ waktu_sk (FK)       │
                          │ diskon              │
                          │ qty_terjual         │
                          │ ...                 │
                          └─────────────────────┘
```

### 🔗 Relasi Utama

| Tabel                  | Berperan sebagai | Terhubung dengan                         |
| ---------------------- | ---------------- | ---------------------------------------- |
| `dim_produk`           | Dimension        | `fact_penjualan`, `fact_performa_diskon` |
| `dim_pelanggan`        | Dimension        | `fact_penjualan`                         |
| `dim_waktu`            | Dimension        | `fact_penjualan`, `fact_performa_diskon` |
| `fact_penjualan`       | Fact             | Produk, Pelanggan, Waktu                 |
| `fact_performa_diskon` | Fact             | Produk, Waktu                            |

### 💡 Cara Membacanya

**`fact_penjualan`** merupakan fact table utama yang mencatat kejadian transaksi.

```text
Produk + Pelanggan + Waktu
            │
            ▼
     FACT PENJUALAN
            │
            ▼
   Qty & Total Penjualan
```

Sedangkan **`fact_performa_diskon`** digunakan secara khusus untuk menganalisis hubungan antara diskon dan performa penjualan produk.

```text
Produk + Waktu
      │
      ▼
FACT PERFORMA DISKON
      │
      ▼
Diskon + Qty Terjual
```

Dengan struktur ini, analisis dapat dilakukan berdasarkan:

* 📅 **Waktu** → tren penjualan harian/bulanan/tahunan
* 🛍️ **Produk** → performa dan pendapatan berdasarkan produk/kategori
* 👤 **Pelanggan** → profil dan nilai transaksi berdasarkan membership
* 🏷️ **Diskon** → pengaruh diskon terhadap jumlah produk terjual


### ERD

Visualisasi lengkap Star Schema dapat dilihat pada:

![Star Schema ERD](./sql/star-schema-e-commerce-dwh.png)

---

# 👥 4. Tim & Pembagian Tugas

| Anggota                                  | Role                    | Fokus                      |
| ---------------------------------------- | ----------------------- | -------------------------- |
| **Muhammad Izzanurdin Hasan_2505551075** | 🏗️ Data Architect      | Star Schema & Database     |
| **Christopher**                          | 🧹 Cleansing Specialist | Data Profiling & Cleansing |
| **Mul**                                  | ⚙️ Pipeline Engineer    | Dummy Data & ETL           |

---

## 🏗️ Anggota 1 — Data Architect

**Muhammad Izzanurdin Hasan_2505551075**

### Fokus

```text
/sql/
```

### Tanggung Jawab

* Mendesain Star Schema
* Membuat ERD
* Membuat DBML
* Membuat DDL Database
* Menentukan Primary Key dan Foreign Key
* Melakukan setup database lokal

---

## 🧹 Anggota 2 — Cleansing Specialist

**Christopher**

### Fokus

```text
/notebooks/
/src/cleanse_data.py
```

### Tanggung Jawab

* Data profiling
* Menentukan kategori dataset yang digunakan
* Ekstraksi Product ID menggunakan Regex
* Membersihkan harga
* Handle Missing Value
* Menghapus duplikasi
* Validasi hasil cleansing

---

## ⚙️ Anggota 3 — Pipeline Engineer

**Mul**

### Fokus

```text
/src/
```

### Tanggung Jawab

* Membuat generator data dummy
* Membuat data pelanggan
* Membuat data transaksi
* Menghubungkan transaksi dengan Product ID hasil cleansing
* Membuat pipeline ETL
* Melakukan Load data ke Data Warehouse

---

# 🗂️ 5. Struktur Repository

```text
ecommerce-dwh-etl/
│
├── data/                    # Tidak masuk GitHub
│   ├── raw/                 # Dataset mentah dari Kaggle
│   ├── interim/             # Data setelah cleansing
│   └── processed/           # Data final siap masuk DWH
│
├── notebooks/               # Eksplorasi & data profiling
│   └── *.ipynb
│
├── src/                     # Source code ETL
│   ├── generate_dummy.py
│   ├── cleanse_data.py
│   └── run_etl.py
│
├── sql/                     # Database & Star Schema
│   ├── dbml_star_schema.dbml
│   ├── ddl_star_schema.sql
│   └── star-schema-e-commerce-dwh.png
│
├── .gitignore
├── requirements.txt
└── README.md
```

### 📁 Fungsi Folder Data

| Folder            | Isi                       | Status       |
| ----------------- | ------------------------- | ------------ |
| `data/raw/`       | Dataset asli Kaggle       | Input        |
| `data/interim/`   | Dataset setelah cleansing | Intermediate |
| `data/processed/` | Data final siap di-load   | Output ETL   |

> 🚫 Folder `data/` **tidak di-upload ke GitHub** karena ukuran dataset cukup besar.

---

# 🚀 6. Setup Project di Komputer Lokal

> ⚠️ **WAJIB:** Setiap anggota kelompok harus melakukan setup dataset secara lokal sebelum menjalankan script Python.

---

## Step 1 — Clone Repository

```bash
git clone https://github.com/Izzanurdin/ecommerce-dwh-etl.git
cd ecommerce-dwh-etl
```

---

## Step 2 — Buat Virtual Environment

Disarankan menggunakan virtual environment agar dependency project tidak bercampur dengan Python system.

### Windows

```bash
python -m venv env
env\Scripts\activate
```

### Mac / Linux

```bash
python -m venv env
source env/bin/activate
```

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 📦 7. Persiapan Dataset

## Step 1 — Buat Folder Data

Di dalam root project:

```text
ecommerce-dwh-etl/
└── data/
```

Kemudian buat:

```text
data/
├── raw/
├── interim/
└── processed/
```

Sehingga struktur akhirnya:

```text
ecommerce-dwh-etl/data/raw/
ecommerce-dwh-etl/data/interim/
ecommerce-dwh-etl/data/processed/
```

---

## Step 2 — Download Dataset

Buka:

🔗 **[Kaggle — E-Commerce Data (SHEIN)](https://www.kaggle.com/datasets/oleksiimartusiuk/e-commerce-data-shein/data)**

Kemudian:

1. Download file `.zip`
2. Extract file tersebut
3. Pilih **1–3 file CSV kategori**
4. Copy file CSV tersebut ke:

```text
data/raw/
```

Contoh:

```text
data/
└── raw/
    ├── us-shein-electronics-4395.csv
    └── us-shein-appliances-3987.csv
```

> 💡 Tidak perlu memasukkan seluruh dataset. Untuk development/testing, gunakan 1–3 kategori terlebih dahulu.

---

# 🔄 8. ETL Workflow

Setelah dataset tersedia, proses dilakukan dalam **3 tahap utama**:

```text
RAW DATA
   │
   ▼
[1] CLEANSE
   │
   ▼
INTERIM DATA
   │
   ▼
[2] GENERATE DUMMY
   │
   ▼
PROCESSED DATA
   │
   ▼
[3] LOAD
   │
   ▼
DATA WAREHOUSE
```

---

## 1️⃣ Data Cleansing

Jalankan:

```bash
python src/cleanse_data.py
```

Script akan:

* Membaca data dari `data/raw/`
* Mengekstrak Product ID
* Membersihkan harga
* Menangani Null
* Menghapus duplikasi
* Melakukan validasi data

Output:

```text
data/interim/
```

---

## 2️⃣ Generate Dummy Data

Jalankan:

```bash
python src/generate_dummy.py
```

Script akan:

* Membaca data produk bersih
* Membuat data pelanggan sintetis
* Membuat data transaksi sintetis
* Membuat membership
* Membuat quantity
* Membuat data diskon
* Menghubungkan transaksi dengan Product ID

Output:

```text
data/processed/
```

---

## 3️⃣ Load ke Data Warehouse

Jalankan:

```bash
python src/run_etl.py
```

Script akan:

* Membaca data dari `data/processed/`
* Melakukan transformasi akhir jika diperlukan
* Mengisi tabel dimensi
* Mengisi tabel fakta
* Memuat data ke database DWH

Output akhirnya:

```text
DATABASE
   │
   ├── dim_produk
   ├── dim_pelanggan
   ├── dim_waktu
   ├── fact_penjualan
   └── fact_performa_diskon
```

---

# 🌿 9. Git Branching Strategy

Agar pekerjaan antar anggota tidak saling menimpa, **jangan langsung bekerja di `main`**.

## Alur kerja

```text
main
 │
 ├── feature/schema-design
 │
 ├── feature/data-cleansing
 │
 └── feature/etl-pipeline
```

---

## Step 1 — Update Branch

Sebelum mulai bekerja:

```bash
git checkout main
git pull origin main
```

---

## Step 2 — Buat Feature Branch

### Data Architect

```bash
git checkout -b feature/schema-design
```

### Cleansing Specialist

```bash
git checkout -b feature/data-cleansing
```

### Pipeline Engineer

```bash
git checkout -b feature/etl-pipeline
```

---

## Step 3 — Commit Perubahan

Contoh:

```bash
git add .
git commit -m "feat: add product cleansing logic"
```

---

## Step 4 — Push Branch

```bash
git push origin feature/nama-branch
```

Contoh:

```bash
git push origin feature/data-cleansing
```

---

## Step 5 — Pull Request

Setelah selesai:

```text
Feature Branch
      │
      ▼
 GitHub Pull Request
      │
      ▼
 Code Review
      │
      ▼
    main
```

> 💡 Selama Pull Request belum di-merge, anggota masih boleh melakukan `git push` berkali-kali ke branch yang sama.

---

# 📊 10. Progress Tracker

Gunakan tabel berikut untuk memantau progres masing-masing anggota.

**Status:**

* `[ ]` = Belum selesai
* `[x]` = Selesai

| Role                        | Task                                        | Status | Branch                   |
| --------------------------- | ------------------------------------------- | :----: | ------------------------ |
| 🏗️ **Data Architect**      | Merancang Star Schema (3 Dimensi + 2 Fakta) |   [ ]  | `feature/schema-design`  |
|                             | Membuat ERD & DBML                          |   [ ]  | `feature/schema-design`  |
|                             | Membuat DDL Database                        |   [ ]  | `feature/schema-design`  |
|                             | Setup Database lokal                        |   [ ]  | —                        |
| 🧹 **Cleansing Specialist** | Menentukan kategori dataset Kaggle          |   [ ]  | `feature/data-cleansing` |
|                             | Ekstraksi Product ID dengan Regex           |   [ ]  | `feature/data-cleansing` |
|                             | Membersihkan data harga                     |   [ ]  | `feature/data-cleansing` |
|                             | Handle Null                                 |   [ ]  | `feature/data-cleansing` |
|                             | Menghapus duplikasi Product ID              |   [ ]  | `feature/data-cleansing` |
| ⚙️ **Pipeline Engineer**    | Membuat repository & struktur project       |   [x]  | `main`                   |
|                             | Membuat `generate_dummy.py`                 |   [ ]  | `feature/etl-pipeline`   |
|                             | Sinkronisasi Product ID                     |   [ ]  | `feature/etl-pipeline`   |
|                             | Membuat `run_etl.py`                        |   [ ]  | `feature/etl-pipeline`   |
| 👥 **Semua Anggota**        | Integrasi seluruh pipeline                  |   [ ]  | `main`                   |
|                             | End-to-end testing                          |   [ ]  | `main`                   |
|                             | Dokumentasi hasil DWH                       |   [ ]  | —                        |
|                             | Dokumentasi before/after cleansing          |   [ ]  | —                        |

---

# 🧪 11. Checklist Sebelum Project Dianggap Selesai

### Data

* [ ] Dataset Kaggle berhasil dibaca
* [ ] Product ID berhasil diekstrak
* [ ] Harga berhasil dibersihkan
* [ ] Null berhasil ditangani
* [ ] Duplikasi berhasil ditangani
* [ ] Data hasil cleansing tersimpan di `data/interim/`

### Dummy Data

* [ ] Customer berhasil dibuat
* [ ] Membership berhasil dibuat
* [ ] Transaction berhasil dibuat
* [ ] Product ID transaction valid
* [ ] Data tersimpan di `data/processed/`

### Database

* [ ] `dim_produk` berhasil dibuat
* [ ] `dim_pelanggan` berhasil dibuat
* [ ] `dim_waktu` berhasil dibuat
* [ ] `fact_penjualan` berhasil dibuat
* [ ] `fact_performa_diskon` berhasil dibuat
* [ ] Foreign Key terhubung dengan benar

### ETL

* [ ] Extract berhasil
* [ ] Transform berhasil
* [ ] Load berhasil
* [ ] Tidak ada error pada pipeline
* [ ] Data dapat di-query dari DWH

### Dokumentasi

* [ ] Screenshot data sebelum cleansing
* [ ] Screenshot data sesudah cleansing
* [ ] Screenshot tabel DWH
* [ ] Screenshot hasil query analitik
* [ ] README sudah diperbarui

---

# 🧑‍💻 12. Quick Start

Kalau semua setup sudah selesai, workflow utamanya cukup:

```bash
# 1. Clean data
python src/cleanse_data.py

# 2. Generate customer & transaction
python src/generate_dummy.py

# 3. Load ke Data Warehouse
python src/run_etl.py
```

Atau secara sederhana:

```text
Kaggle CSV
    ↓
cleanse_data.py
    ↓
data/interim/
    ↓
generate_dummy.py
    ↓
data/processed/
    ↓
run_etl.py
    ↓
⭐ Data Warehouse
```

---

# 📚 13. Ringkasan Project

| Komponen        | Teknologi / Sumber               |
| --------------- | -------------------------------- |
| Dataset         | Kaggle — E-Commerce Data (SHEIN) |
| Programming     | Python                           |
| Data Processing | Pandas / Python                  |
| Data Warehouse  | MySQL / PostgreSQL               |
| Schema          | Star Schema                      |
| ETL             | Python                           |
| Version Control | Git + GitHub                     |
| Data Produk     | Real Dataset                     |
| Customer        | Synthetic / Dummy                |
| Transaction     | Synthetic / Dummy                |

---

## 👥 Prinsip Kerja Tim

> **Jangan hanya membuat script masing-masing. Pastikan seluruh bagian akhirnya dapat terintegrasi menjadi satu pipeline.**

Target akhirnya:

```text
┌───────────────┐
│  Kaggle Data  │
└───────┬───────┘
        ▼
┌───────────────┐
│ Data Cleansing│
└───────┬───────┘
        ▼
┌───────────────┐
│  Dummy Data   │
└───────┬───────┘
        ▼
┌───────────────┐
│   ETL Load    │
└───────┬───────┘
        ▼
┌─────────────────────────┐
│   DATA WAREHOUSE        │
│                         │
│  dim_produk             │
│  dim_pelanggan          │
│  dim_waktu              │
│  fact_penjualan         │
│  fact_performa_diskon   │
└─────────────────────────┘
        ▼
┌─────────────────────────┐
│   ANALYTICAL QUERY      │
└─────────────────────────┘
```

**End Goal:** menghasilkan Data Warehouse E-Commerce yang **terstruktur, terintegrasi, dapat di-query, dan mampu menjawab kebutuhan analitik proyek**
