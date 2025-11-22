# Quickstart: GeoMind AI Core

This document provides a brief overview of how to get started with the GeoMind AI Core feature.

## Architecture Overview

The system is composed of two main components:

1.  **Backend**: A FastAPI (Python) application that handles:
    *   Natural Language Processing (NLP) and understanding.
    *   SQL generation and validation.
    *   Secure communication with the Oracle OpenWorks database.
    *   User authentication and session management.

2.  **Frontend**: A Next.js (React) single-page application that provides the user interface for the chat functionality.

## Getting Started

### Backend

1.  **Prerequisites**: Python 3.11.
2.  **Installation**: `pip install -r requirements.txt`
3.  **Configuration**: Set up environment variables for database connection, Auth0, etc., in a `.env` file.
4.  **Running**: `uvicorn src.main:app --reload`

### Frontend

1.  **Prerequisites**: Node.js 20.x, npm for package management.
2.  **Installation**: `npm install`
3.  **Configuration**: Set up environment variables for the backend API URL, etc., in a `.env.local` file.
4.  **Running**: `npm run dev`
