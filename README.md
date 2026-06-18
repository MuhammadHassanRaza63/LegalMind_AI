# LegalMind AI

LegalMind AI is a lightweight Flask web application that provides a Pakistani-focused legal assistant powered by local document embeddings and external language models. The project demonstrates ingestion of local PDF law-books, embedding them into a Chroma vector store, and answering user queries via a Cohere chat model (configurable). The app includes user authentication (signup/login) and a simple chat UI.

## Features

- User signup / login with secure password hashing
- Chat interface that queries a local vector store for contextual legal answers
- PDF ingestion and text chunking for semantic search
- Environment-driven configuration for API keys and secrets
- Ready-to-run local development setup with `requirements.txt`

## Architecture / Files of Interest

- `app.py` — Flask application, routes, user model and web UI entrypoint
- `backend/engine.py` — Document loading, text-splitting, embeddings, vector store, and LLM wrapper
- `templates/` — Jinja2 templates for `login`, `signup`, `index` and `chat`
- `data/` — Example PDF documents PPC, consumer_act,Constitution of pak. 
- `db_legal/` — Persisted Chroma vector store (ignored by git)
- `instance/` — Local SQLite DB for user accounts (ignored by git)
- `.env.example` — Example environment variables (copy to `.env`)
- `requirements.txt` — Pinning of the current environment packages

## Prerequisites

- Python 3.10+ (tested with CPython 3.14)
- Git (for cloning and pushing)
- Recommended: create a Python virtual environment
- Valid API keys for the external services you plan to use (see Configuration)

## Local Setup (recommended)

1. Clone the repository (if not already):

```bash
git clone https://github.com/MuhammadHassanRaza63/LegalMind_AI.git
cd LegalMind_AI
```

2. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
# or on macOS / Linux: source venv/bin/activate
```

3. Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Create your `.env` configuration from the example and fill in real keys (DO NOT commit `.env`):

```powershell
copy .env.example .env
# Edit .env with your API keys and secrets
```

5. Ensure folders `instance/` and `db_legal/` are writable by your user — both are ignored from Git and used at runtime.

6. Run the app:

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Configuration (environment variables)

Set the following variables in your local `.env` (or environment):

- `SECRET_KEY` — Flask secret key (change from default)
- `DATABASE_URL` — SQLAlchemy URL (default: `sqlite:///instance/users.db`)
- `GOOGLE_API_KEY` — (optional) API key if using Google generative embeddings
- `COHERE_API_KEY` — (optional) Cohere API key for chat model
- `COHERE_CHAT_MODEL` — (optional) Cohere chat model name (defaults are present in code)

Important: `.env` is in `.gitignore`. Never commit real API keys or secrets.

## How It Works (brief)

1. On first run (if `db_legal/` is absent), the app loads PDFs from `data/`, splits them into chunks using `RecursiveCharacterTextSplitter`, computes embeddings, and writes a Chroma vector store to `db_legal/`.
2. When a user asks a question, the app searches the vector store for relevant chunks and sends a prompt (context + question) to the configured LLM wrapper (`ChatCohere`) to generate an answer.

## Security & Privacy Notes

- The repository intentionally avoids committing sensitive files: `instance/`, `db_legal/`, and `.env` are ignored in `.gitignore`.
- If you accidentally committed secrets previously, rotate those keys immediately and remove them from history.
- This project runs in development mode by default. For production, run under a WSGI server (e.g., `gunicorn`) behind TLS and follow best practices for secret management.
  
## Troubleshooting

- `sqlite3.OperationalError: unable to open database file` — ensure `instance/` exists and is writable.
- Missing API key warnings — set `GOOGLE_API_KEY` and/or `COHERE_API_KEY` in `.env` when using those services.
- LangChain/Chroma warnings — the project pins particular client packages; if you upgrade `langchain`, update imports and usage accordingly.

## Contributing

Contributions are welcome. Common contributions include:

- Bug fixes and dependency updates
- Improving prompts and response handling in `backend/engine.py`
- Adding tests or CI configuration

Please open issues or PRs on the repository and avoid including secrets in PRs.

## License

This project does not include a license file by default. Add a `LICENSE` file to the repository if you want to clarify reuse terms.

## Contact

Project owner: Muhammad Hassan Raza (repo owner on GitHub)
Email: hassan638292@gmail.com
