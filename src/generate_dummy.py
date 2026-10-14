import os
import random
import pandas as pd
import numpy as np
from faker import Faker

# KONFIGURASI
fake = Faker("id_ID")
random.seed(42)
np.random.seed(42)
Faker.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")
INTERIM_FILE = os.path.join(
    BASE_DIR, "data", "interim", "clean_products.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

JUMLAH_PELANGGAN = 100
JUMLAH_TRANSAKSI = 1000
TANGGAL_MULAI = "2025-01-01"
TANGGAL_AKHIR = "2025-12-31"

# 1. GENERATE DIMENSI PELANGGAN
pelanggan = pd.DataFrame([
    {
        "nk_pelanggan_id": f"CUST{i:05d}",
        "nama_pelanggan": fake.name(),
        "tipe_member": random.choice(
            ["Bronze", "Silver", "Gold", "Platinum"]
        ),
        "kota": fake.city()
    }
    for i in range(1, JUMLAH_PELANGGAN + 1)
])

pelanggan.insert(
    0, "sk_pelanggan", range(1, len(pelanggan) + 1)
)


# 2. GENERATE DIMENSI WAKTU
tanggal_range = pd.date_range(
    TANGGAL_MULAI, TANGGAL_AKHIR, freq="D"
)

waktu = pd.DataFrame({"tanggal": tanggal_range})
waktu["sk_waktu"] = waktu["tanggal"].dt.strftime("%Y%m%d").astype(int)
waktu["hari"] = waktu["tanggal"].dt.day
waktu["bulan"] = waktu["tanggal"].dt.month

# Nama bulan berbahasa Indonesia
nama_bulan = {
    1: "Januari", 2: "Februari", 3: "Maret",
    4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September",
    10: "Oktober", 11: "November", 12: "Desember"
}

waktu["nama_bulan"] = waktu["bulan"].map(nama_bulan)
waktu["kuartal"] = waktu["tanggal"].dt.quarter
waktu["tahun"] = waktu["tanggal"].dt.year
waktu["tanggal"] = waktu["tanggal"].dt.strftime("%Y-%m-%d")

waktu = waktu[
    ["sk_waktu", "tanggal", "hari", "bulan",
     "nama_bulan", "kuartal", "tahun"]
]

# 3. MENYIAPKAN DIMENSI PRODUK
if os.path.exists(INTERIM_FILE):
    produk = pd.read_csv(INTERIM_FILE)

    if "product_id" not in produk.columns:
        raise ValueError(
            "Kolom product_id tidak ditemukan di clean_products.csv."
        )

    if "price_clean" not in produk.columns:
        raise ValueError(
            "Kolom price_clean tidak ditemukan di clean_products.csv."
        )

    name_col = next(
        (
            col for col in produk.columns
            if "name" in col.lower() or "title" in col.lower()
        ),
        None
    )

    category_col = next(
        (
            col for col in produk.columns
            if "category" in col.lower()
        ),
        None
    )

    produk_dummy = pd.DataFrame({
        "nk_produk_id": produk["product_id"].astype(str),
        "nama_produk": (
            produk[name_col].fillna("Produk").astype(str)
            if name_col else "Produk"
        ),
        "kategori": (
            produk[category_col].fillna("Lainnya").astype(str)
            if category_col else "Lainnya"
        ),
        "harga_asli": pd.to_numeric(
            produk["price_clean"], errors="coerce"
        )
    })

    produk_dummy = produk_dummy.dropna(subset=["harga_asli"])
    produk_dummy = produk_dummy[produk_dummy["harga_asli"] >= 0]
    produk_dummy = produk_dummy.drop_duplicates(
        subset=["nk_produk_id"]
    )

    if produk_dummy.empty:
        raise ValueError("Tidak ada produk valid dari hasil cleansing.")

    produk_dummy["status_aktif"] = True

else:
    # Data demo untuk pengujian tanpa dataset asli
    produk_dummy = pd.DataFrame([
        {
            "nk_produk_id": f"DEMO{i:03d}",
            "nama_produk": f"Produk Demo {i}",
            "kategori": random.choice(
                ["Pakaian", "Aksesori", "Elektronik"]
            ),
            "harga_asli": round(random.uniform(10, 100), 2),
            "status_aktif": True
        }
        for i in range(1, 21)
    ])

produk_dummy = produk_dummy.reset_index(drop=True)
produk_dummy.insert(
    0, "sk_produk", range(1, len(produk_dummy) + 1)
)

produk_dummy = produk_dummy[
    ["sk_produk", "nk_produk_id", "nama_produk",
     "kategori", "harga_asli", "status_aktif"]
]

# 4. GENERATE DATA FAKTA
penjualan = []
performa_diskon = []

for _ in range(JUMLAH_TRANSAKSI):
    produk_row = produk_dummy.sample(1).iloc[0]
    pelanggan_row = pelanggan.sample(1).iloc[0]
    waktu_row = waktu.sample(1).iloc[0]

    qty = random.randint(1, 5)
    harga = float(produk_row["harga_asli"])
    diskon = random.choice([0, 5, 10, 15, 20])

    potongan_per_item = harga * diskon / 100
    total = max(0, (harga - potongan_per_item) * qty)

    penjualan.append({
        "sk_produk": int(produk_row["sk_produk"]),
        "sk_pelanggan": int(pelanggan_row["sk_pelanggan"]),
        "sk_waktu": int(waktu_row["sk_waktu"]),
        "qty_terjual": qty,
        "total_bayar": round(total, 2)
    })

    if diskon > 0:
        performa_diskon.append({
            "sk_produk": int(produk_row["sk_produk"]),
            "sk_waktu": int(waktu_row["sk_waktu"]),
            "persentase_diskon": diskon,
            "potongan_harga": round(potongan_per_item, 2),
            "qty_terjual_diskon": qty
        })


# 5. SIMPAN CSV SESUAI STRUKTUR STAR SCHEMA
produk_dummy.to_csv(
    os.path.join(OUTPUT_DIR, "dim_produk.csv"), index=False
)

pelanggan.to_csv(
    os.path.join(OUTPUT_DIR, "dim_pelanggan.csv"), index=False
)

waktu.to_csv(
    os.path.join(OUTPUT_DIR, "dim_waktu.csv"), index=False
)

pd.DataFrame(penjualan).to_csv(
    os.path.join(OUTPUT_DIR, "dummy_penjualan.csv"), index=False
)

pd.DataFrame(performa_diskon).to_csv(
    os.path.join(OUTPUT_DIR, "dummy_performa_diskon.csv"),
    index=False
)


# 6. RINGKASAN
print("Generate data dummy selesai!")
print(f"Produk: {len(produk_dummy)}")
print(f"Pelanggan: {len(pelanggan)}")
print(f"Waktu: {len(waktu)}")
print(f"Transaksi: {len(penjualan)}")
print(f"Data performa diskon: {len(performa_diskon)}")
print(f"Output tersimpan di: {OUTPUT_DIR}")