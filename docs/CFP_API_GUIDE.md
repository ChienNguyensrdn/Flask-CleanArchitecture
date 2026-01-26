# CFP (Call for Papers) Module - API Documentation

## Tổng Quan
Module CFP cung cấp các API để quản lý hội nghị, chủ đề nghiên cứu (tracks), mẫu email và ghi nhật ký email.

## Cấu Trúc Dự Án

```
src/
├── api/
│   ├── controllers/
│   │   ├── conference_controller.py     # API endpoints cho hội nghị
│   │   ├── track_controller.py          # API endpoints cho chủ đề
│   │   └── email_template_controller.py # API endpoints cho mẫu email
│   └── schemas/
│       ├── conference.py                # Schemas cho hội nghị
│       ├── track.py                     # Schemas cho chủ đề
│       └── email_template.py            # Schemas cho email
├── services/
│   ├── conference_service.py            # Business logic hội nghị
│   ├── track_service.py                 # Business logic chủ đề
│   └── email_template_service.py        # Business logic email
└── infrastructure/
    ├── repositories/
    │   ├── conference_repository.py      # Database access hội nghị
    │   ├── track_repository.py           # Database access chủ đề
    │   └── email_template_repository.py  # Database access email
    └── models/
        ├── conference_model.py           # Mô hình cơ sở dữ liệu hội nghị
        ├── track_model.py                # Mô hình cơ sở dữ liệu chủ đề
        └── email_template_model.py       # Mô hình cơ sở dữ liệu email
```

## Conference API Endpoints

### 1. Lấy danh sách tất cả hội nghị
```
GET /conferences/
```

**Response (200):**
```json
[
  {
    "id": 1,
    "tenant_id": 1,
    "name": "International Conference on Software Engineering",
    "short_name": "ICSE-2026",
    "description": "...",
    "venue": "New York, USA",
    "submission_deadline": "2026-03-31T23:59:59",
    "review_deadline": "2026-05-31T23:59:59",
    "notification_date": "2026-06-15T00:00:00",
    "camera_ready_deadline": "2026-07-15T23:59:59",
    "conference_start_date": "2026-08-01T00:00:00",
    "conference_end_date": "2026-08-05T23:59:59",
    "cfp_content": "Call for Papers content...",
    "cfp_is_public": true,
    "review_mode": "double_blind",
    "min_reviews_per_paper": 3,
    "status": "open",
    "created_at": "2026-01-26T10:00:00"
  }
]
```

### 2. Lấy hội nghị theo tenant
```
GET /conferences/tenant/{tenant_id}
```

### 3. Lấy hội nghị có public CFP
```
GET /conferences/public-cfp
```

### 4. Lấy chi tiết hội nghị
```
GET /conferences/{conference_id}
```

### 5. Tạo hội nghị mới
```
POST /conferences/
Content-Type: application/json

{
  "tenant_id": 1,
  "name": "International Conference on Software Engineering",
  "short_name": "ICSE-2026",
  "description": "...",
  "venue": "New York, USA",
  "submission_deadline": "2026-03-31T23:59:59",
  "review_deadline": "2026-05-31T23:59:59",
  "notification_date": "2026-06-15T00:00:00",
  "camera_ready_deadline": "2026-07-15T23:59:59",
  "conference_start_date": "2026-08-01T00:00:00",
  "conference_end_date": "2026-08-05T23:59:59",
  "cfp_is_public": false,
  "review_mode": "double_blind",
  "min_reviews_per_paper": 3
}
```

**Response (201):** Trả về conference object mới tạo

### 6. Cập nhật hội nghị
```
PUT /conferences/{conference_id}
Content-Type: application/json

{
  "name": "Updated Conference Name",
  "description": "Updated description",
  ...
}
```

### 7. Xóa hội nghị
```
DELETE /conferences/{conference_id}
```

**Response (204):** No content

### 8. Publish CFP
```
POST /conferences/{conference_id}/cfp/publish
Content-Type: application/json

{
  "cfp_content": "Call for Papers HTML content..."
}
```

### 9. Unpublish CFP
```
POST /conferences/{conference_id}/cfp/unpublish
```

### 10. Cập nhật trạng thái hội nghị
```
PUT /conferences/{conference_id}/status
Content-Type: application/json

{
  "status": "open"  // draft, open, reviewing, decided, published
}
```

### 11. Kiểm tra trạng thái CFP
```
GET /conferences/{conference_id}/cfp-status
```

