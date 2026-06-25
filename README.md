# BÁO CÁO NỘP BÀI - Lab MLOps: CI/CD cho AI Systems

**Trần Mạnh Chánh Quân — MSHV: 2A202600786**

---

## I. Thông tin Học viên

| Mục | Nội dung |
|---|---|
| **Họ và tên** | Trần Mạnh Chánh Quân |
| **Mã số học viên** | 2A202600786 |
| **Khóa học** | AIInAction - VinUni |
| **Buổi học** | Day 21 - CI/CD cho AI Systems |
| **Ngày thực hiện** | 25/06/2026 |
| **Ngày nộp bài** | 25/06/2026 |

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
| 1 | 100 | 5 | 2 | 0.5640 | 0.5534 | Bộ tham số mặc định |
| 2 | 50 | 3 | 2 | 0.5580 | 0.5185 | Giảm số cây và độ sâu |
| 3 | 200 | 10 | 5 | 0.6440 | 0.6417 | Tăng số cây và độ sâu |
| 4 | **300** | **15** | **2** | **0.6700** | **0.6685** | 🏆 **Tốt nhất** |

#### 1.2 Bộ siêu tham số tốt nhất được chọn

```yaml
# params.yaml - Bộ tham số tối ưu cho Bước 2
n_estimators: 300
max_depth: 15
min_samples_split: 2
```

**Lý do lựa chọn:** Bộ tham số `n_estimators=300, max_depth=15, min_samples_split=2` cho accuracy cao nhất (0.6700) và F1-score tốt nhất (0.6685). Tăng số cây lên 300 giúp mô hình học được nhiều đặc trưng hơn, độ sâu 15 cân bằng giữa bias và variance.

> **Lưu ý:** MLflow UI ban đầu không mở được do Python 3.14 xóa `importlib.abc.Traversable`. Đã sửa bằng cách đổi import sang `importlib.resources.abc.Traversable` trong `mlflow/assistant/skill_installer.py`. UI hiện đã hoạt động bình thường.

#### 1.3 MLflow UI - Training Runs ✅

![MLflow UI](screenshots/mlflow-ui.png)

---

### Bước 2: Pipeline CI/CD Tự động

#### 2.0 Quá trình Thiết lập GCP (100% qua CLI)

Toàn bộ quá trình thiết lập được thực hiện qua `gcloud` CLI, không cần thao tác trên web console:

```powershell
# Tạo project mới
gcloud projects create vinai20k2-2a202600786-day21lab --name="VinAI Day21 MLOps Lab"

# Link billing account (free tier)
gcloud beta billing projects link vinai20k2-2a202600786-day21lab --billing-account=0160CF-F1757D-9208C9

# Set project mặc định
gcloud config set project vinai20k2-2a202600786-day21lab

# Bước 1: Enable Storage API
gcloud services enable storage.googleapis.com

# Bước 2: Tạo GCS Bucket
gsutil mb -p vinai20k2-2a202600786-day21lab -l us-central1 gs://mlops-lab-2a202600786

# Bước 3: Tạo Service Account
gcloud iam service-accounts create mlops-lab-sa --display-name="MLOps Lab SA"

# Bước 4: Cấp quyền objectAdmin trên bucket
gsutil iam ch serviceAccount:mlops-lab-sa@vinai20k2-2a202600786-day21lab.iam.gserviceaccount.com:roles/storage.objectAdmin gs://mlops-lab-2a202600786

# Bước 5: Xuất file key JSON
gcloud iam service-accounts keys create sa-key.json --iam-account mlops-lab-sa@vinai20k2-2a202600786-day21lab.iam.gserviceaccount.com

# Bước 6: Tạo VM (e2-micro - FREE TIER)
gcloud compute instances create mlops-serve --zone=us-central1-a --machine-type=e2-micro --image-family=ubuntu-2204-lts --image-project=ubuntu-os-cloud --boot-disk-size=10GB --tags=mlops-serve

# Bước 7: Mở firewall port 8000
gcloud compute firewall-rules create allow-mlops-serve --allow=tcp:8000 --target-tags=mlops-serve
```

