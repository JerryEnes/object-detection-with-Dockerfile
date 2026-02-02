FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install opencv-python-headless
COPY . .
RUN mkdir -p static/uploads static/results
EXPOSE 5000
CMD ["python", "app.py"]
