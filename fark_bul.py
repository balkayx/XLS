#!/usr/bin/env python3
"""
Excel dosyalarını karşılaştırıp fark kayıtlarını bulan script.
ai.xls dosyasında bulunan ancak Kitap1.xlsx dosyasında bulunmayan kayıtları bulur.
Karşılaştırma 'full_name' ve 'phone_number' alanlarına göre yapılır.
"""

import pandas as pd
import re
import os


def normalize_phone(phone):
    """Telefon numarasını normalize et (sadece rakamlar)"""
    if pd.isna(phone) or phone is None:
        return ""
    # Sadece rakamları al
    phone_str = str(phone)
    normalized = re.sub(r'[^\d]', '', phone_str)
    return normalized


def normalize_name(name):
    """İsmi normalize et (küçük harf, fazla boşlukları temizle)"""
    if pd.isna(name) or name is None:
        return ""
    # Küçük harf yap ve fazla boşlukları temizle
    normalized = str(name).lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


def read_ai_file(filename):
    """ai.xls dosyasını oku ve normalize et"""
    print(f"'{filename}' dosyası okunuyor...")
    
    try:
        df = pd.read_excel(filename)
        print(f"Toplam {len(df)} kayıt bulundu.")
        
        # Gerekli kolonları kontrol et
        if 'full_name' not in df.columns or 'phone_number' not in df.columns:
            raise ValueError("'full_name' ve 'phone_number' kolonları bulunamadı!")
        
        # Sadece gerekli kolonları al ve normalize et
        df_clean = df[['full_name', 'phone_number']].copy()
        df_clean['normalized_name'] = df_clean['full_name'].apply(normalize_name)
        df_clean['normalized_phone'] = df_clean['phone_number'].apply(normalize_phone)
        
        # Boş kayıtları filtrele
        df_clean = df_clean[
            (df_clean['normalized_name'] != '') | 
            (df_clean['normalized_phone'] != '')
        ].copy()
        
        print(f"Normalize edilmiş {len(df_clean)} geçerli kayıt.")
        return df, df_clean
        
    except Exception as e:
        print(f"Hata: {filename} dosyası okunurken hata oluştu: {e}")
        raise


def read_kitap_file(filename):
    """Kitap1.xlsx dosyasını oku ve normalize et"""
    print(f"'{filename}' dosyası okunuyor...")
    
    try:
        df = pd.read_excel(filename)
        print(f"Toplam {len(df)} kayıt bulundu.")
        
        # Gerekli kolonları kontrol et
        required_cols = ['Ad', 'Soyad', 'Telefon']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Gerekli kolonlar bulunamadı: {missing_cols}")
        
        # Full name oluştur (Ad + Soyad)
        df['full_name'] = (
            df['Ad'].fillna('').astype(str) + ' ' + 
            df['Soyad'].fillna('').astype(str)
        ).str.strip()
        
        # Telefon kolonunu phone_number olarak al
        df['phone_number'] = df['Telefon']
        
        # Normalize et
        df['normalized_name'] = df['full_name'].apply(normalize_name)
        df['normalized_phone'] = df['phone_number'].apply(normalize_phone)
        
        # Sadece gerekli kolonları al
        df_clean = df[['full_name', 'phone_number', 'normalized_name', 'normalized_phone']].copy()
        
        # Boş kayıtları filtrele
        df_clean = df_clean[
            (df_clean['normalized_name'] != '') | 
            (df_clean['normalized_phone'] != '')
        ].copy()
        
        print(f"Normalize edilmiş {len(df_clean)} geçerli kayıt.")
        return df, df_clean
        
    except Exception as e:
        print(f"Hata: {filename} dosyası okunurken hata oluştu: {e}")
        raise


def find_differences(ai_df, kitap_df):
    """ai.xls'de olup Kitap1.xlsx'de olmayan kayıtları bul"""
    print("\nFark kayıtları aranıyor...")
    
    # Kitap1.xlsx'deki normalize edilmiş değerleri set olarak al
    kitap_set = set()
    for _, row in kitap_df.iterrows():
        # Hem isim hem telefon ile eşleştir
        key = (row['normalized_name'], row['normalized_phone'])
        kitap_set.add(key)
        
        # Sadece isimle eşleştir (telefon boş olabilir)
        if row['normalized_name']:
            kitap_set.add((row['normalized_name'], ''))
            
        # Sadece telefonla eşleştir (isim boş olabilir)
        if row['normalized_phone']:
            kitap_set.add(('', row['normalized_phone']))
    
    # ai.xls'deki kayıtları kontrol et
    differences = []
    for idx, row in ai_df.iterrows():
        name_key = row['normalized_name']
        phone_key = row['normalized_phone']
        
        # Eşleşme kontrolü
        found = False
        
        # Tam eşleşme (hem isim hem telefon)
        if (name_key, phone_key) in kitap_set:
            found = True
        # İsim eşleşmesi (telefon farklı olabilir)
        elif name_key and (name_key, '') in kitap_set:
            found = True
        # Telefon eşleşmesi (isim farklı olabilir)
        elif phone_key and ('', phone_key) in kitap_set:
            found = True
        
        if not found:
            differences.append(idx)
    
    print(f"Toplam {len(differences)} fark kaydı bulundu.")
    return differences


def main():
    """Ana fonksiyon"""
    print("Excel dosyalarını karşılaştırma scripti başlatılıyor...\n")
    
    # Dosya yolları
    ai_file = 'ai.xls'
    kitap_file = 'Kitap1.xlsx'
    output_file = 'fark.xlsx'
    
    try:
        # Dosyaları oku
        ai_original, ai_clean = read_ai_file(ai_file)
        kitap_original, kitap_clean = read_kitap_file(kitap_file)
        
        # Farkları bul
        diff_indices = find_differences(ai_clean, kitap_clean)
        
        if not diff_indices:
            print("Hiç fark kaydı bulunamadı. Tüm kayıtlar her iki dosyada da mevcut.")
            return
        
        # Fark kayıtlarını al
        diff_records = ai_original.iloc[diff_indices].copy()
        
        # Sonuçları kaydet
        print(f"\nFark kayıtları '{output_file}' dosyasına yazılıyor...")
        diff_records.to_excel(output_file, index=False)
        
        print(f"İşlem tamamlandı!")
        print(f"- ai.xls'de toplam {len(ai_original)} kayıt")
        print(f"- Kitap1.xlsx'de toplam {len(kitap_original)} kayıt")
        print(f"- Fark: {len(diff_records)} kayıt")
        print(f"- Sonuç dosyası: {output_file}")
        
        # Özet istatistik
        print(f"\nÖzet:")
        print(f"ai.xls'de bulunan ancak Kitap1.xlsx'de bulunmayan {len(diff_records)} kayıt {output_file} dosyasına kaydedildi.")
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)