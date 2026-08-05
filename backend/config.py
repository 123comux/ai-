"""Backend configuration."""

import os
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).parent

# Data directories
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
KNOWLEDGE_BASE_DIR = BASE_DIR / "data" / "knowledge_base"

# Ensure directories exist
for d in [RAW_DIR, PROCESSED_DIR, KNOWLEDGE_BASE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Server config
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Dataset config
FIREWEB_EDU_SAMPLE = "sample-10BT"  # Can also use "sample-100BT", "sample-350BT"
FIREWEB_EDU_MAX_ROWS = 1000  # Limit for local processing

QVAC_GENESIS_MAX_ROWS = 5000

STUDYCHAT_MAX_ROWS = 16851  # Full dataset

# CORS (allow Taro dev server + Web Preview + Cloud IDE + any port)
CORS_ORIGINS = [
    "null",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:57434",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:57434",
    "http://127.0.0.1:8000",
    "https://trae.mobile.volcapp.com",
]
CORS_ORIGIN_REGEX = r"https://.*\.(mobile\.volcapp\.com|volceapi\.com|apigateway.*\.volceapi\.com)"