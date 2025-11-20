# interactive-lr1 Backend

## Prerequisites

- Python 3.11 or higher
- pip

## Setup

1. Install dependencies:
    pip install -r requirements.txt

2. Run unit tests:
    pytest tests/

3. Start the Flask server:
    bash run.sh

- The app runs on http://127.0.0.1:5000 and accepts requests from http://localhost:5173 via CORS.

## Files

- app.py — Main Flask app and API endpoints
- parser_core.py — Grammar parsing logic
- first_follow.py — FIRST/FOLLOW set computations
- lr1_builder.py — LR(1) automaton and table construction, parsing simulation
 - lr1_builder.py automaton and table construction, parsing simulation
- schemas.py — Pydantic models for request/response contracts
- exceptions.py — Custom error types
- tests/test_parser_core.py — Unit tests for grammar and parser logic
- requirements.txt — Dependencies
- run.sh — Development server runner

