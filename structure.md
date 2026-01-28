UTH_ConfMS/
├── main.py                    # FastAPI application entry point
├── pyproject.toml             # Project dependencies
├── .env                       # Environment configuration
├── app/
│   ├── core/
│   │   ├── config.py          # Settings management
│   │   ├── database.py        # SQLAlchemy setup
│   │   └── security.py        # JWT & password hashing
│   ├── models/                # Database models (SQLAlchemy)
│   │   ├── tenant.py          # Multi-tenancy
│   │   ├── user.py            # Users & authentication
│   │   ├── conference.py      # Conference settings
│   │   ├── track.py           # Conference tracks
│   │   ├── paper.py           # Paper submissions
│   │   ├── paper_author.py    # Co-authors
│   │   ├── pc_member.py       # Program committee
│   │   ├── paper_assignment.py # Reviewer assignments
│   │   ├── review.py          # Reviews & scores
│   │   ├── decision.py        # Accept/reject
│   │   ├── camera_ready.py    # Final versions
│   │   └── audit_log.py       # Activity tracking
│   ├── schemas/               # Pydantic schemas
│   │   ├── user.py
│   │   ├── conference.py
│   │   ├── paper.py
│   │   └── review.py
│   └── api/                   # API endpoints
│       ├── deps.py            # Dependencies (auth)
│       ├── auth.py            # /api/v1/auth
│       ├── conferences.py     # /api/v1/conferences
│       ├── papers.py          # /api/v1/papers
│       ├── reviews.py         # /api/v1/reviews
│       └── pc_members.py      # /api/v1/pc-members