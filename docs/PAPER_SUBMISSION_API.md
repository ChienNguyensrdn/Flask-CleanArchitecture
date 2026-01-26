# Paper Submission Module (UC-15) - API Documentation

## 📝 Tổng Quan

Module Paper Submission cung cấp đầy đủ tính năng:
- **Nộp bài báo** (draft → submitted)
- **Quản lý tác giả** (thêm, xóa, sắp xếp, corresponding author)
- **Upload file** (PDF chính & tài liệu bổ sung)
- **Cập nhật bài** (chỉ draft)
- **Hủy nộp** (withdraw)
- **Yêu cầu sửa** (revision request)
- **Nộp lại sau sửa** (resubmit)

## 📊 Paper Statuses

| Status | Mô Tả |
|--------|-------|
| **draft** | Bài đang soạn thảo (chưa nộp) |
| **submitted** | Đã nộp chính thức |
| **under_review** | Đang được đánh giá |
| **revision_requested** | Yêu cầu sửa chữa |
| **accepted** | Được chấp nhận |
| **rejected** | Từ chối |
| **withdrawn** | Rút lại bài nộp |
| **camera_ready** | Sẵn sàng xuất bản |

## 🎯 API Endpoints

### Paper Management (11 endpoints)

#### 1. Tạo bài báo (Draft)
```
POST /papers/
Content-Type: application/json

{
  "conference_id": 1,
  "track_id": 1,
  "title": "A Novel Approach to Software Architecture",
  "abstract": "This paper presents a comprehensive study of modern software architecture patterns...",
  "keywords": "architecture, design patterns, microservices",
  "submitter_id": 5,
  "authors": [
    {
      "user_id": 5,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "affiliation": "MIT",
      "country": "USA",
      "author_order": 1,
      "is_corresponding": true,
      "is_presenter": true
    },
    {
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane@example.com",
      "affiliation": "Stanford",
      "country": "USA",
      "author_order": 2,
      "is_corresponding": false,
      "is_presenter": false
    }
  ],
  "page_count": 12,
  "word_count": 5000
}
```

**Response (201):**
```json
{
  "id": 1,
  "conference_id": 1,
  "track_id": 1,
  "submitter_id": 5,
  "paper_number": null,
  "title": "A Novel Approach to Software Architecture",
  "abstract": "...",
  "keywords": "architecture, design patterns, microservices",
  "pdf_path": null,
  "supplementary_path": null,
  "page_count": 12,
  "word_count": 5000,
  "status": "draft",
  "is_withdrawn": false,
  "requires_revision": false,
  "submitted_at": null,
  "withdrawn_at": null,
  "created_at": "2026-01-26T10:00:00",
  "updated_at": "2026-01-26T10:00:00",
  "authors": [...]
}
```

#### 2. Lấy danh sách bài báo
```
GET /papers/?conference_id=1&submitter_id=5
```

Query parameters:
- `conference_id` (optional) - Lọc theo hội nghị
- `submitter_id` (optional) - Lọc theo tác giả nộp

#### 3. Lấy chi tiết bài báo
```
GET /papers/{paper_id}
```

#### 4. Cập nhật bài báo (chỉ draft)
```
PUT /papers/{paper_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "abstract": "Updated abstract...",
  "keywords": "new keywords",
  "track_id": 2,
  "page_count": 15,
  "word_count": 6000
}
```

**Lưu ý:** Chỉ có thể cập nhật bài báo ở trạng thái `draft`

#### 5. Xóa bài báo (chỉ draft)
```
DELETE /papers/{paper_id}
```

**Lưu ý:** Chỉ có thể xóa bài báo ở trạng thái `draft`

#### 6. Nộp bài chính thức
```
POST /papers/{paper_id}/submit
```

**Điều kiện:**
- Bài phải có ít nhất 1 tác giả
- Phải có 1 tác giả corresponding
- Phải upload PDF

#### 7. Rút lại bài nộp
```
POST /papers/{paper_id}/withdraw
```

