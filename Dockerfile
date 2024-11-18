FROM python:3.12-slim

RUN mkdir -p /home/python/master_of_jokes

WORKDIR /home/python/master_of_jokes

# Copy project files
COPY . .

# Install dependencies and project in development mode
RUN pip install --no-cache-dir .

# Set environment variables
ENV FLASK_APP=master_of_jokes
ENV FLASK_ENV=production
ENV FLASK_RUN_PORT=3000

# Create instance folder
RUN mkdir -p instance

# Expose configurable port
EXPOSE 3000

# Command to run the development server
RUN ["flask", "--app", "master_of_jokes", "init-db"]

# Command to run the development server
CMD ["flask", "run", "--host=0.0.0.0"] 