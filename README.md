# Excel Dosya Karşılaştırma Scripti

Bu script `ai.xls` ve `Kitap1.xlsx` dosyalarını karşılaştırarak, `ai.xls` dosyasında bulunan ancak `Kitap1.xlsx` dosyasında bulunmayan kayıtları bulur.

## Gereksinimler

```bash
pip install pandas openpyxl xlrd
```

## Kullanım

```bash
python3 fark_bul.py
```

## İşleyiş

1. **ai.xls** dosyasından `full_name` ve `phone_number` alanları okunur
2. **Kitap1.xlsx** dosyasından `Ad` + `Soyad` (full_name) ve `Telefon` (phone_number) alanları okunur
3. Her iki dosyadaki veriler normalize edilir:
   - İsimler: küçük harf, fazla boşluklar temizlenir
   - Telefon numaraları: sadece rakamlar kalır
4. Karşılaştırma yapılır ve fark kayıtları belirlenir
5. Sonuç **fark.xlsx** dosyasına kaydedilir

## Çıktı

- `fark.xlsx`: ai.xls'de bulunan ancak Kitap1.xlsx'de bulunmayan tüm kayıtlar
- Konsol çıktısı: İşlem özeti ve istatistikler

## Dosya Yapısı

- `ai.xls`: Kaynak dosya (1931 kayıt)
- `Kitap1.xlsx`: Karşılaştırma dosyası (848 kayıt)
- `fark.xlsx`: Sonuç dosyası (fark kayıtları)
- `fark_bul.py`: Ana script