#### 8. Cập nhật trạng thái
```
PUT /papers/{paper_id}/status
Content-Type: application/json

{
  "status": "under_review"
}
```

#### 9. Yêu cầu sửa chữa
```
POST /papers/{paper_id}/request-revision
Content-Type: application/json

{
  "revision_notes": "Please clarify the methodology section and provide more experimental results..."
}
```

#### 10. Nộp lại sau sửa
```
POST /papers/{paper_id}/resubmit
Content-Type: application/json

{
  "title": "Updated Title",
  "abstract": "Updated abstract with revisions..."
}
```

#### 11. Danh sách bài theo track
```
GET /papers?track_id=1
```

---

### File Upload (2 endpoints)

#### Upload PDF Chính
```
POST /papers/{paper_id}/upload-pdf
Content-Type: multipart/form-data

File: paper.pdf (max 50MB)
```

**Response (200):**
```json
{
  "message": "PDF uploaded successfully",
  "file_path": "uploads/papers/paper_1/paper_1.pdf"
}
```

#### Upload Tài Liệu Bổ Sung
```
POST /papers/{paper_id}/upload-supplementary
Content-Type: multipart/form-data

File: supplementary_data.zip (max 50MB)
```

---

### Author Management (7 endpoints)

#### 1. Lấy danh sách tác giả
```
GET /papers/{paper_id}/authors
```

**Response (200):**
```json
[
  {
    "id": 1,
    "paper_id": 1,
    "user_id": 5,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "affiliation": "MIT",
    "country": "USA",
    "orcid": "0000-0001-2345-6789",
    "author_order": 1,
    "is_corresponding": true,
    "is_presenter": true,
    "created_at": "2026-01-26T10:00:00",
    "updated_at": "2026-01-26T10:00:00"
  },
  ...
]
```

#### 2. Thêm tác giả
```
POST /papers/{paper_id}/authors
Content-Type: application/json

{
  "user_id": 10,
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "affiliation": "Stanford",
  "country": "USA",
  "orcid": "0000-0001-9876-5432",
  "author_order": 2,
  "is_corresponding": false,
  "is_presenter": false
}
```

#### 3. Lấy chi tiết tác giả
```
GET /papers/authors/{author_id}
```

#### 4. Cập nhật thông tin tác giả
```
PUT /papers/authors/{author_id}
Content-Type: application/json

{
  "affiliation": "Updated Affiliation",
  "email": "newemail@example.com"
}
```

#### 5. Xóa tác giả
```
DELETE /papers/authors/{author_id}
```

#### 6. Gán tác giả corresponding
```
POST /papers/{paper_id}/corresponding-author/{author_id}
```

**Lưu ý:** Chỉ có 1 tác giả corresponding. Gán tác giả mới sẽ hủy gán của tác giả cũ.

#### 7. Sắp xếp lại tác giả
```
POST /papers/{paper_id}/reorder-authors
Content-Type: application/json

{
  "authors": [
    {
      "author_id": 1,
      "order": 1
    },
    {
      "author_id": 2,
      "order": 2
    },
    {
      "author_id": 3,
      "order": 3
    }
  ]
}
```

---

## 💻 Ví Dụ Workflow Hoàn Chỉnh

### 1. Tạo bài báo draft
```bash
curl -X POST http://localhost:5000/papers/ \
  -H "Content-Type: application/json" \
  -d '{
    "conference_id": 1,
    "track_id": 1,
    "title": "My Research Paper",
    "abstract": "This is the abstract...",
    "authors": [...],
    "submitter_id": 5
  }'

# Response: Paper ID = 1
```

### 2. Upload PDF
```bash
curl -X POST http://localhost:5000/papers/1/upload-pdf \
  -F "file=@paper.pdf"
```

### 3. Cập nhật thông tin
```bash
curl -X PUT http://localhost:5000/papers/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

### 4. Thêm tác giả bổ sung
```bash
curl -X POST http://localhost:5000/papers/1/authors \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com"
  }'