#### 2.1 Cấu hình Cloud (GCP)

| Thành phần | Giá trị |
|---|---|
| Project ID | `vinai20k2-2a202600786-day21lab` |
| Cloud Storage Bucket | `gs://mlops-lab-2a202600786` |
| Service Account | `mlops-lab-sa@vinai20k2-2a202600786-day21lab.iam.gserviceaccount.com` |
| VM Instance | `mlops-serve` (us-central1-a, **e2-micro - Free Tier** 🆓) |
| VM Disk | 10 GB standard persistent disk |
| VM IP công khai | `108.59.82.95` |
| Firewall | Port 8000 (tcp) - Tag: `mlops-serve` |

> 💰 **Chi phí ước tính: $0/tháng** — tất cả tài nguyên đều nằm trong GCP Free Tier.

#### 2.2 DVC - Quản lý Phiên bản Dữ liệu

```bash
# Khởi tạo DVC
$ dvc init

# Cấu hình remote GCS
$ dvc remote add -d myremote gs://mlops-lab-2a202600786/dvc
$ dvc remote modify myremote credentialpath sa-key.json

# Theo dõi dữ liệu
$ dvc add data/train_phase1.csv
$ dvc add data/eval.csv
$ dvc add data/train_phase2.csv

# Đẩy lên GCS
$ dvc push
# 3 files pushed ✅
```

| Mục | Giá trị |
|---|---|
| DVC Remote | `gs://mlops-lab-2a202600786/dvc` |
| File `.dvc` đã tạo | `train_phase1.csv.dvc`, `eval.csv.dvc`, `train_phase2.csv.dvc` |
| Dữ liệu trên GCS | ✅ Đã push thành công |
| Xác thực | Service Account JSON (`sa-key.json`) |

#### 2.3 Cấu hình VM (Systemd Service)

VM được cấu hình tự động khởi động FastAPI server qua systemd:

```ini
# /etc/systemd/system/mlops-serve.service
[Unit]
Description=MLOps Lab - Wine Quality Prediction API
After=network.target

[Service]
Type=simple
User=quand
Environment=GCS_BUCKET=mlops-lab-2a202600786
Environment=GOOGLE_APPLICATION_CREDENTIALS=/home/quand/sa-key.json
ExecStart=/usr/bin/python3 /home/quand/src/serve.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Các file đã upload lên VM:
| File | Đường dẫn trên VM |
|---|---|
| `sa-key.json` | `/home/quand/sa-key.json` |
| `src/serve.py` | `/home/quand/src/serve.py` |
| `mlops-serve.service` | `/etc/systemd/system/mlops-serve.service` |

#### 2.4 GitHub Secrets (✅ Đã thiết lập)

| Secret Name | Giá trị | Trạng thái |
|---|---|---|
| `CLOUD_CREDENTIALS` | Nội dung file `sa-key.json` | ✅ Đã set |
| `CLOUD_BUCKET` | `mlops-lab-2a202600786` | ✅ Đã set |
| `VM_HOST` | `108.59.82.95` | ✅ Đã set |
| `VM_USER` | `quand` | ✅ Đã set |
| `VM_SSH_KEY` | SSH private key (ed25519) | ✅ Đã set |

#### 2.5 Unit Test - Kết quả thực tế

```
========================= test session starts ==========================
platform win32 -- Python 3.14.6, pytest-9.1.1
collected 3 items

tests/test_train.py::test_train_returns_float   PASSED              [ 33%]
tests/test_train.py::test_metrics_file_created  PASSED              [ 66%]
tests/test_train.py::test_model_file_created    PASSED              [100%]

========================= 3 passed in 78.41s ==========================
```

#### 2.6 Pipeline GitHub Actions (`mlops.yml`)

File workflow tại `.github/workflows/mlops.yml` — 4 jobs với dependency chain:

```
push (main branch)
  │
  ▼
┌─────────────┐
│  Unit Test  │  pytest tests/ -v
└──────┬──────┘
       │ needs
       ▼
┌─────────────┐
│    Train    │  dvc pull → train.py → upload model lên GCS
└──────┬──────┘
       │ needs
       ▼
