# Kamus data

## Tabel
| Tabel | Isi |
|---|---|
| `ref.app` | Aplikasi yang dianalisis (`role`: focus = Daya Auto, peer = pembanding) |
| `ref.app_snapshot` | Riwayat metadata publik Play Store (install, skor toko, versi) |
| `ref.topic` | Taksonomi topik + label tampilan + `is_issue` |
| `ref.setting` | Pengaturan: model topik aktif, bobot skor prioritas |
| `ref.event` | Peristiwa (rilis, redesain, gangguan) dengan sumber |
| `ref.feature_audit` | Hasil audit fitur manual per aplikasi |
| `ref.rice_input` | Input RICE (asumsi kamu) per topik |
| `raw.playstore_review` | Ulasan mentah (tanpa nama pengguna) |
| `clean.review` | Ulasan bersih: `text_clean`, `text_norm`, `has_text`, `lang_flag`, `is_dup_long` |
| `nlp.review_topic` | Topik per ulasan (multi-label; `is_primary` = topik utama) |
| `nlp.review_label` | Sentimen dari teks (opsional) |
| `nlp.gold_label` | Label manual untuk evaluasi |
| `ops.scrape_log` | Riwayat pengambilan data |

## View (sumber file Tableau)
| File ekspor | View | Grain | Kolom penting |
|---|---|---|---|
| `kpi_monthly.csv` | `mart.v_monthly_kpi` | aplikasi × bulan | `n_reviews`, `avg_rating`, `pct_negative`, `pct_positive`, `nps_style`, `pct_replied`, `pct_negative_replied`, `median_reply_hours` |
| `topic_month.csv` | `mart.v_topic_month` | aplikasi × bulan × topik | `n_mentions`, `n_negative_mentions`, `mention_rate_pct`, `avg_rating` |
| `topic_summary.csv` | `mart.v_topic_summary` | aplikasi × topik | `mention_rate_pct`, `share_of_negative_pct`, `avg_rating`, `avg_thumbs_up` |
| `benchmark.csv` | `mart.v_benchmark` | aplikasi | rating, % negatif, reply rate, install, skor toko |
| `version_stats.csv` | `mart.v_version_stats` | aplikasi × versi | `n_reviews`, `first_seen`, `avg_rating`, `pct_negative`, `enough_data` |
| `version_window.csv` | `mart.v_version_window` | aplikasi × versi (≥ 30 ulasan) | `rollout_proxy_date`, `*_before/_after`, `delta_rating`, `delta_pct_negative`, `has_overlapping_release` |
| `priority_topic.csv` | `mart.v_priority_topic` | aplikasi × topik keluhan | `freq_pct`, `severity`, `engagement`, `freq_n/sev_n/eng_n`, `priority_score`, `priority_rank`, `trend_pct`, `rice_score` |
| `event_window.csv` | `mart.v_event_window` | peristiwa × aplikasi | `*_before/_after` (30 hari) |
| `feature_matrix.csv` | `mart.v_feature_matrix` | aplikasi × fitur | `available`, `notes` |
| `review_level.csv` (opsional) | `mart.v_review_export` | satu ulasan, tanpa teks | `review_date`, `rating`, `sentiment`, `app_version`, `primary_topic` |

## Definisi penting
- **Sentimen** (utama): rating 1–2 = negative, 3 = neutral, 4–5 = positive.
- **has_text**: teks ternormalisasi ≥ 3 karakter. Analisis topik hanya memakai ulasan `has_text`.
- **is_dup_long**: teks ≥ 6 kata yang sama persis dalam satu aplikasi (kemunculan ke-2 dst.); dikeluarkan dari semua view.
- **rollout_proxy_date**: tanggal ulasan ke-5 dari suatu versi (proksi tanggal rilis).
- **Waktu**: dikonversi ke WIB (Asia/Jakarta) di view; zona asal dari library diasumsikan UTC.
