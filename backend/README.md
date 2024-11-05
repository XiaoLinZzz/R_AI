# 🔧 Backend Setup

## ✨ Prerequisites

| Requirement         | Version       |
| ------------------- | ------------- |
| Python              | 3.x or higher |
| MongoDB             | Latest stable |
| Virtual Environment | Python venv   |

## 🚀 Installation & Setup

### 1️⃣ Virtual Environment Setup

Create and activate a virtual environment to isolate project dependencies:

```bash
# Create virtual environment
python -m venv myenv

# Activate virtual environment
# For Unix/macOS:
source ./myenv/bin/activate
# For Windows:
myenv\Scripts\activate
```

### 2️⃣ Dependencies Installation

Install all required packages:

```bash
pip install -r requirements.txt
```

### 3️⃣ Database Setup

Start MongoDB server:

```bash
# Using Homebrew on macOS
brew services start mongodb-community

# Check MongoDB status
brew services list
```

### 4️⃣ Database Configuration

Configure your database settings in `backend/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'your_database_name',
        'CLIENT': {
            'host': 'mongodb://localhost:27017/',
        }
    }
}
```

### 5️⃣ Database Migrations

Initialize and apply database migrations:

```bash
# Generate migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 6️⃣ Launch Server

Start the development server:

```bash
python manage.py runserver
```

🌐 The API will be available at `http://localhost:8000/api/`

## 📝 Development Notes

- Keep your virtual environment activated while working on the project
- Monitor MongoDB logs for any database issues
- Use `python manage.py createsuperuser` to create an admin user
- Check `requirements.txt` regularly for dependency updates

## 🔍 Useful Commands

| Command                          | Description           |
| -------------------------------- | --------------------- |
| `python manage.py shell`         | Opens Django shell    |
| `python manage.py dbshell`       | Opens database shell  |
| `python manage.py test`          | Runs test suite       |
| `python manage.py collectstatic` | Collects static files |

## ⚠️ Troubleshooting

- If MongoDB fails to start, check if the service is properly installed
- For migration errors, try removing migration files and recreating them
- Check MongoDB connection if database operations fail