**Response (200):**
```json
{
  "conference_id": 1,
  "cfp_is_public": true,
  "is_cfp_open": true,
  "submission_deadline": "2026-03-31T23:59:59"
}
```

---

## Track API Endpoints

### 1. Lấy danh sách tất cả chủ đề
```
GET /tracks/
```

### 2. Lấy chủ đề của hội nghị
```
GET /tracks/conference/{conference_id}
?include_inactive=false
```

Query params:
- `include_inactive` (boolean): Bao gồm các track không hoạt động

### 3. Lấy chi tiết chủ đề
```
GET /tracks/{track_id}
```

### 4. Tạo chủ đề mới
```
POST /tracks/
Content-Type: application/json

{
  "conference_id": 1,
  "name": "Software Architecture",
  "short_name": "SA",
  "description": "Track for software architecture papers",
  "keywords": "architecture, design patterns, system design",
  "submission_deadline": "2026-03-31T23:59:59",
  "review_deadline": "2026-05-31T23:59:59",
  "track_chair_id": null,
  "is_active": true,
  "display_order": 0
}
```

**Response (201):** Trả về track object mới tạo

### 5. Cập nhật chủ đề
```
PUT /tracks/{track_id}
Content-Type: application/json

{
  "name": "Updated Track Name",
  "description": "Updated description",
  ...
}
```

### 6. Xóa chủ đề (soft delete)
```
DELETE /tracks/{track_id}
```

### 7. Kích hoạt chủ đề
```
POST /tracks/{track_id}/activate
```

### 8. Vô hiệu hóa chủ đề
```
POST /tracks/{track_id}/deactivate
```

### 9. Sắp xếp lại các chủ đề
```
POST /tracks/conference/{conference_id}/reorder
Content-Type: application/json

{
  "track_order": [
    {"track_id": 1, "display_order": 1},
    {"track_id": 2, "display_order": 2},
    {"track_id": 3, "display_order": 3}
  ]
}
```

### 10. Gán track chair
```
POST /tracks/{track_id}/chair/{user_id}
```

### 11. Kiểm tra trạng thái gửi bài của track
```
GET /tracks/{track_id}/submission-status
```

**Response (200):**
```json
{
  "track_id": 1,
  "name": "Software Architecture",
  "is_open": true,
  "is_active": true,
  "submission_deadline": "2026-03-31T23:59:59"
}
```

---

## Email Template API Endpoints

### 1. Lấy danh sách mẫu email
```
GET /email-templates/
```

### 2. Lấy mẫu email của hội nghị
```
GET /email-templates/conference/{conference_id}
```

### 3. Lấy chi tiết mẫu email
```
GET /email-templates/{template_id}
```

### 4. Lấy mẫu email theo loại
```
GET /email-templates/type/{template_type}
?conference_id=1
```

Template types:
- `submission_confirmation` - Xác nhận gửi bài
- `pc_invitation` - Mời PC members
- `review_assigned` - Phân công đánh giá
- `review_reminder` - Nhắc nhở đánh giá
- `decision_accept` - Thông báo chấp nhận
- `decision_reject` - Thông báo từ chối
- `camera_ready_reminder` - Nhắc nhở camera ready
- `rebuttal_open` - Thông báo rebuttal

### 5. Tạo mẫu email
```
POST /email-templates/
Content-Type: application/json

{
  "conference_id": 1,
  "template_type": "submission_confirmation",
  "name": "Submission Confirmation",
  "subject": "Your paper has been submitted",
  "body_html": "<html>...<p>Dear {{author_name}},</p>...</html>",
  "body_text": "Dear {{author_name}}, ...",
  "language": "en",
  "is_active": true,
  "is_default": false
}
```

### 6. Cập nhật mẫu email
```
PUT /email-templates/{template_id}
Content-Type: application/json

{
  "subject": "Updated subject",
  "body_html": "Updated content...",
  ...
}
```

### 7. Xóa mẫu email
```
DELETE /email-templates/{template_id}
```

### 8. Lấy placeholders có sẵn
```
GET /email-templates/{template_id}/placeholders
```

**Response (200):**
```json
{
  "template_id": 1,
  "template_type": "submission_confirmation",
  "placeholders": [
    "author_name",
    "paper_title",
    "paper_id",
    "conference_name",
    "submission_date",
    "submission_deadline"
  ]
}
```

### 9. Render mẫu email với dữ liệu
```
POST /email-templates/{template_id}/render
Content-Type: application/json

{
  "placeholders": {
    "author_name": "John Doe",
    "paper_title": "A Study on Software Architecture",
    "paper_id": "ICSE2026-001",
    "conference_name": "ICSE 2026",
    "submission_date": "2026-01-26",
    "submission_deadline": "2026-03-31"
  }
}
```

