FROM python:3.11.5
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

LABEL authors="joeedginton-foy"
WORKDIR /app
COPY . /app

RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy


# Create the logs directory and set permissions
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Creates a non-root user and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app

# Switch to the non-root user
USER appuser

#CMD ["python", "main.py"]