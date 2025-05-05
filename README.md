# 📧 Modular Python SMTP Relay with TLS, SendGrid & Brevo

This is a secure and modular SMTP relay server that receives emails via SMTPS (port 465) and forwards them using **SendGrid** and **Brevo (Sendinblue)** APIs. It includes daily quota tracking and automatically switches providers once a quota is reached.

---

## ✅ Features

- 🔒 TLS-secured SMTP on port 465 with auto-generated self-signed cert
- 📨 Supports both SendGrid and Brevo (Sendinblue)
- 🔁 Quota-based provider rotation (e.g. 200 via SendGrid, 300 via Brevo)
- 📦 Docker-ready deployment
- 🔌 Modular design for adding new providers
- 🧾 MIME-parsing with `aiosmtpd`

---

## 🚀 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SENDGRID_API_KEY` | Your SendGrid API key | `SG.xxxx` |
| `BREVO_API_KEY` | Your Brevo (Sendinblue) API key | `xkeysib-xxxx` |
| `SENDGRID_DAILY_LIMIT` | Daily limit for SendGrid usage (default 200) | `200` |
| `BREVO_DAILY_LIMIT` | Daily limit for Brevo usage (default 300) | `300` |
| `RELAY_FROM_EMAIL` | (Optional) Override "From" email | `noreply@example.com` |
| `RELAY_FROM_NAME` | (Optional) Override sender name | `My App` |

---

## 🛠 How to Build and Run
### ▶️ Run the Container
You would most likely want to run inside an already existing container along with other services 
so that they can access this smtp relay. If that is the case then copy the compose.override.example.yaml
file in the the same folder as your docker-compose.yml file.
```bash
cp -nv smtp-relay\compose.override.example.yaml compose.override.yaml
```

Then run 
```bash
docker compose build
docker compose up -d
docker compose logs -f  smtp-relay
```

This container will be accessible as 'smtp-relay' hostname from other services in the same container.

---

## 📁 Project Structure

```
smtp_relay/
├── compose.override.example.yaml
├── email_relay.py                # Main server entrypoint
├── entrypoint.sh
├── Dockerfile
├── README.md
└── providers/
    ├── __init__.py
    ├── provider_base.py          # Interface for providers
    ├── sendgrid_provider.py
    └── brevo_provider.py
```

---

## 📚 Notes

- TLS cert is auto-generated on first run if `/etc/ssl/private/server.pem` does not exist
- Can be extended to support more providers by implementing `EmailProvider` interface

---

## 📬 Testing

You can send emails using any SMTP client configured for:

- SMTP server: `localhost`
- Port: `465`
- TLS: Enabled
- No auth required (optional for internal use only)

---
### Motivation:

I had to create this because I was installing Zammad ticketing system, and it needed a SMTP server. My hosting provider blocks outgoing
SMTP ports, so I could not use SMTP protocol to send messages. This smtp-relay provides a way for Zammad to think its talking to a SMTP server. 
It works fine for our needs of sending about 250 messages per day (there is no reason it can not send 10000 messages per day).

---

## 🧩 License

MIT
