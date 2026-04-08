# ==================== .env.example ====================
# Copy this file to .env and fill in your actual values

# Backend Configuration
FLASK_APP=edulrew_backend.py
FLASK_ENV=development
DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///edulrew.db
# For MySQL: DATABASE_URL=mysql+pymysql://user:password@localhost:3306/edulrew
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost:5432/edulrew

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production-12345

# Fast2SMS Configuration (for SMS alerts)
FAST2SMS_API_KEY=your_fast2sms_api_key_here

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=5000

# Frontend Configuration
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_ENVIRONMENT=development

# ==================== requirements.txt ====================
Flask==2.3.0
Flask-SQLAlchemy==3.0.5
Flask-CORS==4.0.0
Flask-JWT-Extended==4.5.2
Werkzeug==2.3.0
python-dotenv==1.0.0
requests==2.31.0
pandas==1.5.3
numpy==1.24.3
scikit-learn==1.2.2
joblib==1.2.0
shap==0.42.1
matplotlib==3.7.1
gunicorn==21.2.0
psycopg2-binary==2.9.6
PyMySQL==1.1.0

# ==================== package.json ====================
{
  "name": "edulrew-frontend",
  "version": "1.0.0",
  "description": "EduDew - Rural Student Dropout Early Warning System Frontend",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.4.0",
    "recharts": "^2.8.0",
    "react-router-dom": "^6.14.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "devDependencies": {
    "react-scripts": "5.0.1"
  }
}

# ==================== docker-compose.yml ====================
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: edulrew-mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: edulrew
      MYSQL_USER: edulrew_user
      MYSQL_PASSWORD: edulrew_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - edulrew_network

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: edulrew-backend
    environment:
      DATABASE_URL: mysql+pymysql://edulrew_user:edulrew_password@mysql:3306/edulrew
      FLASK_ENV: production
      JWT_SECRET_KEY: your-secret-key-here
    ports:
      - "5000:5000"
    depends_on:
      - mysql
    networks:
      - edulrew_network
    volumes:
      - ./models:/app/models

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: edulrew-frontend
    environment:
      REACT_APP_API_URL: http://localhost:5000/api
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - edulrew_network

volumes:
  mysql_data:

networks:
  edulrew_network:
    driver: bridge

# ==================== Dockerfile.backend ====================
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY edulrew_backend.py .
COPY .env .

# Create models directory
RUN mkdir -p models

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "edulrew_backend:app"]

# ==================== Dockerfile.frontend ====================
FROM node:18-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]

# ==================== nginx.conf ====================
server {
    listen 3000;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        try_files $uri /index.html;
    }

    location /api {
        proxy_pass http://backend:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    error_page 404 /index.html;
}

# ==================== Makefile ====================
.PHONY: help setup install run-backend run-frontend run-docker test clean

help:
	@echo "EduDew Development Commands"
	@echo "============================"
	@echo "make setup              - Initial setup"
	@echo "make install            - Install dependencies"
	@echo "make run-backend        - Run backend server"
	@echo "make run-frontend       - Run frontend development server"
	@echo "make run-docker         - Run with Docker Compose"
	@echo "make test               - Run tests"
	@echo "make clean              - Clean up"

setup:
	cp .env.example .env
	python -m venv venv
	source venv/bin/activate || . venv/Scripts/activate

install:
	pip install -r requirements.txt
	cd frontend && npm install

run-backend:
	python edulrew_backend.py

run-frontend:
	cd frontend && npm start

run-docker:
	docker-compose up -d

test:
	pytest tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf venv/
	rm -rf frontend/node_modules/
	rm -rf frontend/build/
