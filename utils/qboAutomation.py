import base64
import requests

# Get a fresh QBO access token using the refresh token
def get_fresh_qbo_token(client_id, client_secret, refresh_token):
    url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    auth_string = f"{client_id}:{client_secret}" 
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception as e:
        print(f"\n  [QBO Error] Token refresh exception: {e}")
    return None

def post_expense_to_qbo(info, access_token, realm_id):
    """Formats your AI info and pushes it to your QBO Sandbox Company"""
    url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/purchase"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Map your Ollama extracted info directly to the QBO Purchase Entity
    payload = {
        "PaymentType": "CreditCard",
        "TxnDate": info.get("date"),
        "AccountRef": {
            "value": "41"  # Default Sandbox Credit Card Account ID
        },
        "Line": [
            {
                "Amount": info.get("totalAmount"),
                "DetailType": "AccountBasedExpenseLineDetail",
                "AccountBasedExpenseLineDetail": {
                    "AccountRef": {
                        "value": "13"  # Default Sandbox Expense Account ID
                    }
                }
            }
        ],
        "VendorRef": {
            "name": info.get("store")  # QBO matches text name directly if vendor exists
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        return response.status_code == 200
    except Exception:
        return False

def qbo_worker_thread(info, cfg):
    client_id = cfg.get("qbo_client_id")
    client_secret = cfg.get("qbo_client_secret")
    refresh_token = cfg.get("qbo_refresh_token")
    realm_id = cfg.get("qbo_realm_id")
    
    if not all([client_id, client_secret, refresh_token, realm_id]):
        print("Missing QBO credentials. Complete the setup wizard or add them into the config file:")
        return 

    access_token = get_fresh_qbo_token(client_id, client_secret, refresh_token)
    if not access_token:
        print(f"\n  [QBO Sync Failed] Authorization failed for {info.get('store')}")
        return
        
    # 2. Push to cloud ledger
    success = post_expense_to_qbo(info, access_token, realm_id)
    if success:
        print(f"\n  [QBO Sync Success] Exported: {info.get('store')} - ${info.get('totalAmount')}")
    else:
        print(f"\n  [QBO Sync Failed] Ledger rejection on receipt from {info.get('store')}")