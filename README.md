# R_AI

A data analysis application built with Django REST Framework and React.

## Backend Setup

### Prerequisites

- Python 3.x
- MongoDB
- Virtual Environment

### Installation

1. Create and activate the virtual environment:

```bash
python -m venv myenv
source ./myenv/bin/activate # For Unix/macOS
myenv\Scripts\activate # For Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start MongoDB server:

```bash
Using Homebrew on macOS
brew services start mongodb-community
```

4. Configure database:

Update the MongoDB connection settings in `backend/settings.py` if needed:

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

5. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

6. Start the development server:

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## Frontend Setup

1. Navigate to frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
yarn install
```

3. Start development server:

```bash
yarn dev
```

## API Endpoints

- `POST /api/upload/`: Upload and analyze data files (CSV/Excel)
- `GET /api/analysis/<analysis_id>/`: Retrieve analysis results

## Features

- File upload and analysis
- Automatic data type inference
- Support for CSV and Excel files
- Real-time data visualization
- MongoDB integration for data persistence

## Tech Stack

- Backend:
  - Django
  - Django REST Framework
  - Pandas
  - MongoDB (with Djongo)
- Frontend:
  - React
  - Vite
  - Ant Design
  - Axios
