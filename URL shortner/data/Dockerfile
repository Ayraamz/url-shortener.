
FROM python:3.11-slim

WORKDIR /app

# System deps for pandas/matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends         gcc g++ build-essential libatlas-base-dev liblapack-dev gfortran         libfreetype6-dev libpng-dev         && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
