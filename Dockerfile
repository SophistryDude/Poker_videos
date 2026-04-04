FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir flask gunicorn numpy

COPY stake_move_model.py .
COPY leak_analysis.py .
COPY generate_profiles.py .
COPY synthetic_players_100k.csv .
COPY poker_app/ ./poker_app/

EXPOSE 5001

CMD ["gunicorn", "poker_app.app:app", "--bind", "0.0.0.0:5001", "--workers", "2", "--timeout", "120"]
