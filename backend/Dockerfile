FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["functions-framework", "--target=increment_visitor_counter", "--host=0.0.0.0"]
