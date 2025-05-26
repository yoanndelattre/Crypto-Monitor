# 🧠 Crypto Monitor

Crypto Monitor is a Python-based monitoring tool designed to track wallet activity on blockchain platforms. It is containerized with Docker and provides an easy setup using `docker-compose`.

## 🚀 Features

- Monitor one or more wallet addresses on Hyperliquid
- Detect new positions, scaling events, and possible liquidations
- Send real-time alerts to Discord via webhook
- Persistent position tracking with SQLite
- Docker-ready for easy deployment

## 📦 Project Structure

├── main.py # Main script to monitor wallet activity  
├── wallets.json # List of wallet addresses to track  
├── requirements.txt # Python dependencies  
├── Dockerfile # Docker container definition  
├── docker-compose.yml # Compose file for orchestration  
├── README.md # Project documentation  
└── .github/workflows/ # GitHub Actions for CI/CD

## 🛠️ Prerequisites

Make sure you have the following installed:

- Python 3.8+
- Docker
- Docker Compose

## 🐳 Quick Start (Docker)

1. Clone the repository:

```bash
git clone https://github.com/yoanndelattre/Crypto-Monitor.git
cd Crypto-Monitor
```
3. Configure your wallet addresses in wallets.json:

```bash
{
    "Trader Alpha": "0x1234abcd...",
    "Trader Beta": "0x5678efgh..."
}
```

4. Environment Variables

Create a `.env` file in the project root with the following variable:

```env
WEBHOOK_URL_DISCORD=your_discord_webhook_url_here
```
This variable is required to send wallet position alerts to Discord. You can generate a webhook URL in your Discord server settings.

5. Run the Docker container:
```bash
docker-compose up
```

## 🧪 Development Setup (Local)

1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Run the script:
```bash
python main.py
```

## 🤝 Contributing
Feel free to fork the project, open issues or pull requests. Contributions are welcome!

## 📄 License
This project is licensed under the MIT License. See the LICENSE file for details.