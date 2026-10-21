# Bookly

Bookly is a basic project I’m building to practise Python backend development with **FastAPI**. The main goal is to learn how a FastAPI application is structured and get more comfortable working with the tools commonly used in Python backend development.

This is a learning project, so I’m focusing on understanding the fundamentals and improving it as I learn.

## Tech Stack

The project environment includes the following tools and libraries:

- **Python** — programming language
- **FastAPI** — building the web API
- **Uvicorn** — running the application locally
- **SQLAlchemy / SQLModel** — database-related ORM tools available in the environment
- **Pydantic** — data validation and settings support
- **PostgreSQL-related drivers** — database connectivity libraries are present in the dependencies
- **PyJWT** — JWT-related functionality
- **Passlib / bcrypt** — password-hashing libraries
- **Pytest** — testing
- **python-dotenv / pydantic-settings** — configuration support

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/dube-codes/Bookly.git
cd bookly
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

Make sure `requirements.txt` is in the project directory, then run:

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

From the project root, run:

```bash
uvicorn src:app --reload
```

### 5. Open the API documentation

Once the server is running, visit:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

These pages are FastAPI's interactive documentation interfaces. The available routes depend on what is implemented in the project.

## Configuration

If the application requires environment variables or a database connection, configure them according to the settings expected by the project code. Do not commit passwords, secret keys, or other private credentials to the repository.

## What I’m Learning

Through Bookly, I’m practising Python backend development and learning how to work with FastAPI and its surrounding ecosystem. I plan to build my understanding step by step as I work through the project.

## Current Status

Bookly is a practice project for learning FastAPI. This README describes the project at a high level and does not claim that features are complete unless they are implemented in the code.

## License

No license has been specified yet.
