import pandas as pd
import glob
import os

print("Lagi proses cleansing data...")

# Baca semua file CSV di data/raw/
raw_files = glob.glob('data/raw/*.csv')

if not raw_files:
    print("Error: Nggak ketemu file CSV di folder data/raw!")
else:
    df_list = [pd.read_csv(f) for f in raw_files]
    df = pd.concat(df_list, ignore_index=True)
    print(f"Total data mentah: {len(df)} baris")

    # 1. Deteksi kolom URL spesifik (href)
    href_col = next((c for c in df.columns if 'href' in c.lower()), None)
    
    if href_col:
        # Ambil deretan angka unik dari URL produk
        df['product_id'] = df[href_col].astype(str).str.extract(r'(\d+)')
    else:
        df['product_id'] = None

    # Jika ID kosong/tidak terekstrak, isi dengan urutan angka unik agar data tidak terbuang
    df['product_id'] = df['product_id'].fillna(pd.Series(df.index).astype(str))

    # 2. Membersihkan Harga (buang simbol $ dan ubah ke float)
    price_col = next((c for c in df.columns if 'price' in c.lower()), None)
    if price_col:
        df['price_clean'] = df[price_col].astype(str).str.replace('$', '', regex=False)
        df['price_clean'] = pd.to_numeric(df['price_clean'], errors='coerce')
    else:
        df['price_clean'] = 0.0

    # 3. Handle Missing Value (NULL) & Hapus Duplikat
    df = df.dropna(subset=['product_id', 'price_clean'])
    df = df.drop_duplicates(subset=['product_id'])

    print(f"Total data bersih: {len(df)} baris")

    # 4. Simpan ke data/interim/
    os.makedirs('data/interim', exist_ok=True)
    output_path = 'data/interim/clean_products.csv'
    df.to_csv(output_path, index=False)

    print(f"Selesai! Data bersih disimpan di: {output_path}")