# Architecture

```bash
    ├── migrations
    ├── scripts
    │   └── run_postgres.sh
    ├── src
    │   ├── api
    │   │   ├── controllers
    │   │   │   └── ...  # controllers for the api
    │   │   ├── schemas
    │   │   │   └── ...  # Marshmallow schemas
    │   │   ├── middleware.py
    │   │   ├── responses.py
    │   │   └── requests.py
    │   ├── infrastructure
    │   │   ├── services
    │   │   │   └── ...  # Services that use third party libraries or services (e.g. email service)
    │   │   ├── databases
    │   │   │   └── ...  # Database adapaters and initialization
    │   │   ├── repositories
    │   │   │   └── ...  # Repositories for interacting with the databases
    │   │   └── models
    │   │   │   └── ...  # Database models
    │   ├── domain
    │   │   ├── constants.py
    │   │   ├── exceptions.py
    │   │   ├── models
    │   │   │   └── ...  # Business logic models
    │   ├── services
    │   │    └── ...  # Services for interacting with the domain (business logic)
    │   ├── app.py
    │   ├── config.py
    │   ├── cors.py
    │   ├── create_app.py
    │   ├── dependency_container.py
    │   ├── error_handler.py
    │   └── logging.py
```

## Domain Layer

## Services Layer

## Infrastructure Layer

## Download source code (CMD)
    git clone https://github.com/ChienNguyensrdn/Flask-CleanArchitecture.git
## Kiểm tra đã cài python đã cài đặt trên máy chưa
    python --version
## Run app

 - Bước 1: Tạo môi trường ảo co Python (phiên bản 3.x)
     ## Windows:
     		py -m venv .venv
     ## Unix/MacOS:
     		python3 -m venv .venv
   - Bước 2: Kích hoạt môi trường:
     ## Windows:
     		.venv\Scripts\activate.ps1
     ### Nếu xảy ra lỗi active .venv trên winos run powershell -->Administrator
         Set-ExecutionPolicy RemoteSigned -Force
     ## Unix/MacOS:
     		source .venv/bin/activate
     
   - Bước 3: Cài đặt các thư viện cần thiết
     ## Install:
     		pip install -r requirements.txt
   - Bước 4: Chạy mã xử lý dữ liệu
     ## Run:
    		python app.py


     Truy câp http://localhost:6868/docs
     Truy câp http://localhost:9999/docs



## Create file .env in folder /src/.env
    
    # Flask settings
    FLASK_ENV=development
    SECRET_KEY=your_secret_key
    
    # SQL Server settings
    DB_USER=sa
    DB_PASSWORD=Aa@123456
    DB_HOST=127.0.0.1
    DB_PORT=1433
    DB_NAME=FlaskApiDB
    
    
    DATABASE_URI = "mssql+pymssql://sa:Aa%40123456@127.0.0.1:1433/FlaskApiDB"

## pull image MS SQL server 
    
    ```bash
    docker pull mcr.microsoft.com/mssql/server:2025-latest
    ```
## Install MS SQL server in docker 
    ```bash
    docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Aa123456" -p 1433:1433 --name sql1 --hostname sql1 -d  mcr.microsoft.com/mssql/server:2025-latest
    ```
## Test connect SQL server 

## ORM Flask (from sqlalchemy.orm )
Object Relational Mapping

Ánh xạ 1 class (OOP)  model src/infrastructure/models --> Table in database 
Ánh xạ các mối quan hệ (Relational) -- Khoá ngoại CSDL 
(n-n): many to many 

@startuml
' Diagram Title
title Clean Architecture Sequence Diagram

' Define participants in order of appearance
actor Actor
participant "Web App"
participant "Controller"
participant "Services"
participant "Domain"
participant "infrastructure"
database "Database"

' --- Message Flow ---

' 1. Initial Request
Actor -> "Web App": Request
activate "Web App"

' 2. Forwarding to Controller
"Web App" -> "Controller"
activate "Controller"

' 3. Calling the Service Layer
"Controller" -> "Services"
activate "Services"

' 4. Interacting with the Domain Layer
"Services" -> "Domain"
activate "Domain"
note over Domain: Interfaces

' 5. Interacting with Infrastructure
"Domain" -> "infrastructure"
activate "infrastructure"
note over infrastructure: Class implement

' 6. Database Query
"infrastructure" -> "Database"
activate "Database"

' --- Response Flow (Return Messages) ---

' 7. Database returns data
"Database" --> "infrastructure"
deactivate "Database"

' 8. Infrastructure returns to Domain
"infrastructure" --> "Domain"
deactivate "infrastructure"

' 9. Domain returns to Services
"Domain" --> "Services"
deactivate "Domain"

' 10. Services returns to Controller
"Services" --> "Controller"
deactivate "Services"

' 11. Controller returns to Web App
"Controller" --> "Web App"
deactivate "Controller"

' 12. Final data rendering to Actor
"Web App" --> Actor
note left of "Web App"
  Render data
end note
deactivate "Web App"

@enduml
=======
