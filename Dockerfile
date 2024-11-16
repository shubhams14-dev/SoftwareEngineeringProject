FROM python:3.9-slim

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies and project in development mode
RUN pip install --no-cache-dir -e .

# Set environment variables
ENV FLASK_APP=flaskr
ENV FLASK_ENV=development
ENV FLASK_RUN_PORT=3000

# Create instance folder
RUN mkdir -p instance

# Expose configurable port
EXPOSE 3000

# Command to run the development server
CMD ["flask", "run", "--host=0.0.0.0"] 