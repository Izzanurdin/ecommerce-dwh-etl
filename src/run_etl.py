import os
import subprocess
import sys


# KONFIGURASI DIREKTORI
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_INTERIM_DIR = os.path.join(BASE_DIR, "data", "interim")
DATA_INTERIM_FILE = os.path.join(DATA_INTERIM_DIR, "clean_products.csv")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


# FUNGSI MENJALANKAN SCRIPT
def run_script(script_name):
    script_path = os.path.join(SRC_DIR, script_name)

    print(f"\nMenjalankan {script_name}...", flush=True)

    result = subprocess.run(
        [sys.executable, script_path],
        cwd=BASE_DIR
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Proses {script_name} gagal dijalankan."
        )


# FUNGSI UTAMA PIPELINE ETL
def main():
    print("=" * 50)
    print("PIPELINE ETL E-COMMERCE DATA WAREHOUSE")
    print("=" * 50)

    # 1. Memeriksa ketersediaan data mentah
    raw_exists = (
        os.path.isdir(DATA_RAW_DIR)
        and any(
            file.lower().endswith(".csv")
            for file in os.listdir(DATA_RAW_DIR)
        )
    )

    # 2. Menjalankan cleansing atau menggunakan data demo
    if raw_exists:
        print("\n[1/2] Menjalankan proses cleansing data...")

        run_script("cleanse_data.py")

        if not os.path.isfile(DATA_INTERIM_FILE):
            raise RuntimeError(
                "File clean_products.csv tidak ditemukan "
                "setelah proses cleansing."
            )

        print("Data produk hasil cleansing berhasil disiapkan.")

    else:
        print("\nData mentah belum tersedia.")
        print("Pipeline menggunakan 20 produk demo.")

        # Hapus hasil cleansing lama agar generator
        # tidak keliru memakai data lama.
        if os.path.isfile(DATA_INTERIM_FILE):
            os.remove(DATA_INTERIM_FILE)

    # 3. Membuat data dimensi dan fakta sintetis
    print("\n[2/2] Menjalankan proses generate data...")

    run_script("generate_dummy.py")

    # 4. Memastikan file output tersedia
    expected_files = [
        "dim_produk.csv",
        "dim_pelanggan.csv",
        "dim_waktu.csv",
        "dummy_penjualan.csv",
        "dummy_performa_diskon.csv"
    ]

    missing_files = [
        filename
        for filename in expected_files
        if not os.path.isfile(
            os.path.join(DATA_PROCESSED_DIR, filename)
        )
    ]

    if missing_files:
        raise RuntimeError(
            "File output tidak ditemukan: "
            + ", ".join(missing_files)
        )

    # 5. Ringkasan hasil pipeline
    print("\n" + "=" * 50)
    print("PIPELINE ETL BERHASIL DIJALANKAN!")
    print("=" * 50)
    print("File output tersedia di data/processed/:")

    for filename in expected_files:
        print(f"- {filename}")

    print("\nCatatan: Data masih berupa CSV.")
    print("Proses loading ke MySQL tidak dijalankan.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError) as error:
        print(f"\nERROR: {error}")
        sys.exit(1)