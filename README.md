# 🔮 Mystica — AI-Based Palmistry & Tarot Intelligence Platform

[![Next.js](https://img.shields.io/badge/Next.js-16.1-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB?logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-AI-EE4C2C?logo=pytorch)](https://pytorch.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4.0-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Mystica** is an enterprise-grade, multi-service AI intelligence platform that combines **Computer Vision Palmistry Analysis**, **Interactive AI Tarot Card Readings**, and **Personalized Predictive Insights**. Built with Next.js 16, FastAPI, PyTorch, MediaPipe, and Google Gemini AI, Mystica delivers real-time mystic guidance, palm line extractions, live consultations, and admin telemetry.

---

## 🚀 Key Features

- **🖐️ AI Palmistry Scanner & Line Extraction**:
  - Image preprocessing with OpenCV & MediaPipe hand landmarks tracking.
  - Automatic detection and feature measurement of major palm lines (*Heart Line, Head Line, Life Line, Fate Line*).
  - Neural feature mapping combined with Google Gemini Generative AI for deep palmistry insights.

- **🃏 Interactive AI Tarot Reading Engine**:
  - Multi-card spreads (*Single Card Daily Draw, 3-Card Past/Present/Future, Love & Career Spreads*).
  - Dynamic 3D card flipping micro-animations with Framer Motion.
  - Contextual AI interpretations customized to user profile and question context.

- **📊 Personal Insights & Analytics Dashboard**:
  - Historical reading logs, personal alignment tracking, and interactive growth charts via Recharts.
  - Exportable PDF reports powered by `jspdf` and `html2pdf.js`.

- **💬 Real-Time Live Consultations & Chat**:
  - Session history and interactive consultation booking.
  - Real-time notifications and real-time guidance channels.

- **🛡️ Admin & Operational Telemetry**:
  - Complete admin control panel (`/admin`) for user monitoring, reading usage metrics, system performance, and API logs.

---

## 🛠️ Technology Stack

| Domain | Technologies |
| :--- | :--- |
| **Frontend Framework** | Next.js 16 (App Router), React 19, TypeScript |
| **Styling & UI Components** | Tailwind CSS v4, Radix UI primitives, Lucide Icons, Framer Motion |
| **State & Data Fetching** | Zustand, TanStack React Query, React Hook Form, Zod |
| **Primary Backend** | Python FastAPI, Pydantic schemas, Uvicorn |
| **AI & Computer Vision Microservice** | PyTorch, OpenCV, MediaPipe, YOLO object tracking, Google Gemini AI (`@google/generative-ai`) |
| **Database & ORM** | PostgreSQL, Prisma ORM |
| **Containerization & Infra** | Docker, Docker Compose |

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    User([User Browser / Mobile]) <--> NextJS[Next.js 16 Frontend App]
    NextJS <--> FastAPI[FastAPI Main Backend]
    NextJS <--> Gemini[Google Gemini AI API]
    FastAPI <--> Postgres[(PostgreSQL Database)]
    FastAPI <--> PalmAI[Palmistry CV AI Microservice]
    PalmAI <--> MediaPipe[MediaPipe / OpenCV / PyTorch]
```

---

## 📁 Repository Structure

```text
Mystica/
├── src/                          # Next.js Frontend Application
│   ├── app/                      # App router (pages, admin, api routes, layout)
│   ├── components/               # UI components (Shadcn/Radix, card flip, palm canvas)
│   ├── hooks/                    # React custom hooks
│   └── lib/                      # Utilities, API client, state management
├── backend/                      # Main FastAPI Backend Service
│   ├── routers/                  # API endpoints (auth, readings, dashboard, admin, etc.)
│   ├── prisma/                   # Database schema & migrations
│   ├── main.py                   # FastAPI app entrypoint
│   └── requirements.txt          # Python dependencies
├── mini-services/                # Microservices Ecosystem
│   └── palmistry-ai/             # PyTorch & CV Palm Analysis Service
│       ├── models/               # ML weights & detection models
│       ├── main.py               # Vision API endpoint
│       └── requirements.txt      # CV & ML packages
├── docker-compose.yml            # Multi-container orchestration setup
└── README.md                     # Documentation
```

---

## ⚡ Quick Start Guide

### Prerequisites
- **Node.js** `>= 18.x`
- **Python** `>= 3.10`
- **Docker & Docker Compose** (Optional, for containerized run)

---

### 1. Running locally with Node.js & Python

#### Frontend Setup (Next.js)
```bash
# Navigate to the root directory
cd Mystica---An-AI-based-Palmistry-and-Tarot-Intelligence-Platform-main

# Install dependencies
npm install

# Start development server
npm run dev
```
*Frontend runs on `http://localhost:3000`*

#### Backend Setup (FastAPI)
```bash
cd backend

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --port 8000
```
*Backend API docs available at `http://localhost:8000/docs`*

#### Palmistry AI Microservice Setup
```bash
cd mini-services/palmistry-ai

# Activate venv & install dependencies
pip install -r requirements.txt

# Run service
python main.py
```
*Palmistry AI microservice runs on `http://localhost:8001`*

---

### 2. Running with Docker Compose 🐳

To launch the full stack (Frontend, Backend, AI Service, Database) in isolated containers:

```bash
docker-compose up --build
```

---

## 🔑 Environment Configuration

Create `.env.local` in the root frontend directory and `.env` in the backend directory:

```env
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_PALM_AI_URL=http://localhost:8001
GEMINI_API_KEY=your_google_gemini_api_key

# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost:5432/mystica_db
JWT_SECRET=your_jwt_secret_key
```

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<p center="text-align">Crafted with ✨ and AI Intelligence.</p>