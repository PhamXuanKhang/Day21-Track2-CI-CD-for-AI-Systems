# Báo Cáo Lab Day 21 — CI/CD cho AI Systems

**Sinh viên:** Phạm Xuân Khang  
**Course:** AIInAction – VinUni  

---

## 1. Siêu Tham Số Đã Chọn (Kết Quả Bước 1)

Ba thí nghiệm được chạy với các siêu tham số khác nhau, theo dõi qua MLflow:

| Thí nghiệm | n_estimators | max_depth | min_samples_split | Accuracy | F1-score |
|:-----------:|:------------:|:---------:|:-----------------:|:--------:|:--------:|
| 1 (baseline) | 50 | 3 | 2 | 0.5580 | 0.5185 |
| 2 | 100 | 5 | 2 | 0.5640 | 0.5534 |
| 3 (tốt nhất) | 200 | 10 | 5 | **0.6440** | **0.6417** |

**Bộ siêu tham số được chọn:** `n_estimators=200`, `max_depth=20`, `min_samples_split=2`

**Lý do chọn:**
- Tăng `n_estimators` từ 50 → 200 cải thiện accuracy rõ rệt (+8.6%) nhờ ensemble lớn hơn giảm variance.
- Tăng `max_depth` cho phép mô hình học các tương tác phi tuyến giữa 12 đặc trưng hóa học của rượu.
- Tập dữ liệu Wine Quality có phân phối nhãn mất cân bằng (class 1 chiếm ~44%), nên cần cây sâu hơn để phân biệt class thiểu số.

**So sánh accuracy theo lượng dữ liệu (Bước 2 vs Bước 3):**

| Giai đoạn | Tập huấn luyện | Accuracy | F1-score |
|:----------:|:--------------:|:--------:|:--------:|
| Bước 2 | train_phase1 (2.998 mẫu) | 0.6440 | 0.6417 |
| Bước 3 | phase1 + phase2 (5.996 mẫu) | *(xem artifact pipeline)* | *(xem artifact pipeline)* |

---

## 2. Khó Khăn Gặp Phải và Cách Giải Quyết

**Khó khăn 1 — Eval gate bị chặn với phase1 data**

Với 2.998 mẫu huấn luyện, mô hình chỉ đạt accuracy 0.644 < 0.70. Ngưỡng không thể vượt chỉ bằng tuning siêu tham số do dataset Wine Quality có nhiễu cao và phân phối nhãn lệch. Giải pháp: thực hiện Bước 3 — ghép `train_phase2.csv` để tăng lên 5.996 mẫu, kích hoạt pipeline tự động qua DVC + git push.

**Khó khăn 2 — Workflow trigger sai branch**

Pipeline ban đầu cấu hình trigger trên `main` nhưng repo dùng branch `master`. Giải pháp: sửa `branches: [main]` thành `branches: [master]` trong `mlops.yml`.

**Khó khăn 3 — SSH key có passphrase**

`VM_SSH_KEY` secret được tạo với passphrase, khiến `appleboy/ssh-action` không thể xác thực tự động. Giải pháp: tạo lại key với `-N ""` (passphrase rỗng), thêm public key mới vào VM, cập nhật secret.

**Khó khăn 4 — DVC connection string bị cắt ngắn**

File `.dvc/config.local` chỉ lưu một phần connection string (thiếu `AccountKey`), khiến `dvc push` thất bại. Giải pháp: lấy lại connection string đầy đủ qua `az storage account show-connection-string` và ghi đè bằng `dvc remote modify --local`.
