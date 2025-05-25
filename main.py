import time
import requests
import json
import os
import sqlite3
import logging

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)

# === Configuration ===
WEBHOOK_URL_DISCORD = os.environ['WEBHOOK_URL_DISCORD']   # Ton Webhook Discord
DB_FILE = "data/state.db"
WALLETS_FILE = "wallets.json"
API_INFO_URL = "https://api.hyperliquid.xyz/info" # Specific URL for info endpoint

# === Initialisation base de données ===
def init_db():
    logging.info("Initialisation de la base de données...")
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            wallet TEXT,
            coin TEXT,
            size REAL,
            entry REAL,
            unrealizedPnl REAL,
            positionValue REAL,
            liquidationPx REAL,
            leverage REAL,
            direction TEXT,
            PRIMARY KEY (wallet, coin)
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Base de données prête.")

# === Wallets ===
def load_wallets():
    try:
        logging.info("Chargement des wallets...")
        with open(WALLETS_FILE, "r") as f:
            wallets = json.load(f)
            logging.info(f"{len(wallets)} wallet(s) chargé(s).")
            return json.load(f)
    except Exception as e:
        logging.error(f"Erreur chargement wallets.json : {e}")
        return {}

# === Discord ===
def send_discord_message(message):
    try:
        logging.info(f"Envoi Discord : {message[:60]}...")
        requests.post(WEBHOOK_URL_DISCORD, json={"content": message})
    except Exception as e:
        logging.error(f"Erreur envoi Discord : {e}")

# === Sauvegarde SQLite ===
def load_state(wallet_address):
    logging.info(f"Chargement de l'état pour {wallet_address}...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT coin, size, entry, unrealizedPnl, positionValue, liquidationPx, leverage, direction FROM positions WHERE wallet = ?", (wallet_address,))
    rows = cursor.fetchall()
    conn.close()
    state = {}
    for row in rows:
        coin = row[0]
        state[coin] = {
            "size": row[1],
            "entry": row[2],
            "unrealizedPnl": row[3],
            "positionValue": row[4],
            "liquidationPx": row[5],
            "leverage": row[6],
            "direction": row[7]
        }
    logging.info(f"{len(state)} position(s) chargée(s) pour {wallet_address}.")
    return state

def save_state(wallet_address, positions):
    logging.info(f"Sauvegarde de l'état pour {wallet_address}...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Supprimer les anciennes positions
    cursor.execute("DELETE FROM positions WHERE wallet = ?", (wallet_address,))
    for coin, pos in positions.items():
        cursor.execute('''
            INSERT INTO positions (wallet, coin, size, entry, unrealizedPnl, positionValue, liquidationPx, leverage, direction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            wallet_address, coin,
            pos["size"], pos["entry"],
            pos["unrealizedPnl"], pos["positionValue"], pos["liquidationPx"],
            pos["leverage"], pos["direction"]
        ))
    conn.commit()
    conn.close()
    logging.info(f"État sauvegardé pour {wallet_address} ({len(positions)} position(s)).")

# === API Fetch ===
def fetch_positions(wallet_address):
    try:
        logging.info(f"Requête des positions pour {wallet_address}...")
        payload = {
            "type": "clearinghouseState",
            "user": wallet_address
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(API_INFO_URL, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        positions = {}
        for p in data.get("assetPositions", []):
            pos = p.get("position", {})
            size = float(pos.get("szi", 0))
            if size != 0:
                coin = pos.get("coin")
                entry_px = float(pos.get("entryPx", 0))
                unrealized_pnl = float(pos.get("unrealizedPnl", 0))
                positionValue = float(pos.get("positionValue", 0))
                liquidation_px_raw = pos.get("liquidationPx")
                liquidation_px = float(liquidation_px_raw) if liquidation_px_raw is not None else None
                leverage = pos.get("leverage", {}).get("value", 0)
                direction = "long" if size > 0 else "short"
                positions[coin] = {
                    "size": size,
                    "entry": entry_px,
                    "unrealizedPnl": unrealized_pnl,
                    "positionValue": positionValue,
                    "liquidationPx": liquidation_px,
                    "leverage": leverage,
                    "direction": direction
                }
        logging.info(f"{len(positions)} position(s) active(s) pour {wallet_address}.")
        return positions
    except Exception as e:
        logging.error(f"Erreur API pour {wallet_address} : {e}")
        return {}

# === Analyse des changements ===
def analyze(wallet_name, wallet_address, current, previous):
    for asset in current:
        pos = current[asset]
        liquidation_px = pos.get("liquidationPx")
        direction = pos.get("direction", "inconnue")
        if asset not in previous:
            logging.info(f"Nouvelle position détectée pour {wallet_name} sur {asset}")
            liquidation_str = f"{liquidation_px:.2f}" if liquidation_px is not None else "N/A"
            send_discord_message(
                f"📈 **{wallet_name}** a ouvert une nouvelle position **{direction.upper()}** sur **{asset}**\n"
                f"• Taille: {pos['size']}\n"
                f"• Valeur de la position: {pos['positionValue']} $\n"
                f"• Prix d'entrée: {pos['entry']:.2f}\n"
                f"• Liquidation: {liquidation_str}"
            )

    # Détection de fermetures ou liquidations
    for asset in previous:
        if asset not in current:
            last = previous[asset]
            reason = "❌ Fermeture manuelle"
            # This liquidation detection logic might need refinement based on how Hyperliquid reports liquidation
            # For now, it's an estimation based on a significant negative PnL relative to initial capital at risk
            if last["unrealizedPnl"] < -abs(last["entry"] - last["liquidationPx"]) * last["size"] * 0.95:
                reason = "💥 Liquidation probable"
            logging.info(f"Fermeture détectée pour {wallet_name} sur {asset} ({reason})")
            send_discord_message(
                f"{reason} pour **{wallet_name}** sur **{asset}**\n"
                f"• Taille précédente: {last['size']} à {last['entry']:.2f}"
            )

# === Boucle principale ===
def monitor():
    logging.info("Démarrage de la surveillance...")
    init_db()
    while True:
        wallets = load_wallets()
        for name, address in wallets.items():
            logging.info(f"Vérification de {name} ({address})...")
            current_positions = fetch_positions(address)
            previous_positions = load_state(address)
            analyze(name, address, current_positions, previous_positions)
            save_state(address, current_positions)
        logging.info("Pause de 10 secondes...\n")
        time.sleep(10)

# === Lancement ===
if __name__ == "__main__":
    monitor()