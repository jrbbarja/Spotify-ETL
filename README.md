# 🎧 Spotify Automated ETL Pipeline & Data Warehouse

## 📖 Project Overview
This project is an end-to-end, automated Data Engineering solution designed to continuously track and analyze personal music consumption. It extracts raw listening data from the Spotify Web API, transforms it into a relational schema using Python, and securely loads it into a cloud-hosted PostgreSQL database. 

The pipeline is designed to be **idempotent**, utilizing SQL `ON CONFLICT` constraints to seamlessly handle duplicate records during scheduled batch runs without manual intervention. The backend data warehouse is then connected to a live Power BI dashboard to serve actionable, time-series insights.

## 🛠️ Architecture & Tech Stack
* **Extraction:** Python 3, `spotipy`, Spotify OAuth 2.0
* **Transformation:** `pandas` (JSON flattening, timestamp normalization, data cleansing)
* **Loading:** `sqlalchemy`, PostgreSQL (Supabase cloud hosting)
* **Orchestration:** Windows Task Scheduler (Batch automation)
* **Analytics/BI:** Power BI Desktop & Power BI Service

## ✨ Core Pipeline Features
* **Live API Integration:** Securely authenticates and requests the latest user listening history.
* **Complex Data Wrangling:** Flattens highly nested JSON responses into clean, tabular formats.
* **Fault-Tolerant Loading:** Utilizes `ON CONFLICT DO NOTHING` SQL logic to gracefully skip duplicate songs and only append genuinely new listening events to the database.
* **Automated Execution:** Runs entirely hands-free via scheduled local batch execution, keeping the downstream dashboard perpetually up-to-date.
