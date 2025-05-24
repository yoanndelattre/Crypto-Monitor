import time
import requests
import json
import os

# === Configuration ===
WEBHOOK_URL_DISCORD = os.environ['WEBHOOK_URL_DISCORD']   # Ton Webhook Discord
SAVE_FILE = "data/state.json"
WALLETS_FILE = "wallets.json"
API_INFO_URL = "https://api.hyperliquid.xyz/info" # Specific URL for info endpoint

# === Wallets ===
def load_wallets():
    try:
        with open(WALLETS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("Erreur chargement wallets.json :", e)
        return {}

# === Discord ===
def send_discord_message(message):
    try:
        requests.post(WEBHOOK_URL_DISCORD, json={"content": message})
    except Exception as e:
        print("Erreur Discord:", e)

# === JSON Storage ===
def load_state():
    if not os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("Erreur chargement state.json :", e)
        return {}

def save_state(state):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        print("Erreur sauvegarde:", e)

# === API Fetch ===
def fetch_positions(wallet_address):
    try:
        payload = { # This is the JSON body to be sent
            "type": "clearinghouseState",
            "user": wallet_address
        }
        headers = {"Content-Type": "application/json"} # Required for sending JSON body

        # Change back to requests.post, but send 'json' argument
        response = requests.post(API_INFO_URL, json=payload, headers=headers)
        print(response.status_code, response.text) # Print status code and raw text for full debugging
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        positions = {}
        for p in data.get("assetPositions", []):
            pos = p.get("position", {})
            size = float(pos.get("positionValue", 0))
            if size > 0:
                coin = pos.get("coin")
                positions[coin] = {
                    "size": size,
                    "entry": float(pos.get("entryPx", 0)),
                    "mark": None,  # Pas dans l'exemple, on peut chercher ailleurs ou mettre None
                    "unrealizedPnl": float(pos.get("unrealizedPnl", 0)),
                    "liquidationPx": float(pos.get("liquidationPx", 0)),
                    "leverage": pos.get("leverage", {}).get("value", 0)
                }
        return positions
    except Exception as e:
        print("Erreur API pour", wallet_address, ":", e)
        return {}

# === Analyse des changements ===
def analyze(wallet_name, wallet_address, current, previous):
    for asset in current:
        pos = current[asset]
        if asset not in previous:
            send_discord_message(
                f"📈 **{wallet_name}** a ouvert une nouvelle position sur **{asset}**\n"
                f"• Taille: {pos['size']} contrats\n"
                f"• Prix d'entrée: {pos['entry']:.2f}\n"
                f"• Liquidation: {pos['liquidationPx']:.2f}"
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
            send_discord_message(
                f"{reason} pour **{wallet_name}** sur **{asset}**\n"
                f"• Taille précédente: {last['size']} à {last['entry']:.2f}"
            )

# === Boucle principale ===
def monitor():
    # Create the 'data' directory if it doesn't exist
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    state = load_state()

    while True:
        wallets = load_wallets()
        for name, address in wallets.items():
            current_positions = fetch_positions(address)
            previous_positions = state.get(address, {})
            analyze(name, address, current_positions, previous_positions)
            state[address] = current_positions

        save_state(state)
        time.sleep(10)

# === Lancement ===
if __name__ == "__main__":
    monitor()