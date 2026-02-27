# Titanic Chat Agent 🚢🤖

An intelligent chat agent for the Titanic dataset powered by **FastAPI**, **Streamlit**, **LangGraph**, **LangChain**, and **Groq (`llama-3.3-70b-versatile`)**.

## 🌟 Features

- **Conversational AI:** Ask questions about the Titanic dataset (e.g., "What was the survival rate of 1st class passengers?") and get accurate, context-aware answers.
- **FastAPI Backend:** Secure, and asynchronous API backend. 
- **Streamlit Frontend:** Clean, interactive, and user-friendly chat UI.
- **LangGraph Integration:** Intelligent routing and state-managed agent workflows using LangGraph and LangChain.
- **Local & Dockerized Deployment:** Easily run locally or spin up the entire stack using Docker and Docker Compose.
- **Interactive API Docs:** Built-in Scalar API reference UI.

---

## 🏗️ Architecture

1. **Backend (FastAPI):**
   - Loads the Titanic dataset into memory efficiently on startup.
   - Hosts the LangGraph agent built using Groq's high-performance LLMs.
   - Provides clear REST endpoints for the chat interface.
   - Replaces traditional Swagger UI with modern **Scalar API documentation**.

2. **Frontend (Streamlit):**
   - Sends user messages to the backend.
   - Renders the chat history nicely in the browser.

---

## ⚙️ Prerequisites

- **Docker** and **Docker Compose** installed (recommended for easy setup).
- A [Groq API Key](https://console.groq.com/keys) to power the LLM.

---

## 🚀 Quickstart via Docker Compose (Recommended)

The easiest way to run both the frontend and backend is using Docker Compose.

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd titanic_agent
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   MODEL_NAME=llama-3.3-70b-versatile
   ```

3. **Start the application:**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the Application:**
   - **Chat UI (Streamlit):** [http://localhost:8501](http://localhost:8501)
   - **Backend API:** [http://localhost:8000](http://localhost:8000)
   - **Scalar API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💻 Running Locally (Without Docker)

You can also run the application using a Python virtual environment.

1. **Install Dependencies:**
   Make sure you have Python 3.9+ installed.
   ```bash
   pip install -r requirements.txt
   ```

2. **Set the required environment variable:**
   ```bash
   export GROQ_API_KEY="your_API_key"
   ```

3. **Use the start script:**
   The `start.sh` script runs both the backend and frontend concurrently.
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
   *(Alternatively, run `uvicorn app.main:app` and `streamlit run frontend/streamlit_app.py` in separate terminals).*

---

## 📁 Project Structure

```text
titanic_agent/
├── app/                  # FastAPI Application and LangGraph Agent logic
│   ├── agent/            # LangGraph nodes and builder
│   ├── core/             # Configuration and utilities
│   ├── routes/           # API Endpoints
│   ├── services/         # Data loading and business logic
│   └── main.py           # FastAPI entry point
├── frontend/             # Streamlit application
│   ├── Dockerfile        # Dockerfile specifically for the frontend
│   └── streamlit_app.py  # Chat UI code
├── data/                 # Directory containing the Titanic CSV
├── Dockerfile            # Multi-stage or single-container Dockerfile
├── docker-compose.yml    # Docker services orchestration
├── docker-compose.prod.yml # Production-ready Compose overrides
├── requirements.txt      # Root Python dependencies
└── start.sh              # Local development startup script
```

## 📜 License

[MIT License](LICENSE)
