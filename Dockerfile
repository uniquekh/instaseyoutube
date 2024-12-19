# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install ImageMagick (needed by moviepy for handling images)
RUN apt-get update && \
    apt-get install -y imagemagick

# Copy token.pickle into the container (this is your OAuth token file)
COPY token.pickle /app/token.pickle

# Expose port 5000 (or whichever port you use for your bot)
EXPOSE 5000

# Command to run the bot
CMD ["python", "app.py"]
