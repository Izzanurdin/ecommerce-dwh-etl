-- DDL Script untuk membuat Star Schema Data Warehouse E-Commerce

-- 1. Membuat Database (Opsional, pastikan di-uncomment jika belum ada)
 CREATE DATABASE ecommerce_dwh;
 USE ecommerce_dwh;

-- 2. Membuat Tabel Dimensi (Dimension Tables)

CREATE TABLE dim_produk (
    sk_produk INT AUTO_INCREMENT PRIMARY KEY,
    nk_produk_id VARCHAR(50) NOT NULL,
    nama_produk VARCHAR(255),
    kategori VARCHAR(100),
    harga_asli DECIMAL(15,2),
    status_aktif BOOLEAN DEFAULT TRUE
);

CREATE TABLE dim_pelanggan (
    sk_pelanggan INT AUTO_INCREMENT PRIMARY KEY,
    nk_pelanggan_id VARCHAR(50) NOT NULL,
    nama_pelanggan VARCHAR(150),
    tipe_member VARCHAR(50),
    kota VARCHAR(100)
);

CREATE TABLE dim_waktu (
    sk_waktu INT PRIMARY KEY,
    tanggal DATE,
    hari INT,
    bulan INT,
    nama_bulan VARCHAR(20),
    kuartal INT,
    tahun INT
);

-- 3. Membuat Tabel Fakta (Fact Tables)

CREATE TABLE fact_penjualan (
    sk_penjualan INT AUTO_INCREMENT PRIMARY KEY,
    sk_produk INT,
    sk_pelanggan INT,
    sk_waktu INT,
    qty_terjual INT,
    total_bayar DECIMAL(15,2),
    FOREIGN KEY (sk_produk) REFERENCES dim_produk(sk_produk),
    FOREIGN KEY (sk_pelanggan) REFERENCES dim_pelanggan(sk_pelanggan),
    FOREIGN KEY (sk_waktu) REFERENCES dim_waktu(sk_waktu)
);

CREATE TABLE fact_performa_diskon (
    sk_diskon INT AUTO_INCREMENT PRIMARY KEY,
    sk_produk INT,
    sk_waktu INT,
    persentase_diskon DECIMAL(5,2),
    potongan_harga DECIMAL(15,2),
    qty_terjual_diskon INT,
    FOREIGN KEY (sk_produk) REFERENCES dim_produk(sk_produk),
    FOREIGN KEY (sk_waktu) REFERENCES dim_waktu(sk_waktu)
);