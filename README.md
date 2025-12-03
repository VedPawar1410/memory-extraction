# AI Memory & Personality Engine

A Streamlit-powered prototype that extracts structured memory from chat conversations and rewrites AI responses with personalized personas using Google Gemini.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Features

- **Memory Extraction** — Analyze chat history to extract:
  - **Facts** — Name, location, occupation, relationships
  - **Preferences** — Likes, dislikes, choices
  - **Emotional Patterns** — Communication style, behavioral tendencies

- **Personality Rewriting** — Transform generic AI responses into personalized messages with different personas:
  - Friendly & Encouraging
  - Professional & Formal
  - Casual & Humorous
  - Empathetic & Supportive
  - And more...

## Quick Start

### Prerequisites

- Python 3.9+
- [Google Gemini API Key](https://aistudio.google.com/apikey)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/memory-extraction.git
cd memory-extraction

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Run the app
streamlit run app.py
```

### Using Docker

```bash
# Build the image
docker build -t memory-extraction-app .

# Run the container
docker run -p 8501:8501 -e GOOGLE_API_KEY=your_api_key_here memory-extraction-app
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

## Project Structure

```
memory-extraction/
├── app.py                 # Streamlit UI application
├── memory_engine.py       # Memory extraction module
├── personality_engine.py  # Persona-based response rewriting
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── render.yaml            # Render deployment config
└── README.md
```

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Streamlit** | Web UI framework |
| **Google Gemini 2.0 Flash** | LLM for extraction & rewriting |
| **LangChain** | LLM orchestration |
| **Pydantic** | Structured output validation |

## Usage

1. **Enter your API Key** — Paste your Google Gemini API key in the sidebar
2. **Paste Chat History** — Use the sample conversation or paste your own
3. **Click "Analyze User"** — Extract structured memory from the conversation
4. **View Profile** — See extracted facts, preferences, and emotional patterns
5. **Test Personality** — Select a persona and transform a generic response

## Deploy to Render

1. Fork this repository
2. Click the "Deploy to Render" button above
3. Add your `GOOGLE_API_KEY` as an environment variable
4. Deploy!

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Your Google Gemini API key | Yes |

## License

MIT License — feel free to use this project for learning and experimentation.

---

<p align="center">
  Built with ❤️ using Streamlit & Google Gemini
</p>
