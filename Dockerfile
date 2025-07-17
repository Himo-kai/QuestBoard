# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Allow toggling development mode via build argument
ARG FLASK_ENV=production
ENV FLASK_ENV=${FLASK_ENV}

# Copy all application files
COPY *.py ./
COPY gear_keywords.json ./

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the port Flask will run on (5000 by default)
EXPOSE 5000

# Run the Flask app
CMD ["flask", "run"]
