# CFP Module - Hướng Dẫn Triển Khai

## 🎯 Tóm Tắt

Module CFP (Call for Papers) hoàn chỉnh cho hệ thống quản lý hội nghị, bao gồm:
- **39 API endpoints** cho Conference, Track, Email Template
- **Clean Architecture** (Controller → Service → Repository → Database)
- **Đầy đủ Validation & Error Handling**
- **Unit Tests** mẫu

## 📦 Cấu Trúc File Tạo Mới

```
src/
├── api/
│   ├── controllers/
│   │   ├── conference_controller.py       (11 endpoints)
│   │   ├── track_controller.py            (11 endpoints)
│   │   └── email_template_controller.py   (17 endpoints)
│   └── schemas/
│       ├── conference.py
│       ├── track.py
│       └── email_template.py
├── services/
│   ├── conference_service.py
│   ├── track_service.py
│   └── email_template_service.py
└── infrastructure/repositories/
    ├── conference_repository.py
    ├── track_repository.py
    └── email_template_repository.py
```

## 🚀 Cài Đặt & Chạy

### 1. Cài Đặt Dependencies
```bash
pip install flask sqlalchemy marshmallow
```

### 2. Tạo Database Tables
```python
# Sử dụng Alembic migrations
alembic upgrade head
```

### 3. Chạy Flask App
```bash
cd src
python app.py
```

### 4. Test APIs
```bash
# Chạy unit tests
python -m pytest test_cfp_module.py -v

# Hoặc chạy Flask development
python app.py
# Truy cập: http://localhost:5000/conferences/
```

## 📝 Ví Dụ Sử Dụng API

### Tạo Hội Nghị
```bash
curl -X POST http://localhost:5000/conferences/ \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": 1,
    "name": "ICSE 2026",
    "short_name": "ICSE-2026",
    "venue": "New York",
    "cfp_is_public": false
  }'
```

### Tạo Track
```bash
curl -X POST http://localhost:5000/tracks/ \
  -H "Content-Type: application/json" \
  -d '{
    "conference_id": 1,
    "name": "Software Architecture",
    "short_name": "SA",
    "is_active": true
  }'
```

### Tạo Email Template
```bash
curl -X POST http://localhost:5000/email-templates/ \
  -H "Content-Type: application/json" \
  -d '{
    "conference_id": 1,
    "template_type": "submission_confirmation",
    "name": "Submission Confirmation",
    "subject": "Paper Received - {{paper_id}}",
    "body_html": "<p>Dear {{author_name}},</p><p>Your paper {{paper_title}} has been received.</p>"
  }'
```

### Publish CFP
```bash
curl -X POST http://localhost:5000/conferences/1/cfp/publish \
  -H "Content-Type: application/json" \
  -d '{
    "cfp_content": "<h1>Call for Papers</h1>..."
  }'
```

## 🧪 Chạy Unit Tests

```bash
# Chạy tất cả tests
python -m pytest test_cfp_module.py -v

# Chạy test cụ thể
python -m pytest test_cfp_module.py::TestConferenceService -v

# Với coverage
python -m pytest test_cfp_module.py --cov=src --cov-report=html
```

## 📚 API Endpoints

### Conference APIs (11)
| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| GET | `/conferences/` | Lấy tất cả hội nghị |
| GET | `/conferences/tenant/{id}` | Lấy hội nghị của tenant |
| GET | `/conferences/public-cfp` | Lấy hội nghị có public CFP |
| GET | `/conferences/{id}` | Lấy chi tiết hội nghị |
| POST | `/conferences/` | Tạo hội nghị |
| PUT | `/conferences/{id}` | Cập nhật hội nghị |
| DELETE | `/conferences/{id}` | Xóa hội nghị |
| POST | `/conferences/{id}/cfp/publish` | Publish CFP |
| POST | `/conferences/{id}/cfp/unpublish` | Unpublish CFP |
| PUT | `/conferences/{id}/status` | Cập nhật trạng thái |
| GET | `/conferences/{id}/cfp-status` | Kiểm tra CFP status |

