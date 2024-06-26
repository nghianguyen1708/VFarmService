# VFarmService FastAPI Application

VFarmService is a FastAPI-based web application for managing chat boxes and messages between users.

## Features

- User authentication and token-based access control.
- CRUD operations for users, chat boxes, and messages.
- Secure password hashing using bcrypt.
- PostgreSQL database backend with SQLAlchemy ORM.

## Installation

To run this application locally, follow these steps:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/VFarmService.git
    cd VFarmService
    ```

2. **Set up a virtual environment (optional but recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  
    ```
   On Windows use:

    ```bash
    venv\Scripts\activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up PostgreSQL database:**

   **Option 1: Manual Setup**

    - Install PostgreSQL and create a database.
    - Update the database connection details in `app/database.py`.

   **Option 2: Using Docker**

    - Ensure you have Docker installed and running.
    - Use the provided `docker-compose.yml` file to set up PostgreSQL:

        ```bash
        docker-compose up -d
        ```

    - Update the database connection details in `app/database.py` to match the Docker configuration.

5. **Run database migrations with Alembic:**

    ```bash
    alembic upgrade head
    ```

6. **Run the application:**

    ```bash
    uvicorn app.main:app --reload --port 8888
    ```

7. **Access the API documentation:**

   Open your browser and go to [http://127.0.0.1:8888/docs](http://127.0.0.1:8888/docs) to view the Swagger UI.