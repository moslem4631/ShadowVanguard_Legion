# F:\ShadowVanguard_Legion_Godspeed\recon.py
# Version 2.0 - Spot Reconnaissance Edition

import ccxt
import os
from dotenv import load_dotenv

print("--- Reconnaissance Mission Started (Objective: SPOT Markets) ---")

# Load credentials from the vault (optional for this script, but good practice)
load_dotenv()
api_key = os.getenv('TESTNET_API_KEY')
secret_key = os.getenv('TESTNET_SECRET_KEY')

# Note: For public data like markets, API keys are often not strictly needed,
# but providing them ensures we are authenticated if required.
if not api_key or not secret_key:
    print("WARNING: API credentials not found in .env. Proceeding with public access.")
    # Assign dummy values if not found, as ccxt may require them.
    api_key = 'dummy'
    secret_key = 'dummy'
else:
    print("Credentials loaded successfully from .env vault.")

# Establish connection. We are connecting to the SPOT part of the exchange.
try:
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': secret_key,
        # We REMOVE 'defaultType': 'future' to access SPOT markets
    })
    
    # IMPORTANT: The public testnet for SPOT is integrated differently.
    # The main ccxt library connects to a public but separate spot testnet URL
    # when sandbox mode is enabled. We will enable it to see spot test markets.
    exchange.set_sandbox_mode(True)

    print(f"Connection to Binance SPOT Testnet established at: {exchange.urls['api']}")

except Exception as e:
    print(f"FATAL: Could not initialize exchange. Reason: {e}")
    exit()


try:
    # Fetch all available markets from the connected exchange
    markets = exchange.load_markets()
    print(f"Successfully loaded {len(markets)} market definitions.")
    
    active_spot_markets = []
    print("\n--- Scanning for Active USDT SPOT Markets ---")
    for symbol, market in markets.items():
        # [SURGICAL CHANGE]: We now look for 'spot' markets instead of 'perpetual'
        if market.get('spot') and market.get('quote') == 'USDT' and market.get('active'):
            active_spot_markets.append(symbol)

    if not active_spot_markets:
        print("\nCRITICAL FINDING: No active USDT SPOT markets found on the Testnet.")
        print("This could indicate a temporary issue with the Binance Spot Testnet.")
    else:
        print(f"\nSUCCESS: Found {len(active_spot_markets)} active USDT SPOT markets.")
        print("Here are some of the available markets for testing:")
        # Print first 20 for brevity
        for symbol in active_spot_markets[:20]:
            print(f" - {symbol}")
    
    print("\n--- Reconnaissance Mission Complete ---")

except Exception as e:
    print(f"\nAn error occurred during the mission: {e}")