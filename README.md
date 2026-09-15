# IPC Legal Chatbot

A RAG-based AI legal assistant for exploring the Indian Penal Code (IPC).

## 🚀 Live Demo

https://ipcchatbot.streamlit.app

## 📌 Overview

IPC Legal Chatbot is an AI-powered legal information assistant designed
to help users explore the Indian Penal Code through a conversational
interface.

The project covers 511 IPC sections and uses multiple search strategies
to retrieve relevant legal information.

## ✨ Features

- Search across IPC sections
- Keyword-based search
- Exact-match search
- Chapter-wise search
- RAG-based response generation
- Streamlit web interface
- Fast retrieval and response generation

## 🛠️ Tech Stack

- Python
- Streamlit
- RAG
- Natural Language Processing

## 🧠 How It Works

User Query
    ↓
Query Processing
    ↓
Search / Retrieval
    ↓
Relevant IPC Sections
    ↓
Response Generation
    ↓
Answer

## 📊 Project Details

- IPC sections covered: 511
- Legal keywords indexed: 2,205+
- Target response time: under 3 seconds

## 💻 Installation

### Clone the repository

```bash
git clone https://github.com/Vasheegaran/ipc-chatbot.git
cd ipc-chatbot

pip install -r requirements.txt

streamlit run app.py