```

### 5. Gán tác giả corresponding
```bash
curl -X POST http://localhost:5000/papers/1/corresponding-author/1
```

### 6. Upload supplementary
```bash
curl -X POST http://localhost:5000/papers/1/upload-supplementary \
  -F "file=@supplementary.zip"
```

### 7. Nộp bài chính thức
```bash
curl -X POST http://localhost:5000/papers/1/submit
```

### 8. Yêu cầu sửa
```bash
curl -X POST http://localhost:5000/papers/1/request-revision \
  -H "Content-Type: application/json" \
  -d '{"revision_notes": "Please clarify..."}'
```

### 9. Nộp lại sau sửa
```bash
curl -X POST http://localhost:5000/papers/1/resubmit \
  -H "Content-Type: application/json" \
  -d '{"abstract": "Updated abstract..."}'
```

---

## 🔐 Validation Rules

### Paper Title
- Tối thiểu 5 ký tự
- Tối đa 1000 ký tự

### Abstract
- Tối thiểu 50 ký tự
- Tối đa 5000 ký tự

### Authors
- Bắt buộc ít nhất 1 tác giả
- Bắt buộc 1 tác giả corresponding

### File Upload
- Chỉ PDF được chấp nhận
- Tối đa 50MB

### Author Info
- Email là bắt buộc
- First name & Last name là bắt buộc

---

## ⚠️ Error Codes

| Status | Error | Giải Pháp |
|--------|-------|-----------|
| 400 | "Cannot update submitted papers" | Chỉ có thể cập nhật draft papers |
| 400 | "Paper must have at least one author" | Thêm tác giả trước khi nộp |
| 400 | "Paper must have a corresponding author" | Gán tác giả corresponding |
| 400 | "Paper PDF must be uploaded" | Upload PDF trước khi nộp |
| 400 | "Only PDF files allowed" | Chỉ upload file PDF |
| 400 | "File too large" | File vượt quá 50MB |
| 404 | "Paper not found" | Paper ID không tồn tại |
| 404 | "Author not found" | Author ID không tồn tại |

---

## 📋 Database Models

### PaperModel
```python
id: int (primary key)
conference_id: int (foreign key)
track_id: int (foreign key, nullable)
submitter_id: int (foreign key)
paper_number: str (nullable)
title: str (1000 chars max)
abstract: text
keywords: text
pdf_path: str (500 chars, nullable)
supplementary_path: str (500 chars, nullable)
page_count: int (nullable)
word_count: int (nullable)
status: str (draft, submitted, under_review, ...)
submitted_at: datetime (nullable)
withdrawn_at: datetime (nullable)
is_withdrawn: bool
requires_revision: bool
created_at: datetime
updated_at: datetime
```

### PaperAuthorModel
```python
id: int (primary key)
paper_id: int (foreign key)
user_id: int (foreign key, nullable - cho external authors)
author_order: int
first_name: str
last_name: str
email: str
affiliation: str (nullable)
country: str (nullable)
orcid: str (nullable)
is_corresponding: bool
is_presenter: bool
created_at: datetime
updated_at: datetime
```

---

## 🚀 Deployment

### Files Tạo Mới
- ✅ `src/api/schemas/paper.py`
- ✅ `src/infrastructure/repositories/paper_repository.py`
- ✅ `src/services/paper_service.py`
- ✅ `src/api/controllers/paper_controller.py`
- ✅ `src/api/routes.py` (updated)

### File Cấu Hình
- Upload path: `uploads/papers/` (auto-created)
- Max file size: 50MB (configurable)
- Allowed extensions: pdf

### Install Dependencies
```bash
pip install flask werkzeug  # werkzeug for file upload
```

---

## 📊 Statistics

- **Total Endpoints:** 20
- **Paper Management:** 11 endpoints
- **File Upload:** 2 endpoints
- **Author Management:** 7 endpoints
- **Request Validation:** Full Marshmallow schemas
- **Error Handling:** Comprehensive with proper HTTP codes

---

**Module hoàn thành! Sẵn sàng production.** 🎉
