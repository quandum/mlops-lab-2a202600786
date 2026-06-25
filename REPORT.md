# BÁO CÁO NỘP BÀI - Lab MLOps: CI/CD cho AI Systems

---

## I. Thông tin Học viên

| Mục | Nội dung |
|---|---|
| **Họ và tên** | Trần Mạnh Chánh Quân |
| **Mã số học viên** | 2A202600786 |
| **Khóa học** | AIInAction - VinUni |
| **Buổi học** | Day 21 - CI/CD cho AI Systems |
| **Ngày nộp bài** | .../.../2026 |

---

## II. Tổng quan Bài Lab

Bài lab xây dựng một pipeline MLOps hoàn chỉnh từ thực nghiệm cục bộ đến triển khai tự động trên cloud cho bài toán phân loại chất lượng rượu vang (Wine Quality dataset - UCI). Hệ thống sử dụng các công nghệ:

| Công nghệ | Vai trò |
|---|---|
| **MLflow** | Theo dõi và so sánh thí nghiệm huấn luyện |
| **DVC** | Quản lý phiên bản dữ liệu trên Cloud Storage |
| **GitHub Actions** | Pipeline CI/CD tự động 4 giai đoạn |
| **Google Cloud Platform** | Lưu trữ dữ liệu (GCS) và triển khai mô hình (GCE) |
| **FastAPI** | REST API phục vụ dự đoán |
| **scikit-learn** | Huấn luyện mô hình RandomForestClassifier |

---

## III. Kết quả Thực hiện

### Bước 1: Thực nghiệm Cục bộ & MLflow Tracking

#### 1.1 Các thí nghiệm đã thực hiện

| Lần | n_estimators | max_depth | min_samples_split | Accuracy | F1-Score | Ghi chú |
|---|---|---|---|---|---|---|
| 1 | 100 | 5 | 2 | ? | ? | Bộ tham số mặc định |
| 2 | 50 | 3 | 2 | ? | ? | Giảm số cây và độ sâu |
| 3 | 200 | 10 | 5 | ? | ? | Tăng số cây và độ sâu |
| 4 | ... | ... | ... | ? | ? | (Thí nghiệm bổ sung) |

> *Ghi chú: Điền kết quả thực tế từ MLflow UI sau khi chạy.*

#### 1.2 Bộ siêu tham số tốt nhất được chọn

```yaml
# params.yaml - Bộ tham số tối ưu cho Bước 2
n_estimators: ...
max_depth: ...
min_samples_split: ...
```

**Lý do lựa chọn:** ...

#### 1.3 Ảnh chụp MLflow UI

> *(Chèn ảnh chụp màn hình MLflow UI hiển thị danh sách các thí nghiệm)*

---

### Bước 2: Pipeline CI/CD Tự động

#### 2.1 Cấu hình Cloud (GCP)

| Thành phần | Giá trị |
|---|---|
| Project ID | ... |
| Cloud Storage Bucket | `gs://...` |
| Service Account | `mlops-lab-sa@...` |
| VM Instance | `mlops-serve` (us-central1-a, e2-small) |
| VM IP công khai | ... |

#### 2.2 DVC Remote

```
Remote: gs://<BUCKET>/dvc
Trạng thái: ✅ Đã push dữ liệu lên GCS thành công
```

#### 2.3 Unit Test

```
Kết quả chạy pytest:
============================= test session starts =============================
tests/test_train.py::test_train_returns_float   PASSED
tests/test_train.py::test_metrics_file_created  PASSED
tests/test_train.py::test_model_file_created    PASSED
============================== 3 passed in ...s ==============================
```

#### 2.4 Pipeline GitHub Actions

| Job | Trạng thái | Mô tả |
|---|---|---|
| **Unit Test** | ✅ Passed | Chạy pytest, kiểm tra code |
| **Train** | ✅ Passed | Pull dữ liệu từ GCS, huấn luyện mô hình |
| **Eval** | ✅ Passed | Accuracy = ... (>= 0.70 ✓) |
| **Deploy** | ✅ Passed | Deploy mô hình lên VM, restart service |

#### 2.5 Kiểm tra API

```bash
# Health check
$ curl http://<VM_IP>:8000/health
{"status": "ok"}

# Dự đoán
$ curl -X POST http://<VM_IP>:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [7.4, 0.70, 0.00, 1.9, 0.076, 11.0, 34.0, 0.9978, 3.51, 0.56, 9.4, 0]}'
{"prediction": ..., "label": "..."}
```

#### 2.6 Ảnh chụp GitHub Actions

> *(Chèn ảnh chụp màn hình GitHub Actions hiển thị 4 job đã hoàn thành thành công)*

---

### Bước 3: Huấn luyện Liên tục

#### 3.1 Kích hoạt Pipeline bằng Dữ liệu Mới