**Response (200):**
```json
{
  "subject": "Your paper has been submitted",
  "body_html": "<html>...<p>Dear John Doe,</p>...<p>Paper ID: ICSE2026-001</p>...</html>"
}
```

---

## Email Log API Endpoints

### 1. Lấy danh sách tất cả email logs
```
GET /email-templates/logs
```

### 2. Lấy email logs của hội nghị
```
GET /email-templates/logs/conference/{conference_id}
```

### 3. Lấy chi tiết email log
```
GET /email-templates/logs/{log_id}
```

### 4. Tạo email log (ghi lại email)
```
POST /email-templates/logs
Content-Type: application/json

{
  "conference_id": 1,
  "template_id": 1,
  "recipient_email": "author@example.com",
  "recipient_name": "John Doe",
  "recipient_user_id": 5,
  "subject": "Your paper has been submitted",
  "body": "HTML content of email...",
  "paper_id": 123
}
```

**Response (201):** Email log object được tạo

### 5. Đánh dấu email đã gửi
```
POST /email-templates/logs/{log_id}/mark-sent
```

### 6. Đánh dấu email thất bại
```
POST /email-templates/logs/{log_id}/mark-failed
Content-Type: application/json

{
  "error_message": "Invalid email address"
}
```

### 7. Lấy emails theo trạng thái
```
GET /email-templates/logs/status/{status}
```

Status: `pending`, `sent`, `failed`, `bounced`

### 8. Lấy danh sách emails pending
```
GET /email-templates/logs/pending
```

---

## Ví dụ Sử Dụng Thực Tế

### Workflow: Tạo hội nghị với CFP

```bash
# 1. Tạo hội nghị
POST /conferences/
{
  "tenant_id": 1,
  "name": "ICSE 2026",
  "short_name": "ICSE-2026",
  "venue": "New York",
  "submission_deadline": "2026-03-31T23:59:59"
}

# 2. Tạo tracks
POST /tracks/
{
  "conference_id": 1,
  "name": "Software Architecture",
  "short_name": "SA"
}

POST /tracks/
{
  "conference_id": 1,
  "name": "Machine Learning",
  "short_name": "ML"
}

# 3. Chuẩn bị mẫu email
POST /email-templates/
{
  "conference_id": 1,
  "template_type": "submission_confirmation",
  "name": "ICSE Submission Confirmation",
  "subject": "Your ICSE 2026 Submission - {{paper_id}}",
  "body_html": "<p>Dear {{author_name}},</p><p>Your paper {{paper_title}} has been received.</p>"
}

# 4. Publish CFP
POST /conferences/1/cfp/publish
{
  "cfp_content": "<h1>Call for Papers</h1><p>We invite submissions...</p>"
}

# 5. Kiểm tra trạng thái CFP
GET /conferences/1/cfp-status

# 6. Gửi email xác nhận
POST /email-templates/logs
{
  "conference_id": 1,
  "template_id": 1,
  "recipient_email": "author@example.com",
  "recipient_name": "John Doe",
  "subject": "Your ICSE 2026 Submission - ICSE2026-001",
  "body": "Dear John Doe, Your paper A Study on Software Architecture has been received.",
  "paper_id": 1
}

POST /email-templates/logs/{log_id}/mark-sent
```

---

## Lỗi Phổ Biến

| Status Code | Mô Tả |
|-------------|-------|
| 200 | OK - Thành công |
| 201 | Created - Tạo thành công |
| 204 | No Content - Xóa thành công |
| 400 | Bad Request - Dữ liệu không hợp lệ |
| 404 | Not Found - Không tìm thấy |
| 500 | Server Error - Lỗi máy chủ |

---

## Yêu Cầu & Cài Đặt

### Dependencies:
```
Flask
SQLAlchemy
Marshmallow
```

### Models:
- `ConferenceModel` - Lưu trữ thông tin hội nghị
- `TrackModel` - Lưu trữ chủ đề nghiên cứu
- `EmailTemplateModel` - Lưu trữ mẫu email
- `EmailLogModel` - Lưu trữ nhật ký email

---

## Thiết Kế Clean Architecture

**Controllers** → **Services** → **Repositories** → **Database**

- **Controllers**: Xử lý HTTP requests/responses
- **Services**: Business logic
- **Repositories**: Database access
- **Models**: ORM objects

Thiết kế này giúp dễ test, maintain, và scale.
