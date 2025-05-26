# 🧠 Crypto Monitor

Crypto Monitor is a Python-based monitoring tool designed to track wallet activity on blockchain platforms. It is containerized with Docker and provides an easy setup using `docker-compose`.

## 🚀 Features

- Monitor specific wallet addresses
- Configurable wallet list (`wallets.json`)
- Lightweight and easy to deploy
- Suitable for crypto enthusiasts and developers

## 📦 Project Structure

├── main.py # Main script to monitor wallet activity  
├── wallets.json # List of wallet addresses to track  
├── requirements.txt # Python dependencies  
├── Dockerfile # Docker container definition  
├── docker-compose.yml # Compose file for orchestration  
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
[
  {
    "name": "My Wallet",
    "address": "0x123abc..."
  }
]
```

3. Build and run the Docker container:
```bash
docker-compose up --build
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

## ✅ To Do  
- Add support for multiple chains
- Discord / Telegram bot integration
- Web UI for visualization
- Notification system

## 🤝 Contributing
Feel free to fork the project, open issues or pull requests. Contributions are welcome!

## 📄 License
This project is licensed under the MIT License. See the LICENSE file for details.