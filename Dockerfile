FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir python-telegram-bot==13.7

COPY bot.py .

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import os; assert os.getenv('TELEGRAM_TOKEN') is not None, 'TELEGRAM_TOKEN not set'"

# Use environment variable
ENV TELEGRAM_TOKEN=""

CMD ["python3", "bot.py"]
