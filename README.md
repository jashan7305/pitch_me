# PitchMe

PitchMe generates client-specific health-insurance presentations. Enter a company name and select one of the bundled policies, or upload a custom policy PDF. The app researches the company, retrieves relevant policy evidence, creates a PowerPoint pitch, and independently checks the pitch claims against the policy source.

## Features

- Company research using Google results through SerpAPI
- Grounded pitch generation with Gemini
- Bundled policy documents for ABHI, Care Health, HDFC ERGO, and Niva Bupa
- Custom policy PDF upload
- Claim-by-claim policy audit
- Downloadable client pitch (`.pptx`) and audit report (`.docx`)

## Requirements

- Docker with Docker Compose
- A Gemini API key
- A SerpAPI key

## Setup with Docker Compose

From the project root:

```bash
cp .env.example .env
```

Add your API keys to `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
SERPAPI_API_KEY=your_serpapi_api_key
```

Start the app:

```bash
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000).

Stop the app with:

```bash
docker compose down
```

Generated presentations and audit reports are saved in `backend/storage/generated`.
