# KẾ HOẠCH THỰC HIỆN - Lab MLOps: CI/CD cho AI Systems

## Thông tin Học viên

| Mục | Nội dung |
|---|---|
| **Họ và tên** | Trần Mạnh Chánh Quân |
| **Mã số học viên** | 2A202600786 |
| **Khóa học** | AIInAction - VinUni |
| **Buổi học** | Day 21 - CI/CD cho AI Systems |
| **Ngày thực hiện** | 25/06/2026 |

---

## Tổng quan Dự án

Dự án xây dựng pipeline MLOps hoàn chỉnh cho bài toán phân loại chất lượng rượu vang (Wine Quality - UCI), bao gồm 3 bước chính:

1. **Bước 1**: Thực nghiệm cục bộ với MLflow tracking
2. **Bước 2**: Pipeline CI/CD tự động trên GitHub Actions + DVC + Cloud (GCP)
3. **Bước 3**: Huấn luyện liên tục khi có dữ liệu mới

---

## Sơ đồ Kiến trúc Tổng thể

```
[Máy tính cá nhân]
      │ git push
      ▼
[GitHub Repository]
      │ GitHub Actions tự động kích hoạt
      ▼
[Runner CI/CD]
  ├── Job 1: Unit Test (pytest)
  ├── Job 2: Train (MLflow + DVC pull)
  ├── Job 3: Eval (accuracy >= 0.70?)
  └── Job 4: Deploy → Cloud VM (FastAPI)
      │                    │
  dvc pull/push       POST /predict
      │                    │
      ▼                    ▼
[Cloud Storage]      [Cloud VM]
  data/                mlops-serve:8000
  models/latest/
```

---

## Kế hoạch Chi tiết

---

### GIAI ĐOẠN 0: Chuẩn bị Môi trường (Một lần duy nhất)

| # | Công việc | Công cụ / Lệnh | Ghi chú |
|---|---|---|---|
| 0.1 | Cài đặt Python 3.10+ | `python --version` | Yêu cầu >= 3.10 |
| 0.2 | Cài đặt Git + tạo repo GitHub public | `git --version` | Repo mới, chưa có nội dung |
| 0.3 | Đăng ký tài khoản GCP (dùng gói free trial) | https://cloud.google.com | Có thể dùng AWS hoặc Azure thay thế |
| 0.4 | Cài đặt Google Cloud SDK (`gcloud`) | `gcloud --version` | CLI để tương tác với GCP |
| 0.5 | Clone repo về máy, tạo virtual environment | `python -m venv .venv` + activate | Môi trường ảo Python |
| 0.6 | Cài đặt thư viện Python | `pip install -r requirements.txt` | Các thư viện: mlflow, sklearn, pandas, dvc, fastapi, pytest... |
| 0.7 | Tạo file `.gitignore` | Tạo thủ công | Theo mẫu trong README.md |
| 0.8 | Tải và chia dữ liệu | `python generate_data.py` | Tạo 3 file CSV trong `data/` |

**Kết quả mong đợi:**
```
train_phase1.csv : 2998 mẫu
eval.csv         :  500 mẫu
train_phase2.csv : 2998 mẫu
```

---

### GIAI ĐOẠN 1: Bước 1 - Thực nghiệm Cục bộ & MLflow Tracking

**Mục tiêu:** Chạy ít nhất 3 thí nghiệm với siêu tham số khác nhau, so sánh trên MLflow UI, chọn bộ tham số tốt nhất.

