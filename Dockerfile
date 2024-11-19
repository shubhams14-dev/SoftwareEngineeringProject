FROM python:3.12-slim


WORKDIR /app

# Copy project files
COPY dist/master_of_jokes-1.0.0-py2.py3-none-any.whl .

# Install dependencies and project in development mode
RUN pip install master_of_jokes-1.0.0-py2.py3-none-any.whl gunicorn

EXPOSE 5000
# Command to run the development server
CMD [ "gunicorn", "-w","4","-b", "0.0.0.0:5000", "master_of_jokes:create_app()"] 