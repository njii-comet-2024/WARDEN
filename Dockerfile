# Project: WARDEN
# Author/s: COMET Software Subteam 2024
# -----------------------------------------------------


# Select the base image
FROM python:3.8-slim

# Copy the files to run the app
COPY src /WARDEN/src/air-vehicle
COPY src /WARDEN/src/ground-vehicle
COPY data /WARDEN/data
COPY requirements.txt /WARDEN

# Install python and other common libraries
RUN apt-get update -y && \
    apt-get -y install \
    ca-certificates \
    openssh-client \
    gcc \
    libc-dev \
    tdsodbc \
    g++ \
    libffi-dev \
    libxml2 \
    unixodbc-dev \
    python3-pip \
    nano && \
    pip3 install -r /WARDEN/requirements.txt &&\
    pip3 install --upgrade pip

# Select the working directory
WORKDIR /WARDEN

# Add this comand to avoid the container to close after the execution
#CMD tail -f /dev/null

# Execute the script
CMD [ "python", "src/main.py", "-l", "debug" ]
