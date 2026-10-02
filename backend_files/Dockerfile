FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code and the serialized model
COPY app.py superkart_model.joblib ./

# Flask API listens on 7860
EXPOSE 7860

# Serve with gunicorn (production-grade WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "app:superkart_api"]