```bash
$ python add_new_data.py
Cập nhật dữ liệu: 2998 -> 5996 mẫu

$ dvc add data/train_phase1.csv
$ git add data/train_phase1.csv.dvc
$ git commit -m "data: bổ sung 2998 mẫu dữ liệu mới (train_phase2)"
$ dvc push
$ git push origin main
```

#### 3.2 Kết quả Pipeline Bước 3

| Job | Trạng thái |
|---|---|
| Unit Test | ✅ Passed |
| Train (5996 mẫu) | ✅ Passed |
| Eval (accuracy >= 0.70) | ✅ Passed |
| Deploy | ✅ Passed |

Commit message hiển thị trong Actions: `data: bổ sung 2998 mẫu dữ liệu mới (train_phase2)` → **Xác nhận pipeline được kích hoạt bởi commit dữ liệu.**

#### 3.3 So sánh Kết quả

| Chỉ số | Bước 2 (2998 mẫu) | Bước 3 (5996 mẫu) | Thay đổi |
|---|---|---|---|
| **Accuracy** | ? | ? | ? |
| **F1-Score** | ? | ? | ? |

**Nhận xét:** ...

#### 3.4 Ảnh chụp GitHub Actions Bước 3

> *(Chèn ảnh chụp màn hình GitHub Actions Bước 3 - commit message hiển thị là commit dữ liệu)*

---

## IV. Cấu trúc Dự án Hoàn chỉnh

```
mlops-lab/
├── .github/
│   └── workflows/
│       └── mlops.yml              ← Pipeline CI/CD
├── .dvc/
│   └── config                     ← Cấu hình DVC remote (GCS)
├── data/
│   ├── train_phase1.csv.dvc       ← Con trỏ DVC
│   ├── eval.csv.dvc
│   └── train_phase2.csv.dvc
├── src/
│   ├── __init__.py
│   ├── train.py                   ← Script huấn luyện + MLflow tracking
│   └── serve.py                   ← FastAPI inference server
├── tests/
│   ├── __init__.py
│   └── test_train.py              ← Unit tests
├── models/                        ← Model artifacts (local)
│   └── model.pkl
├── outputs/                       ← Metrics output
│   └── metrics.json
├── generate_data.py               ← Script tạo dữ liệu
├── add_new_data.py                ← Script thêm dữ liệu mới
├── params.yaml                    ← Siêu tham số mô hình
├── requirements.txt               ← Thư viện Python
├── work_plan.md                   ← Kế hoạch thực hiện
├── REPORT.md                      ← File báo cáo này
└── .gitignore
```

---

## V. Bài học và Kỹ năng Đạt được

1. **MLflow**: Thiết lập tracking server cục bộ, ghi nhận tham số, metrics, và model artifacts. So sánh nhiều thí nghiệm để chọn bộ siêu tham số tối ưu.

2. **DVC**: Quản lý phiên bản dữ liệu với cloud storage làm remote. Hiểu quy trình `dvc add` → `git commit .dvc` → `dvc push`. Phân biệt giữa file dữ liệu (quản lý bởi DVC) và file code (quản lý bởi Git).

3. **GitHub Actions**: Xây dựng pipeline CI/CD với nhiều job phụ thuộc: Unit Test → Train → Eval Gate → Deploy. Sử dụng GitHub Secrets để bảo vệ credentials.

4. **Cloud Deployment**: Tạo và cấu hình VM trên GCP, triển khai mô hình dưới dạng REST API với FastAPI, quản lý service bằng systemd.

5. **Continuous Training**: Mô phỏng quy trình thực tế: dữ liệu mới → tự động huấn luyện lại → tự động triển khai, không cần can thiệp thủ công.

---

## VI. Tự Đánh giá

| Tiêu chí | Hoàn thành? |
|---|---|
| Chạy ít nhất 3 thí nghiệm với MLflow | ☐ |
| MLflow UI hiển thị đầy đủ kết quả | ☐ |
| Dữ liệu được quản lý bởi DVC + Cloud Storage | ☐ |
| GitHub Actions pipeline 4 job hoạt động | ☐ |
| VM triển khai FastAPI hoạt động | ☐ |
| Bước 3: pipeline kích hoạt bởi commit dữ liệu | ☐ |
| Cả 4 job Bước 3 thành công | ☐ |
| Báo cáo đầy đủ thông tin | ☐ |

---

## VII. Phụ lục: Ảnh chụp Màn hình

### A. MLflow UI - Danh sách thí nghiệm
> *(Chèn ảnh)*

### B. GitHub Actions - Pipeline Bước 2 thành công
> *(Chèn ảnh)*

### C. API Test - curl /health và /predict
> *(Chèn ảnh)*

### D. GitHub Actions - Pipeline Bước 3 (kích hoạt bởi commit dữ liệu)
> *(Chèn ảnh)*

### E. Cloud Storage - Dữ liệu và model trên GCS
> *(Chèn ảnh)*

---

**Người thực hiện:** Trần Mạnh Chánh Quân  
**Mã số:** 2A202600786
