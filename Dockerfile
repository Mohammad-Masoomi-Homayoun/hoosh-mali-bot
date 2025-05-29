FROM python:3.11-slim

WORKDIR /app

# Install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bot.py .

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import os; assert os.getenv('TELEGRAM_TOKEN') is not None, 'TELEGRAM_TOKEN not set'"

# Run the bot
CMD ["python", "bot.py"]
