UTH Scientific Conference Paper Management System
● Vietnamese: Hệ thống quản lý giấy tờ Hội nghị Nghiên cứu khoa học dành cho Trường ĐH UTH
● Abbreviation: UTH-ConfMS
a. Context:
Faculties at UTH University already organize research conferences using a combination of external software and services for submission, peer review, decision making, camera-ready collection, scheduling, and publication. However, the workflows are fragmented across multiple tools and vendor portals, which leads to duplicated data, inconsistent templates, dispersed communications, uneven enforcement of conflicts of interest (COI), and limited end-to-end reporting. The proposed system, UTH-ConfMS, unifies these activities by providing an EasyChair style, end-to-end flow: Call for Papers, then Submission, then Review, then Decision, then Camera-ready, then Program and Proceedings. It offers centralized role-based access control (RBAC), single sign-on (SSO), configurable policies, full audit trails, and optional connectors and migration utilities to interoperate with or replace existing services over time.

b. Proposed Solutions:
- Conference and Call for Papers (CFP) setup: create CFP page, deadlines, tracks/topics, email/form templates.
- Submission/abstract and updates: author metadata, co-authors, PDF upload; withdraw/edit before deadline.
- Program Committee (PC) management: invite PC members, track review progress, detect and block conflicts of interest (COI).
- Assignment and review: manual/automatic assignment by topic/keywords; scores and comments; internal discussion; rebuttal window (optional).
- Decision and notifications: aggregate reviews, Accept/Reject, bulk email with anonymized feedback.
- Camera-ready and proceedings: open final-version round; export data for schedule/proceedings (optional open access publishing).
- Reports and analytics: submissions by school/track, acceptance rate, review service-level agreement (SLA), activity logs.

- AI-assisted tools (opt-in, human-in-the-loop):
○ Spell and grammar checking for titles, abstracts, and form text fields.
○ Neutral summaries (150–250 words) to support PC bidding and quick triage.
○ Reviewer–paper similarity hints from topic/keyword embeddings to aid assignment (never auto-assign).
○ Configurable feature flags per conference; all AI suggestions require explicit human confirmation.

● Functional requirement
○ Author: register/login; submit/withdraw/edit before deadline; view results and anonymized reviews; upload camera-ready.
■ AI for Authors (optional): on-demand spell/grammar checks for title/abstract; abstract polishing and keyword suggestions with side-by-side diffs; no automatic edits to uploaded PDF files.
○ Reviewer / PC member: access assigned papers; submit scores/reviews; internal discussions; declare decline/COI.
■ AI for Reviewers/PC (optional): auto-generated neutral synopsis for bidding; key-point extraction (claims, methods, datasets) from abstracts; no author identity exposure during double-blind phases.
○ Program/Track Chair: configure conference/tracks; invite PC; assign papers (manual/automatic); track progress; record decisions; bulk notifications; open camera-ready.
■ AI for Chairs (optional): AI-drafted email templates for decisions and reminders (chair review required).
○ Site Administrator (optional): multi-conference operations, Simple Mail Transfer Protocol (SMTP) configuration/quotas, backup/restore, tenancy settings.
○ AI governance controls (system-wide): preview before apply; per-feature enable/disable; audit entries store prompt, model identifier, timestamp, and input hash.

● Non-functional requirement:
○ Security and privacy: HTTPS; strict role-based access control (RBAC); single-blind/double-blind review modes; COI enforcement; hashed passwords; audit logs; single sign-on (SSO) support.
○ AI data governance: no training on conference data unless the institution opts in; redact personal data in double-blind phases; third-party providers require a data-processing agreement.
○ Performance and scalability: handle deadline peaks; caching; thousands of papers and hundreds of concurrent users.
○ Explainability and quality: every AI score or suggestion includes a short rationale (e.g., top overlapping keywords); track acceptance rate of AI suggestions and reviewer satisfaction.
○ Usability and internationalization (i18n): clear forms; customizable emails/templates; English/Vietnamese user interface (UI); preserve Unicode throughout.
● Conference Workflow (BPMN Swimlane Diagram):


(*) 3.2. Main proposal content (including result and product)
a. Theory and practice (document):
● Students should apply the software development process and UML 2.0 in the modeling system.
● The documents include User Requirements, Software Requirement Specifications, Architecture Design, Detail Design, System Implementation, Testing Document, Installation Guide, source code, and deployable software packages.
● Server-side technologies:
○ Server: Python
○ Database Design: Postgres, Redis
● Client-side technologies:
○ Web Client: ReactJS

b. Products:
○ Role-based web app for Authors/PC/Chairs; Admin portal for platform ops.
○ Public portal for CFP, program, accepted papers (if enabled)..
○ OpenAPI/Swagger for standardized REST.
c. Proposed Tasks:
○ TP1 - Admin & platform: tenancy, RBAC, SMTP/quota, audit.
○ TP2 - Conference & CFP: create/configure conference, tracks, deadlines, templates.
○ TP3 - Submission: author dashboard, metadata, PDF upload, withdraw/edit..
○ TP4 - PC & assignment: invitations, COI, manual/auto assignment, progress tracking.
○ TP5 - Review & discussion: score/review forms, internal PC discussion, rebuttal (optional).
○ TP6 - Decision & notifications: review aggregation, decisions, bulk email to authors.
○ TP7 - Camera-ready & proceedings: final uploads, export to program/proceedings.
○ TP8 - Build – Deploy and Test the system.
○ TP9 - Prepare all the required documents: System analysis and Design, Test plan, Installation manual, User manual.