| # | Công việc | File liên quan | Mô tả chi tiết |
|---|---|---|---|
| **1.1** | **Cấu hình MLflow** | `.env` hoặc shell | Thiết lập biến môi trường: `MLFLOW_TRACKING_URI=sqlite:///mlflow.db`, `MLFLOW_ARTIFACT_ROOT=./mlartifacts` |
| **1.2** | **Hoàn thiện `src/train.py`** | `src/train.py` | Điền code vào tất cả vị trí `# TODO` (10 TODO):
| | | | - TODO 1: Đọc `train_phase1.csv` và `eval.csv` bằng `pd.read_csv()`
| | | | - TODO 2: Tách X (features) và y (target)
| | | | - TODO 3: `mlflow.log_params(params)`
| | | | - TODO 4: Khởi tạo `RandomForestClassifier(**params, random_state=42)` và `model.fit()`
| | | | - TODO 5: Dự đoán, tính `accuracy_score` và `f1_score`
| | | | - TODO 6: `mlflow.log_metric()` cho accuracy và f1, `mlflow.sklearn.log_model()`
| | | | - TODO 7: `print()` kết quả
| | | | - TODO 8: Lưu `outputs/metrics.json`
| | | | - TODO 9: Lưu `models/model.pkl`
| | | | - TODO 10: `return acc`
| **1.3** | **Chạy thí nghiệm lần 1** | `params.yaml` | `n_estimators: 100, max_depth: 5, min_samples_split: 2` → `python src/train.py` |
| **1.4** | **Chạy thí nghiệm lần 2** | `params.yaml` | `n_estimators: 50, max_depth: 3, min_samples_split: 2` → `python src/train.py` |
| **1.5** | **Chạy thí nghiệm lần 3** | `params.yaml` | `n_estimators: 200, max_depth: 10, min_samples_split: 5` → `python src/train.py` |
| **1.6** | **Chạy thêm 1-2 thí nghiệm (tùy chọn)** | `params.yaml` | Thử các tổ hợp khác để có dữ liệu so sánh phong phú hơn |
| **1.7** | **Phân tích kết quả** | MLflow UI | `mlflow ui --backend-store-uri sqlite:///mlflow.db` → mở http://127.0.0.1:5000 |
| **1.8** | **Chọn bộ siêu tham số tốt nhất** | `params.yaml` | Dựa trên accuracy và f1_score cao nhất, cập nhật `params.yaml` |

**Sản phẩm đầu ra Bước 1:**
- [x] File `src/train.py` hoàn chỉnh
- [x] File `params.yaml` với bộ tham số tốt nhất
- [x] MLflow UI hiển thị 3+ thí nghiệm
- [x] File `outputs/metrics.json` và `models/model.pkl` được tạo

---

### GIAI ĐOẠN 2: Bước 2 - Pipeline CI/CD Tự động

**Mục tiêu:** Push code → GitHub Actions tự động: Unit Test → Train → Eval (≥0.70) → Deploy lên VM.

#### 2A - Thiết lập Cloud (GCP)

| # | Công việc | Lệnh / Thao tác | Ghi chú |
|---|---|---|---|
| 2A.1 | Tạo GCS Bucket | `gsutil mb -p $PROJECT -l us-central1 gs://$BUCKET` | Tên bucket phải unique toàn cầu |
| 2A.2 | Enable Storage API | `gcloud services enable storage.googleapis.com` | |
| 2A.3 | Tạo Service Account | `gcloud iam service-accounts create mlops-lab-sa` | |
| 2A.4 | Cấp quyền objectAdmin trên bucket | `gsutil iam ch serviceAccount:...:roles/storage.objectAdmin gs://$BUCKET` | Nguyên tắc quyền tối thiểu |
| 2A.5 | Xuất key JSON | `gcloud iam service-accounts keys create sa-key.json` | **Không commit file này!** |
| 2A.6 | Tạo VM (GCE) | `gcloud compute instances create mlops-serve --zone=us-central1-a --machine-type=e2-small` | Ubuntu 22.04 LTS |
| 2A.7 | Mở firewall port 8000 | `gcloud compute firewall-rules create allow-mlops-serve --allow=tcp:8000` | Cho phép gọi API |
| 2A.8 | Lấy IP công khai của VM | `gcloud compute instances describe mlops-serve` | Lưu lại để dùng sau |
| 2A.9 | SSH vào VM, cài đặt thư viện | `gcloud compute ssh mlops-serve` → `sudo apt update && sudo apt install -y python3-pip` → `pip3 install fastapi uvicorn scikit-learn joblib google-cloud-storage` | |
| 2A.10 | Copy key lên VM | `gcloud compute scp sa-key.json mlops-serve:~/` | Để VM có quyền truy cập GCS |

#### 2B - Thiết lập DVC

