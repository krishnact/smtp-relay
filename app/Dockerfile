FROM python:3.11-slim

# Install required packages
RUN apt-get update && \
    apt-get install -y openssl && \
    pip install aiosmtpd sendgrid requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy source files
COPY . /app

# Expose SMTPS port
EXPOSE 465

ENV CERT_PATH=/etc/ssl/private/server.pem
# Set entrypoint
# CMD ["python", "email_relay.py"]


ENTRYPOINT ["/app/entrypoint.sh"]