### Track APIs (11)
| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| GET | `/tracks/` | Lấy tất cả tracks |
| GET | `/tracks/conference/{id}` | Lấy tracks của hội nghị |
| GET | `/tracks/{id}` | Lấy chi tiết track |
| POST | `/tracks/` | Tạo track |
| PUT | `/tracks/{id}` | Cập nhật track |
| DELETE | `/tracks/{id}` | Xóa track |
| POST | `/tracks/{id}/activate` | Kích hoạt track |
| POST | `/tracks/{id}/deactivate` | Vô hiệu hóa track |
| POST | `/tracks/conference/{id}/reorder` | Sắp xếp lại tracks |
| POST | `/tracks/{id}/chair/{user_id}` | Gán track chair |
| GET | `/tracks/{id}/submission-status` | Kiểm tra status |

### Email Template APIs (17)
| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| GET | `/email-templates/` | Lấy tất cả templates |
| GET | `/email-templates/conference/{id}` | Lấy templates của hội nghị |
| GET | `/email-templates/{id}` | Lấy chi tiết template |
| GET | `/email-templates/type/{type}` | Lấy template theo loại |
| POST | `/email-templates/` | Tạo template |
| PUT | `/email-templates/{id}` | Cập nhật template |
| DELETE | `/email-templates/{id}` | Xóa template |
| GET | `/email-templates/{id}/placeholders` | Lấy placeholders |
| POST | `/email-templates/{id}/render` | Render template |
| GET | `/email-templates/logs` | Lấy tất cả logs |
| GET | `/email-templates/logs/conference/{id}` | Lấy logs hội nghị |
| GET | `/email-templates/logs/{id}` | Lấy chi tiết log |
| POST | `/email-templates/logs` | Tạo email log |
| POST | `/email-templates/logs/{id}/mark-sent` | Đánh dấu đã gửi |
| POST | `/email-templates/logs/{id}/mark-failed` | Đánh dấu thất bại |
| GET | `/email-templates/logs/status/{status}` | Lấy logs theo status |
| GET | `/email-templates/logs/pending` | Lấy pending emails |

## 🔧 Tích Hợp Vào Dự Án

### 1. Thêm Vào requirements.txt
```
Flask==2.3.0
SQLAlchemy==2.0.0
Marshmallow==3.19.0
```

### 2. Cập Nhật app.py (nếu cần)
```python
from src.api.routes import register_routes

app = Flask(__name__)

# Register all routes
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
```

### 3. Models Đã Tồn Tại
- `ConferenceModel` ✅
- `TrackModel` ✅
- `EmailTemplateModel` & `EmailLogModel` ✅

## ✨ Tính Năng Chính

✅ **CRUD đầy đủ** cho Conference, Track, Email Template
✅ **Validation** dữ liệu tự động (Marshmallow)
✅ **Business Logic** trong Services
✅ **Database Access** qua Repositories
✅ **Error Handling** toàn diện
✅ **Placeholder Support** cho email templates ({{author_name}}, {{paper_id}}, v.v.)
✅ **Email Logging** với trạng thái (pending, sent, failed, bounced)
✅ **CFP Management** (publish/unpublish)
✅ **Track Management** (reorder, assign chair)
✅ **Conference Status** (draft, open, reviewing, decided, published)

## 🐛 Troubleshooting

### Import Error: No module named 'src'
**Giải pháp:** Thêm dòng này vào đầu file:
```python
import sys
sys.path.insert(0, '/path/to/src')
```

### Database Connection Error
**Giải pháp:** Kiểm tra `infrastructure/databases/mssql.py`:
```python
from infrastructure.databases.mssql import session
```

### Marshmallow Validation Error
**Giải pháp:** Kiểm tra schema và request body match

## 📖 Tài Liệu Đầy Đủ
Xem `docs/CFP_API_GUIDE.md` để biết chi tiết

## ✅ Danh Sách Hoàn Thành

- ✅ Conference Controller (11 endpoints)
- ✅ Track Controller (11 endpoints)
- ✅ Email Template Controller (17 endpoints)
- ✅ Conference Service
- ✅ Track Service
- ✅ Email Template Service & Email Log Service
- ✅ Conference Repository
- ✅ Track Repository
- ✅ Email Template Repository & Email Log Repository
- ✅ Schemas/DTOs (Conference, Track, Email Template)
- ✅ Routes Registration
- ✅ Unit Tests
- ✅ API Documentation
- ✅ Deployment Guide

---

**Total: 39 API Endpoints, 3 Services, 3 Repositories, 3 Controllers, 3 Schemas**

Module sẵn sàng sử dụng! 🎉
