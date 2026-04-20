# Nexus - Smart Event Companion 🚀

Nexus is an enterprise-grade AI matchmaking agent designed to route hackathon and tech conference attendees to the perfect physical meetup based on their current intent, vibe, and goals.

## 🔗 Live Application
**[Click here to view the live deployment on Google Cloud Run](https://nexus-app-1016175435508.asia-south1.run.app)**

## 🏗️ System Architecture
This project is built using a modern, serverless full-stack architecture:
* **AI Engine:** Google Cloud Vertex AI (`gemini-2.5-flash`) utilizing Chain-of-Thought reasoning to filter intents and handle hostile edge cases.
* **Backend:** FastAPI (Python) containerized with Docker.
* **Database:** PostgreSQL (Cloud SQL / AlloyDB) connected securely via `pg8000`.
* **Deployment:** Google Cloud Run (Fully serverless, autoscaling environment).
* **Frontend:** Vanilla JS with Tailwind CSS, served natively through the FastAPI backend.

## 🛡️ Security & Quality Standards
* **Environment Isolation:** All database credentials and GCP project variables are injected securely via Cloud Run Environment Variables.
* **Prompt Safety:** The AI model is strictly instructed with fallback mechanisms to handle non-relevant, hostile, or gibberish inputs smoothly.
* **Stateless Scaling:** The application is built to scale infinitely on Cloud Run without holding local states.
