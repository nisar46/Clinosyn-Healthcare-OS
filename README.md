# Clinosyn Healthcare OS 🧬
> **STATUS: ✅ Completed | Independent Research Project**

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Ollama](https://img.shields.io/badge/AI-Llama3%20%2F%20Ollama-black?style=for-the-badge)
![SQLite](https://img.shields.io/badge/DB-SQLite-003B57?style=for-the-badge&logo=sqlite)

## ⚡ Executive Summary

**Clinosyn Healthcare OS** is the clinical intelligence top-layer that sits above the [OmniIngest ABDM 2.0](https://github.com/nisar46/OmniIngest-Clinical-Engine) pipeline.

It transforms the clean, ABDM-compliant data stored in `omniingest_FINAL.db` into actionable, AI-driven clinical insights — all **offline and privacy-first**, with no cloud API fees or data leakage risks.

> **Target User:** Doctors, Clinical Directors, and Hospital Executives.
> **NOT for:** Administrative staff (they use OmniIngest).

---

## 🏗️ Architecture Role

```
OmniIngest ABDM 2.0  ──saves──►  omniingest_FINAL.db  ──reads──►  Clinosyn Healthcare OS
(Back-office / Admin)             (Shared SQLite Vault)             (Clinical Staff / Doctors)
```

---

## 💎 Key Features

### 🧠 Offline GenAI — NL-to-SQL RAG Pipeline
- Local **Llama3** (via Ollama) — zero cloud dependency, zero patient data leakage.
- Converts natural language doctor queries into optimized SQLite commands.
- Native `json_extract()` querying directly against unstructured `payload_vault` columns.

### 📊 Clinical Analytics Terminal (Streamlit)
- **Modular vs Monolithic Options:** Features a heavily modularized `app.py` for scalable deployment and a standalone `clinosyn_app.py` for isolated monolithic testing.
- Real-time ingestion analytics and patient record monitoring.
- Active PII masking arrays for privacy compliance.
- **98.2%** high-integrity FHIR pipeline processing success metric.

### 🔒 DPDP Governance Suite
- Interactive Rule 8.3 cascading cryptographic **"Kill-Switch"**.
- Instantly severs downstream data access for DPDP Act compliance.

---

## 🛠️ Tech Stack

| Component | Technology |
|:---|:---|
| **UI / Dashboard** | Streamlit |
| **AI Engine** | LangChain + Llama3 (Ollama) |
| **Database** | SQLite (`omniingest_FINAL.db`) |
| **Query Layer** | NL-to-SQL RAG + `json_extract()` |
| **Compliance** | DPDP Act 2023 Rule 8.3 |

---

## 🔗 Companion Project
This project is part of the **Healthcare Suite** and is designed to work exclusively with:
👉 [OmniIngest Clinical Data Engine (ABDM 2.0)](https://github.com/nisar46/OmniIngest-Clinical-Engine)

---

## 👨‍💻 Author
**Nisar Ahmed** — Clinical Data Analyst | Healthcare Data Engineering
[LinkedIn](https://linkedin.com/in/nisar-ahmed-8440763a3) · [Portfolio](https://nisar46.github.io/portfolio)

> *"Doctors should query data in plain English. Clinosyn makes that real."*

---
*© 2026 Nisar Ahmed. Licensed under MIT.*
