# 🖼️ Image Thumbnail API

A robust FastAPI application for uploading images and automatically generating thumbnails in multiple sizes using background tasks. This project demonstrates core backend skills including authentication, file handling, database management, and asynchronous processing.

## ✨ Features

- **🔐 User Authentication**: Secure registration and login using JWT (JSON Web Tokens).
- **📤 Image Upload**: Validate and upload images (JPEG, PNG, etc.) with size limits.
- **⚡ Automatic Thumbnails**: Generates thumbnails in three sizes (200x200, 500x500, 800x800) in the background.
- **📂 File Management**: Securely stores images and thumbnails on the server.
- **📊 Status Tracking**: Track the generation status (pending, ready, failed) of each thumbnail.
- **🗑️ Cleanup**: Deleting an image automatically removes the original file and all associated thumbnails from the disk.
- **📥 Download**: Securely download original images.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [SQLAlchemy](https://www.sqlalchemy.org/) (SQLite/PostgreSQL)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Image Processing**: [Pillow (PIL)](https://python-pillow.org/)
- **Authentication**: [Python-JOSE](https://python-jose.readthedocs.io/en/latest/) (JWT)
- **Server**: [Uvicorn](https://www.uvicorn.org/)

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip (Python package manager)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/DavidDanso/image-thumbnail-api.git
    cd image-thumbnail-api
    ```

2.  **Create a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables**
    Create a `.env` file in the root directory (optional, or configure in `config.py`):
    ```env
    SECRET_KEY=your_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

5.  **Run the application**
    ```bash
    uvicorn app.main:app --reload
    ```

The API will be available at `http://127.0.0.1:8000`.

### Database Migrations

This project uses Alembic for database migrations.

1.  **Initialize migrations** (if starting fresh)

    ```bash
    alembic init alembic
    ```

2.  **Create a migration** (after changing models)

    ```bash
    alembic revision --autogenerate -m "Describe your changes"
    ```

3.  **Apply migrations**

    ```bash
    alembic upgrade head
    ```

## 📖 API Documentation

FastAPI provides automatic interactive documentation. Once the server is running, visit:

-   **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
-   **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Key Endpoints

#### Auth
-   `POST /api/auth/register`: Register a new user.
-   `POST /api/auth/login`: Login and get an access token.

#### Images
-   `POST /api/images/upload`: Upload an image (Requires Auth).
-   `GET /api/images/upload`: List all your uploads.
-   `GET /api/images/{id}`: Get image metadata and thumbnail details.
-   `GET /api/images/{id}/file`: Download the original image file.
-   `DELETE /api/images/{id}`: Delete an image and its thumbnails.

#### Thumbnails
-   `GET /api/images/thumbnails/{id}`: Check the status of a specific thumbnail.

## 📂 Project Structure

```
.
├── app
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas (Request/Response)
│   ├── database.py          # Database connection
│   ├── oauth2.py            # Authentication logic
│   ├── utils.py             # Utility functions (hashing)
│   └── routers
│       ├── auth.py          # Auth routes
│       ├── users.py         # User management routes
│       ├── uploads.py       # Image upload & handling routes
│       └── thumbnail_service.py # Image processing logic
├── uploads                  # Directory for stored images
│   └── thumbnails           # Directory for generated thumbnails
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the project
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request
