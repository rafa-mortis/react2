# Basic Login App

A simple React frontend with Python Flask backend for basic login functionality.

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the Flask server:
   ```bash
   python app.py
   ```
   The backend will run on http://localhost:5000

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```
   The frontend will run on http://localhost:3000

## Usage
1. Make sure both servers are running
2. Open http://localhost:3000 in your browser
3. Enter any username and password (basic authentication accepts any non-empty credentials)
4. Click Login to see the success page

## Features
- Basic login form with username and password
- Uses React useState and useEffect hooks
- Simple success page after login
- Logout functionality
- Basic error handling
