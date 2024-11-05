# R_AI

A data analysis application built with Django REST Framework and React.

## Backend & Frontend Setup

See [Backend README](backend/README.md) and [Frontend README](frontend/README.md) for detailed setup instructions.

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
