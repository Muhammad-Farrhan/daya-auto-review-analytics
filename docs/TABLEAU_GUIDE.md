# Panduan Tableau

## 1. Menyambungkan data
Tableau Public tidak bisa terhubung ke PostgreSQL lokal. Alurnya: `python src/export_tableau.py` →
folder `exports/` → Tableau **Text file** (CSV). Satu workbook, banyak sumber data; hubungkan lewat `app_key`
(Relationships) bila perlu. Muat ulang file tiap kali data diperbarui.

## 2. Jebakan agregasi (penting)
File bulanan sudah berisi rata-rata. Jika dirata-ratakan lagi lintas bulan hasilnya salah. Pakai rata-rata berbobot:

```
Rating Berbobot      = SUM([Avg Rating] * [N Reviews]) / SUM([N Reviews])
% Negatif Berbobot   = SUM([Pct Negative] * [N Reviews]) / SUM([N Reviews])
% Dibalas Berbobot   = SUM([Pct Replied] * [N Reviews]) / SUM([N Reviews])
```

## 3. Calculated field & parameter
```
Aplikasi Fokus?      = [Role] = 'focus'
Perubahan Rating MoM = ZN(AVG([Avg Rating])) - LOOKUP(ZN(AVG([Avg Rating])), -1)
Total Ulasan Aplikasi= {FIXED [App Name] : SUM([N Reviews])}
Bulan Terakhir       = {FIXED [App Name] : MAX([Review Month])}

-- Parameter p_freq, p_sev, p_eng (Float, 0–1, step 0.05) agar pembaca bisa mengubah bobot:
Skor Prioritas (param) = 100 * ( [p_freq]*[Freq N] + [p_sev]*[Sev N] + [p_eng]*[Eng N] )
Peringkat (param)      = RANK_UNIQUE([Skor Prioritas (param)])        -- table calc, partisi per App Name

Delta Rating Pakai?    = IF [Has Overlapping Release] THEN 'Rilis berdekatan' ELSE 'OK' END
```
Set parameter periode (Date range) untuk filter bulan, dan parameter "Pilih aplikasi pembanding".

## 4. Halaman dashboard
| # | Halaman | Sumber | Isi |
|---|---|---|---|
| 1 | Ringkasan | `kpi_monthly` | KPI (rating berbobot, % negatif, NPS-style, total ulasan), tren bulanan + garis rata-rata bergerak 3 bulan |
| 2 | Topik (Topik 1) | `topic_summary`, `topic_month` | Bar topik (share of negative) berwarna rating; heatmap topik × bulan; filter aplikasi/periode |
| 3 | Dampak update (Topik 2) | `version_stats`, `version_window` | Rating per versi (sumbu waktu = `first_seen`), diagram sebelum vs sesudah, tandai `enough_data` dan `has_overlapping_release` |
| 4 | Benchmark (Topik 3) | `benchmark`, `topic_summary`, `feature_matrix` | Bar rating & % negatif per aplikasi; heatmap topik × aplikasi (mention rate); matriks fitur; reply rate & median waktu balas |
| 5 | Prioritas (Topik 4) | `priority_topic` | Scatter frekuensi × keparahan (ukuran = keterlibatan), tabel peringkat + tren 90 hari, kolom RICE dan user story |

## 5. Praktik tampilan
- Satu pesan per halaman; judul berupa kesimpulan ("Login & OTP menyumbang X% keluhan"), bukan label teknis.
- Maksimal 5–6 warna; merah hanya untuk hal negatif. Beri anotasi pada peristiwa/rilis penting.
- Tooltip: tampilkan n (jumlah ulasan) agar pembaca tahu seberapa kuat angkanya; sembunyikan nilai bila n kecil.
- Footer: sumber (Google Play, periode, tanggal ambil data), catatan "bukan data internal", dan batasan singkat.
- Uji di layar laptop dan ponsel (Device layouts).

## 6. Sebelum publikasi
- Pastikan tidak ada app_key `demo_*` di data.
- Hanya data agregat; matikan opsi **Allow download** bila memungkinkan.
- Buat versi ringkas (1 halaman) sebagai tangkapan layar untuk README/CV.
