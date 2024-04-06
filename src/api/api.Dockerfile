# Use a Python base image
FROM python:3.10

# Set the working directory
WORKDIR /usr/src/app

# Copy requirements.txt
COPY ./requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /usr/src/app

# Run the application
CMD ["uvicorn", "api_main:app", "--reload"]