| # | Công việc | Lệnh | Ghi chú |
|---|---|---|---|
| 2B.1 | Khởi tạo DVC | `dvc init` | |
| 2B.2 | Thêm DVC remote (GCS) | `dvc remote add -d myremote gs://$BUCKET/dvc` | |
| 2B.3 | Cấu hình credential path | `dvc remote modify myremote credentialpath sa-key.json` | |
| 2B.4 | Theo dõi các file dữ liệu | `dvc add data/train_phase1.csv`, `dvc add data/eval.csv`, `dvc add data/train_phase2.csv` | Tạo file `.dvc` |
| 2B.5 | Commit file `.dvc` vào git | `git add data/*.dvc .gitignore .dvc/config` → `git commit -m "feat: track datasets with DVC"` | |
| 2B.6 | Đẩy dữ liệu lên GCS | `dvc push` | Xác nhận trên GCS Console |

#### 2C - Hoàn thiện Code

| # | Công việc | File | Mô tả |
|---|---|---|---|
| 2C.1 | **Hoàn thiện `tests/test_train.py`** | `tests/test_train.py` | Điền 9 TODO:
| | | | - `_make_temp_data()`: tạo dataset giả với numpy
| | | | - `test_train_returns_float()`: kiểm tra train() trả về float [0,1]
| | | | - `test_metrics_file_created()`: kiểm tra file `outputs/metrics.json`
| | | | - `test_model_file_created()`: kiểm tra file `models/model.pkl`
| 2C.2 | **Hoàn thiện `src/serve.py`** | `src/serve.py` | Điền 8 TODO:
| | | | - `download_model()`: tải model.pkl từ GCS
| | | | - `GET /health`: trả về `{"status": "ok"}`
| | | | - `POST /predict`: nhận 12 features, trả về `{"prediction": int, "label": str}`
| 2C.3 | Chạy unit test cục bộ | `pytest tests/ -v` | Đảm bảo tất cả test pass trước khi push |

#### 2D - Thiết lập GitHub Actions

| # | Công việc | Mô tả |
|---|---|---|
| 2D.1 | Tạo thư mục `.github/workflows/` | |
| 2D.2 | **Viết `mlops.yml`** | File workflow với 4 job: Unit Test → Train → Eval → Deploy |
| | | - Trigger: push lên main, thay đổi `data/**.dvc`, `src/**.py`, `params.yaml`
| | | - Job 1 `unit-test`: `pip install -r requirements.txt` → `pytest tests/`
| | | - Job 2 `train`: `dvc pull` → `python src/train.py` → upload model lên GCS
| | | - Job 3 `eval`: Đọc `outputs/metrics.json`, kiểm tra accuracy >= 0.70
| | | - Job 4 `deploy`: SSH vào VM, restart service với model mới
| 2D.3 | **Cấu hình GitHub Secrets** | Trên repo GitHub → Settings → Secrets and variables → Actions:
| | | - `GCP_SA_KEY`: nội dung file `sa-key.json`
| | | - `GCS_BUCKET`: tên bucket
| | | - `VM_IP`: IP công khai của VM
| | | - `VM_SSH_KEY`: private key để SSH vào VM
| 2D.4 | **Viết systemd service trên VM** | Tạo file `/etc/systemd/system/mlops-serve.service` để tự động chạy FastAPI
| 2D.5 | Push code lên GitHub | `git push origin main` → theo dõi pipeline trên tab Actions |

**Sản phẩm đầu ra Bước 2:**
- [x] DVC đã track dữ liệu, dữ liệu đã có trên GCS
- [x] `tests/test_train.py` hoàn chỉnh, tất cả test pass
- [x] `src/serve.py` hoàn chỉnh
- [x] `.github/workflows/mlops.yml` hoạt động
- [x] VM chạy FastAPI, endpoint `/health` và `/predict` hoạt động
- [x] Pipeline CI/CD 4 job chạy thành công

---

### GIAI ĐOẠN 3: Bước 3 - Huấn luyện Liên tục

**Mục tiêu:** Mô phỏng thêm dữ liệu mới → push → pipeline tự động huấn luyện lại & triển khai.

