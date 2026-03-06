# 🏗️ Requirements Architect

> **AI-Native Business Analysis Tool** — Transforms raw stakeholder transcripts or regulatory documents into structured technical specifications with user stories, edge cases, and developer critique.

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 🎯 What It Does

Requirements Architect takes **unstructured input** (meeting transcripts, regulatory docs, stakeholder notes) and produces **production-ready specs**:

- ✅ **User Stories** with acceptance criteria
- ✅ **Edge Cases** and failure modes
- ✅ **Developer Critique** with technical feasibility notes
- ✅ **Export** to PDF, DOCX, and plain text

## 🧠 How It Works

```
Stakeholder Transcript → AI Analysis → Structured Spec
         ↓                    ↓              ↓
  Paste or upload      Multi-provider     User stories,
  raw meeting notes    LLM fallback       edge cases,
  or regulatory docs   (Claude/GPT/       developer
                        Gemini)           critique
```

The tool uses **smart provider fallback** — it tries the best available AI provider (Anthropic Claude → OpenAI GPT → Google Gemini) and falls back automatically if one fails.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- At least one API key: Anthropic, OpenAI, or Google Gemini

### Installation

```bash
git clone https://github.com/trithanhalan/requirements-architect.git
cd requirements-architect
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```env
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

You only need **one** of the three keys. The tool auto-detects which providers are available.

### Run the Streamlit UI

```bash
streamlit run requirements_architect_ui.py
```

### Run CLI Mode

```bash
python requirements_architect.py
```

## 📸 Features

| Feature | Description |
|---|---|
| **Multi-Provider AI** | Automatic fallback across Claude, GPT, and Gemini |
| **Wealthsimple-Inspired UI** | Clean, professional dark theme |
| **Export Options** | PDF, DOCX, TXT, and Markdown |
| **Regulatory Mode** | Handles compliance documents (SOX, GDPR, etc.) |
| **Stakeholder Mode** | Processes meeting transcripts and notes |

## 🛠️ Tech Stack

- **Backend:** Python, LangChain-compatible architecture
- **Frontend:** Streamlit with custom Wealthsimple-inspired theme
- **AI Providers:** Anthropic Claude, OpenAI GPT-4, Google Gemini
- **Export:** ReportLab (PDF), python-docx (DOCX)

## 📁 Project Structure

```
requirements-architect/
├── requirements_architect.py      # Core engine (CLI mode)
├── requirements_architect_ui.py   # Streamlit UI
├── requirements.txt               # Dependencies
├── .env.example                   # API key template
└── README.md                      # This file
```

## 🤝 Contributing

Contributions welcome! Please open an issue first to discuss proposed changes.

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built by <a href="https://github.com/trithanhalan">Alan</a> — Senior BA turned AI builder
</p>
