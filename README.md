# BlueVerify AI

BlueVerify AI is a web-based restoration claim verification system designed to improve the credibility and transparency of environmental restoration claims.

The system allows organizations to submit restoration claims with location, ecosystem, area, restoration date, and supporting evidence. Submitted claims are automatically checked for potential duplicate locations and analyzed for verification concerns before being reviewed through an administrative dashboard.

## Features

* Restoration claim submission
* Location-based claim verification
* Geographic duplicate-risk detection
* Automated evidence analysis
* Credibility and risk assessment
* Admin dashboard for reviewing submitted claims
* Claim status tracking
* Responsive web interface

## Tech Stack

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite

### Verification

* Geographic distance calculation
* Automated claim/evidence analysis

## Project Structure

```text
blueverify-ai/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── blueverify.db
│
├── frontend/
│   ├── index.html
│   ├── submit.html
│   ├── admin.html
│   ├── script.js
│   └── style.css
│
└── README.md
```

## How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/irin46/blueverify-ai.git
cd blueverify-ai
```

### 2. Open the Backend Folder

```bash
cd backend
```

### 3. Create a Virtual Environment

On Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the Backend

Run:

```bash
uvicorn app.main:app --reload
```

The backend will start at:

```text
http://127.0.0.1:8000
```

The API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### 6. Open the Frontend

Open the following file in your browser:

```text
frontend/index.html
```

For the best experience, serve the frontend using a local web server such as VS Code Live Server.

## Application Flow

```text
User
  │
  ▼
Submit Restoration Claim
  │
  ▼
FastAPI Backend
  │
  ├── Validate Claim Data
  │
  ├── Check Geographic Duplicate Risk
  │
  └── Analyze Evidence
  │
  ▼
Database
  │
  ▼
Admin Dashboard
  │
  ▼
Review Verification Results
```

## Claim Verification

Each submitted claim contains information such as:

* Organization
* Location coordinates
* Ecosystem type
* Restoration area
* Restoration date
* Supporting evidence

The system uses geographic proximity checks to identify claims that may represent duplicate or overlapping submissions.

The evidence and claim details are also analyzed to identify potential inconsistencies and verification concerns.

## API

### Submit a Claim

```http
POST /api/submissions
```

### View API Documentation

```text
http://127.0.0.1:8000/docs
```

The interactive API documentation can be used to test the available endpoints.

## Future Improvements

* Satellite-based vegetation analysis
* More advanced evidence verification
* Image-based restoration evidence analysis
* Role-based authentication
* PostgreSQL deployment
* Cloud deployment
* Blockchain-based claim and credit records

## Sustainability Goal

BlueVerify AI supports environmental restoration verification by helping improve the transparency and reliability of restoration claims.

The project primarily aligns with:

**UN Sustainable Development Goal 13 — Climate Action**

## Author

Developed as a sustainability-focused software project combining web development, backend APIs, geographic verification, and automated analysis.