| # | Công việc | Lệnh / Thao tác | Ghi chú |
|---|---|---|---|
| 3.1 | Thêm dữ liệu mới | `python add_new_data.py` | Ghép `train_phase2.csv` vào `train_phase1.csv` → 5996 mẫu |
| 3.2 | Cập nhật DVC | `dvc add data/train_phase1.csv` | File `.dvc` sẽ thay đổi hash |
| 3.3 | Commit file `.dvc` | `git add data/train_phase1.csv.dvc` → `git commit -m "data: bổ sung 2998 mẫu dữ liệu mới (train_phase2)"` | **QUAN TRỌNG**: commit file `.dvc`, KHÔNG phải file CSV |
| 3.4 | Đẩy dữ liệu mới lên GCS | `dvc push` | Phải làm **trước** `git push` |
| 3.5 | Push code lên GitHub | `git push origin main` | GitHub Actions tự động kích hoạt |
| 3.6 | Theo dõi pipeline | Tab Actions trên GitHub | Xác nhận commit message hiển thị đúng |
| 3.7 | Xác nhận triển khai | `curl http://$VM_IP:8000/health` → `curl -X POST http://$VM_IP:8000/predict ...` | Mô hình mới đang phục vụ |
| 3.8 | So sánh kết quả | Điền bảng so sánh accuracy/f1 Bước 2 vs Bước 3 | |

**Sản phẩm đầu ra Bước 3:**
- [x] Pipeline được kích hoạt bởi commit dữ liệu (không phải commit code)
- [x] Cả 4 job (Unit Test, Train, Eval, Deploy) hoàn thành thành công
- [x] Mô hình mới (huấn luyện trên 5996 mẫu) đang chạy trên VM
- [x] Bảng so sánh kết quả Bước 2 vs Bước 3

---

## Danh sách File cần Hoàn thiện (Code)

| File | Số lượng TODO | Trạng thái |
|---|---|---|
| `src/train.py` | 10 TODO | ⬜ Chưa hoàn thiện |
| `tests/test_train.py` | 9 TODO | ⬜ Chưa hoàn thiện |
| `src/serve.py` | 8 TODO | ⬜ Chưa hoàn thiện |
| `.github/workflows/mlops.yml` | Tạo mới | ⬜ Chưa tạo |
| `.gitignore` | Tạo mới | ⬜ Chưa tạo |
| `params.yaml` | Đã có sẵn | ✅ Hoàn thiện |

---

## Thứ tự Thực hiện Khuyến nghị

```
Ngày 1 (2-3 giờ):
  ├── Giai đoạn 0: Chuẩn bị môi trường
  ├── Giai đoạn 1: Hoàn thiện src/train.py + chạy 3+ thí nghiệm
  └── Phân tích MLflow UI, chọn bộ tham số tốt nhất

Ngày 2 (4-5 giờ):
  ├── Giai đoạn 2A: Thiết lập GCP (bucket, service account, VM)
  ├── Giai đoạn 2B: Thiết lập DVC
  ├── Giai đoạn 2C: Hoàn thiện test_train.py + serve.py
  └── Giai đoạn 2D: Viết mlops.yml + GitHub Secrets

Ngày 3 (1-2 giờ):
  ├── Giai đoạn 3: Chạy add_new_data.py
  ├── Push DVC + Git
  ├── Theo dõi pipeline
  └── Xác nhận & so sánh kết quả

Ngày 4: Viết báo cáo REPORT.md + nộp bài
```

---

## Kiểm tra Cuối cùng (Checklist Nộp bài)

- [ ] Tất cả file TODO đã được hoàn thiện
- [ ] `pytest tests/ -v` → tất cả test pass
- [ ] MLflow UI hiển thị ít nhất 3 thí nghiệm
- [ ] Dữ liệu đã có trên Cloud Storage
- [ ] GitHub Actions pipeline chạy thành công (4 job xanh)
- [ ] VM đang chạy, endpoint `/health` và `/predict` hoạt động
- [ ] Bước 3: pipeline được kích hoạt bởi commit dữ liệu
- [ ] Chụp màn hình: MLflow UI, GitHub Actions thành công, API response
- [ ] `REPORT.md` hoàn chỉnh
- [ ] `sa-key.json` KHÔNG bị commit vào repo
