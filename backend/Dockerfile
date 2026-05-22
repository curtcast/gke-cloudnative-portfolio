# Step 1: Use an official Python runtime as a parent image
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the rest of your backend code
COPY . .

# Step 5: Expose port 8080 for Cloud Run
EXPOSE 8080

# 🌟 CRUCIAL FIX: Tell Functions Framework how to boot your code!
CMD ["functions-framework", "--target=increment_visitor_counter", "--host=0.0.0.0", "--port=8080"]FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
