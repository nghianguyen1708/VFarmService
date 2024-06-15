VFarmService FastAPI Application
VFarmService is a FastAPI-based web application for managing chat boxes and messages between users.

Features
User authentication and token-based access control.
CRUD operations for users, chat boxes, and messages.
Secure password hashing using bcrypt.
PostgreSQL database backend with SQLAlchemy ORM.
Installation
To run this application locally, follow these steps:

Clone the repository:

bash
Sao chép mã
git clone https://github.com/yourusername/VFarmService.git
cd VFarmService
Set up virtual environment (optional but recommended):

bash
Sao chép mã
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install dependencies:

bash
Sao chép mã
pip install -r requirements.txt
Set up PostgreSQL database:

Install PostgreSQL and create a database.
Update database connection details in app/database.py.
Run the application:

bash
Sao chép mã
uvicorn app.main:app --reload
Access the API documentation:

Open your browser and go to http://127.0.0.1:8888/docs to view the Swagger UI.