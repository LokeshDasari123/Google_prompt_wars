# 🚀 Nexus – Smart Event Companion

Nexus is an AI-powered matchmaking system built for hackathons and tech conferences.  
It intelligently connects attendees to the most relevant physical meetups based on their intent, goals, and real-time context.

---

## 🔗 Live Demo
👉 https://nexus-app-1016175435508.asia-south1.run.app/

---

## 🎯 Problem

At large tech events, attendees often struggle to:
- Find relevant networking opportunities  
- Discover meetups aligned with their goals  
- Navigate overwhelming event schedules  
- Adapt plans based on changing intent  

---

## 💡 Solution

Nexus solves this using **AI-powered intent understanding**:

- Users describe what they want in natural language  
- The system analyzes intent using **Google Vertex AI (Gemini)**  
- It evaluates all available meetups  
- Returns the **best match + personalized reasoning**

---

## 🧠 Key Features

- 🔍 Natural language intent detection  
- 🎯 AI-powered meetup recommendation  
- 🛡️ Safe fallback for invalid/hostile inputs  
- ⚡ Real-time matchmaking  
- 🌐 Clean and accessible frontend  
- 📡 RESTful API design  
- 🧪 Automated test coverage  

---

## 🏗️ Tech Stack

### Backend
- FastAPI (Python)
- SQLAlchemy (ORM)
- PostgreSQL (Cloud SQL)

### AI Engine
- Google Cloud Vertex AI  
- Gemini 2.5 Flash  
- Chain-of-Thought reasoning approach  

### Frontend
- HTML + Tailwind CSS  
- Vanilla JavaScript  

### Deployment
- Docker  
- Google Cloud Run (serverless, autoscaling)

---

## 📡 API Endpoints

### 👤 User
- `POST /api/v1/users/`  
  Create a user profile with interests

### 🤖 Matchmaking
- `POST /api/v1/match/`  
  Get AI-powered meetup recommendation

### 📍 Meetups
- `GET /api/v1/meetups/`  
  List all meetups  

- `GET /api/v1/meetups/{id}`  
  Get specific meetup  

### ❤️ Health
- `GET /health`  
  Service health check  

---

## 🧪 Testing

Run tests locally:

```bash
pytest backend/tests