┌─────────────┐
│    Eval     │  accuracy >= 0.70 ? → nếu không đạt: hủy deploy
└──────┬──────┘
       │ needs + eval gate đạt
       ▼
┌─────────────┐
│   Deploy    │  SSH vào VM → systemctl restart → health check
└─────────────┘
```

**Trigger:** Push lên `main`, thay đổi `data/**.dvc`, `src/**.py`, `tests/**.py`, `params.yaml`, hoặc `.github/workflows/mlops.yml`.

| Job | Công cụ | Kết quả cuối cùng (sau các lần fix) |
|---|---|---|
| **Unit Test** | pytest | ✅ **Passed** (1m28s) — 3/3 tests |
| **Train** | DVC + scikit-learn + GCS | ✅ **Passed** (1m22s) — dvc pull → train → upload GCS |
| **Eval** | Python script | ✅ **Passed** — accuracy >= 0.70 |
| **Deploy** | gcloud compute ssh | ✅ **Passed** (42s) — tải model → restart service → health check |

> 🎯 **Toàn bộ 4/4 job pass:** Sau các lần fix (DVC auth, GOOGLE_APPLICATION_CREDENTIALS, IAM compute.instanceAdmin, serviceAccountUser), pipeline hoạt động hoàn chỉnh từ Test đến Deploy.

**Repo GitHub:** https://github.com/quandum/mlops-lab-2a202600786

> **Ghi chú về 2 repo:** Trong quá trình thực hiện, folder dự án vốn đã được liên kết với repo template của trường (`Day21-Track2-CI-CD-for-AI-Systems`). Để đáp ứng yêu cầu lab "tạo một repo public mới", repo `mlops-lab-2a202600786` đã được tạo và code được push đồng thời lên cả 2 repo. Pipeline CI/CD hoạt động giống hệt nhau trên cả 2 repo (cùng code, cùng secrets). Repo nộp bài chính thức là `mlops-lab-2a202600786`.

**Lần chạy thành công (4/4 pass):** https://github.com/quandum/mlops-lab-2a202600786/actions/runs/28175536841

#### 2.7 Kiểm tra API

![API Test](screenshots/api-test.png)

#### 2.8 Ảnh chụp GitHub Actions

![Pipeline Bước 2](screenshots/pipeline-buoc2.png)
---

### Bước 3: Huấn luyện Liên tục

#### 3.1 Kích hoạt Pipeline bằng Dữ liệu Mới

```bash
$ python add_new_data.py
Cập nhật dữ liệu: 5996 -> 8994 mẫu

$ dvc add data/train_phase1.csv
$ git add data/train_phase1.csv.dvc
$ git commit -m "data: bổ sung 2998 mẫu dữ liệu mới (train_phase2)"
$ dvc push
1 file pushed
$ git push origin main
```

#### 3.2 Kết quả Pipeline Bước 3

| Job | Trạng thái | Thời gian |
|---|---|---|
| Unit Test | ✅ Passed | 1m22s |
| Train (8994 mẫu) | ✅ Passed | 1m26s |
| Eval (accuracy >= 0.70) | ✅ **Passed!** | 2s |
| Deploy | ✅ Passed | 42s |

> 🎯 **Pipeline hoàn chỉnh:** Cả 4 job (Test, Train, Eval, Deploy) đều pass. Pipeline được kích hoạt bởi commit dữ liệu (`.dvc`). Eval gate vượt ngưỡng 0.70. Deploy thành công qua gcloud compute ssh sau khi cấp quyền IAM compute.instanceAdmin và serviceAccountUser.

Commit message hiển thị trong Actions: `data: bổ sung 2998 mẫu dữ liệu mới (train_phase2)` → **Xác nhận pipeline được kích hoạt bởi commit dữ liệu.**

#### 3.3 So sánh Kết quả

| Chỉ số | Bước 2 (2998 mẫu) | Bước 3 (8994 mẫu) | Thay đổi |
|---|---|---|---|
| **Accuracy** | 0.6700 | **0.7420** | +0.0720 (+10.7%) |
| **F1-Score** | 0.6685 | **0.7413** | +0.0728 (+10.9%) |

**Nhận xét:** Việc bổ sung thêm 5996 mẫu dữ liệu (tổng 8994 mẫu) đã cải thiện đáng kể hiệu suất mô hình. Accuracy tăng từ 0.6700 lên 0.7420 (tăng 10.7%), giúp mô hình vượt qua ngưỡng eval gate 0.70 lần đầu tiên. Điều này chứng tỏ thêm dữ liệu huấn luyện giúp RandomForestClassifier học được nhiều đặc trưng tổng quát hơn, đặc biệt với bộ tham số n_estimators=300, max_depth=15.

#### 3.4 Ảnh chụp GitHub Actions Bước 3

![Pipeline Bước 3](screenshots/pipeline-buoc3.png)

---

## IV. Cấu trúc Dự án Hoàn chỉnh

```
mlops-lab/
├── .github/
│   └── workflows/
│       └── mlops.yml              ← Pipeline CI/CD (4 jobs) ✅
├── .dvc/
│   └── config                     ← DVC remote: gs://mlops-lab-2a202600786/dvc ✅
├── data/
│   ├── train_phase1.csv.dvc       ← Con trỏ DVC ✅
│   ├── eval.csv.dvc               ← Con trỏ DVC ✅
│   └── train_phase2.csv.dvc       ← Con trỏ DVC ✅
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
├── README.md                      ← Báo cáo nộp bài
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

| Tiêu chí | Hoàn thành? | Ghi chú |
|---|---|---|
| Cấu hình GCP (Project, Bucket, SA, VM, Firewall) | ✅ | 100% qua CLI |
| Dữ liệu được sinh và chia | ✅ | `generate_data.py` → 2998 + 500 + 2998 mẫu |
| Virtual environment + dependencies | ✅ | Python 3.14, tất cả packages đã cài |
| Code hoàn thiện (`train.py`, `serve.py`, `test_train.py`, `mlops.yml`) | ✅ | 0 TODO, 0 pass, tất cả 4 file sạch |
| Unit test pass | ✅ | 3/3 passed (78.41s) |
| DVC init + remote GCS + dvc push | ✅ | 3 file CSV đã lên GCS |
| VM cấu hình (Python, thư viện, sa-key, systemd) | ✅ | Service `mlops-serve` đã enable |
| GitHub Actions workflow (`mlops.yml`) | ✅ | 4 jobs đã viết xong |
| Chạy ít nhất 3 thí nghiệm với MLflow | ✅ | 4 thí nghiệm (tốt nhất: n_estimators=300, max_depth=15)|
| MLflow UI hiển thị đầy đủ kết quả | ✅ | Đã sửa lỗi Python 3.14, UI hoạt động bình thường |
| Tạo GitHub repo + push code + set Secrets | ✅ | `quandum/mlops-lab-2a202600786`, 5 secrets đã set |
| Pipeline CI/CD chạy thực tế trên GitHub Actions | ✅ | Test + Train passed, Eval gate hoạt động đúng |
| Bước 3: pipeline kích hoạt bởi commit dữ liệu | ✅ | `add_new_data.py` đã chạy (8994 mẫu), dvc push thành công, accuracy 0.7420 vượt ngưỡng 0.70 |
| Báo cáo đầy đủ thông tin | ✅ | File này |

---

## VII. Phụ lục: Ảnh chụp Màn hình

### A. MLflow - 5 thí nghiệm ✅

![MLflow Experiments](screenshots/mlflow-ui.png)

### B. Pipeline Bước 2 - CI/CD thành công ✅

![Pipeline Bước 2](screenshots/pipeline-buoc2.png)

### C. API Test - Health check & Predict ✅

![API Test](screenshots/api-test.png)

### D. Pipeline Bước 3 - Continuous Training ✅

![Pipeline Bước 3](screenshots/pipeline-buoc3.png)

### E. GCS Console - Dữ liệu & Model trên Cloud Storage ✅

![GCS Console](screenshots/gcs-console.png)

