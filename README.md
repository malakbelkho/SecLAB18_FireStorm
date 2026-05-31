<div align="center">

# 🔥 LAB 18 — FireStorm

### Reverse Android · Frida Hooking · Firebase Authentication · Flag Extraction

![Android](https://img.shields.io/badge/Android-Reverse%20Engineering-3DDC84?style=for-the-badge&logo=android&logoColor=white)
![Frida](https://img.shields.io/badge/Frida-Dynamic%20Instrumentation-red?style=for-the-badge)
![Firebase](https://img.shields.io/badge/Firebase-Authentication-orange?style=for-the-badge&logo=firebase&logoColor=white)
![Python](https://img.shields.io/badge/Python-REST%20API-3776AB?style=for-the-badge&logo=python&logoColor=white)

</div>

---

## 📌 Présentation du challenge

**FireStorm** est un challenge Android de niveau **Medium** dont l’objectif est de récupérer un flag stocké dans une base de données **Firebase Realtime Database**.

L’application contient une méthode cachée qui génère dynamiquement le mot de passe Firebase.  
Cette méthode existe dans le code, mais elle n’est jamais appelée dans le fonctionnement normal de l’application.

Le but du lab est donc de :

- analyser l’APK avec **Jadx-GUI** ;
- identifier la méthode responsable de la génération du mot de passe ;
- forcer son exécution avec **Frida** ;
- utiliser le mot de passe généré pour s’authentifier auprès de **Firebase** ;
- récupérer le flag final.

---

## 🎯 Objectif du lab

Le challenge repose sur une méthode Java appelée :

```java
public String Password()
```
# 1. Installation de l’APK

L’APK `FireStorm.apk` a d’abord été installé sur l’émulateur Android avec **ADB**.

```bash
adb install FireStorm.apk
```

<p align="center">
  <img src="screenshots/adb-install-firestorm.png" width="850"/>
</p>

---

# 2. Vérification de Frida

Avant de lancer l’analyse dynamique, il fallait vérifier que **Frida Server** était bien lancé sur l’émulateur.

```bash
frida-ps -U
```

<p align="center">
  <img src="screenshots/frida-server.png" width="850"/>
</p>

Frida détecte bien l’émulateur Android, ce qui confirme que l’environnement d’instrumentation est prêt.

---

# 3. Analyse statique avec Jadx-GUI

L’APK a ensuite été ouvert avec **Jadx-GUI** afin d’inspecter le code Java décompilé.

## 3.1 Identification de la classe principale

La classe principale identifiée est :

```java
com.pwnsec.firestorm.MainActivity
```

<p align="center">
  <img src="screenshots/jadx_gui_MainActivity.png" width="850"/>
</p>

---

## 3.2 Méthode importante : `Password()`

Dans `MainActivity`, la méthode la plus importante est :

```java
public String Password()
```

<p align="center">
  <img src="screenshots/public_string_password.png" width="850"/>
</p>

Cette méthode construit une chaîne à partir de plusieurs ressources Android :

```java
String string = getString(R.string.Friday_Night);
String string2 = getString(R.string.Author);
String string3 = getString(R.string.JustRandomString);
String string4 = getString(R.string.URL);
String string5 = getString(R.string.IDKMaybethepasswordpassowrd);
String string6 = getString(R.string.Token);
```

Ensuite, elle récupère uniquement certains fragments avec `substring()` :

```java
sb.append(string.substring(5, 9));
sb.append(string4.substring(1, 6));
sb.append(string2.substring(2, 6));
sb.append(string5.substring(5, 8));
sb.append(string3);
sb.append(string6.substring(18, 26));
```

Enfin, elle envoie la chaîne construite vers une fonction native :

```java
return generateRandomString(String.valueOf(sb));
```

---

## 3.3 Fonction native

La méthode native identifiée est :

```java
public native String generateRandomString(String str);
```

<p align="center">
  <img src="screenshots/random-string_method.png" width="850"/>
</p>

Cette fonction n’est pas directement implémentée en Java.  
Elle est liée à une librairie native chargée par l’application.

---

## 3.4 Librairie native `libfirestorm.so`

Dans `MainActivity`, la librairie native est chargée avec :

```java
static {
    System.loadLibrary("firestorm");
}
```

<p align="center">
  <img src="screenshots/libfirestorm.png" width="850"/>
</p>

Cela signifie que la logique finale de génération du mot de passe est partiellement cachée dans le code natif.

---

# 4. Analyse des ressources `strings.xml`

Le fichier `strings.xml` contient plusieurs informations importantes utilisées dans la construction du mot de passe et dans la configuration Firebase.

<p align="center">
  <img src="screenshots/strings-xml.png" width="850"/>
</p>

Parmi les chaînes importantes, on trouve :

```xml
<string name="Author">TK757567</string>
<string name="Friday_Night">It\'s Friday, and PwnSec CTF is here!!!!!</string>
<string name="IDKMaybethepasswordpassowrd">v1n4of.5EY?%0z</string>
<string name="JustRandomString">or_is_it_random???</string>
<string name="URL">https://pwnsec.xyz/flag?auth=</string>
```

---

## 4.1 Informations Firebase

Les informations Firebase nécessaires sont également présentes dans les ressources de l’application.

<p align="center">
  <img src="screenshots/firebase_database-email.png" width="850"/>
</p>

```xml
<string name="firebase_database_url">https://firestorm-9d3db-default-rtdb.firebaseio.com</string>
<string name="firebase_email">TK757567@pwnsec.xyz</string>
```

L’API key est aussi récupérable depuis les ressources :

<p align="center">
  <img src="screenshots/google_api_key_firebase.png" width="850"/>
</p>

```xml
<string name="google_api_key">AIzaSyAXsK0qsx4RuLSA9C8IPSWd0eQ67HVHuJY</string>
```

---

# 5. Instrumentation dynamique avec Frida

Comme la méthode `Password()` n’est jamais appelée naturellement par l’application, elle a été appelée manuellement avec **Frida**.

## 5.1 Script Frida utilisé

Le script suivant recherche une instance active de `MainActivity`, puis appelle directement la méthode `Password()`.

```javascript
Java.perform(function () {

    function callPassword() {
        console.log("[*] Recherche d'une instance active de MainActivity...");

        Java.choose("com.pwnsec.firestorm.MainActivity", {

            onMatch: function (instance) {
                console.log("[+] Instance MainActivity trouvée : " + instance);

                try {
                    var password = instance.Password();
                    console.log("[+] Firebase Password : " + password);
                } catch (e) {
                    console.log("[-] Erreur lors de l'appel de Password() : " + e);
                }
            },

            onComplete: function () {
                console.log("[*] Recherche terminée.");
            }
        });
    }

    console.log("[*] Script Frida chargé.");
    console.log("[*] Attente de 3 secondes avant l'appel de Password()...");

    setTimeout(callPassword, 3000);
});
```

---

## 5.2 Lancement du script

La commande utilisée est :

```bash
frida -U -f com.pwnsec.firestorm -l scripts/frida_firestorm.js
```

<p align="center">
  <img src="screenshots/frida_firestorm.png" width="850"/>
</p>

---

## 5.3 Résultat obtenu

Frida a trouvé une instance active de `MainActivity`, puis a exécuté la méthode `Password()`.

<p align="center">
  <img src="screenshots/frida_password_recovered.png" width="850"/>
</p>

Mot de passe Firebase obtenu :

```text
C7_dotpsC7t7f_._In_i.IdttpaofoaIIdIdnndIfC
```

---

# 6. Authentification Firebase avec Python

Une fois le mot de passe récupéré, il a été utilisé avec l’email Firebase extrait de `strings.xml`.

## 6.1 Script Python utilisé

Le script suivant utilise l’API REST Firebase pour :

1. s’authentifier avec l’email et le mot de passe ;
2. récupérer un `idToken` ;
3. lire la Realtime Database ;
4. afficher le flag.

```python
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
```

---

## 6.2 Exécution du script

Commande utilisée :

```bash
python scripts/get_flag_rest.py
```

<p align="center">
  <img src="screenshots/get_flag_rest_executed.png" width="850"/>
</p>

---

# 7. Récupération du flag

L’authentification Firebase a réussi et la base de données a retourné le flag.

<p align="center">
  <img src="screenshots/flag_recovereddd.png" width="850"/>
</p>

Flag obtenu :

```text
PWNSEC{C0ngr4ts_Th4t_w45_4N_345y_P4$$w0rd_t0_G3t!!!_0R_!5_!t???}
```

---

# 8. Résumé de l’attaque

| Étape | Action | Résultat |
|---|---|---|
| 1 | Installation de l’APK | Application installée sur l’émulateur |
| 2 | Analyse avec Jadx | `MainActivity` identifiée |
| 3 | Recherche de méthode sensible | `Password()` trouvée |
| 4 | Analyse des ressources | Email, API key et database URL extraits |
| 5 | Instrumentation avec Frida | Appel forcé de `Password()` |
| 6 | Génération du password | Mot de passe Firebase récupéré |
| 7 | Authentification Firebase | Token obtenu |
| 8 | Lecture de la base | Flag récupéré |

---

# 9. Schéma global du challenge

```text
APK FireStorm
     │
     ▼
Analyse statique avec Jadx
     │
     ├── MainActivity
     ├── Password()
     ├── generateRandomString()
     └── strings.xml
             │
             ▼
Configuration Firebase récupérée
             │
             ▼
Hook Frida sur MainActivity
             │
             ▼
Appel manuel de Password()
             │
             ▼
Mot de passe Firebase généré
             │
             ▼
Script Python REST
             │
             ▼
Authentification Firebase
             │
             ▼
Lecture Realtime Database
             │
             ▼
FLAG
```

---

# 10. Difficultés rencontrées

## Argument `--no-pause` non reconnu

La commande proposée dans l’énoncé contenait :

```bash
--no-pause
```

Cependant, avec la version utilisée de Frida, cet argument n’était pas reconnu.

Erreur obtenue :

```text
frida: error: unrecognized arguments: --no-pause
```

La commande correcte utilisée a donc été :

```bash
frida -U -f com.pwnsec.firestorm -l scripts/frida_firestorm.js
```

Frida a automatiquement repris le thread principal avec :

```text
Spawned `com.pwnsec.firestorm`. Resuming main thread!
```

---

# 11. Conclusion

Ce lab montre comment une méthode sensible peut rester présente dans le code d’une application Android même si elle n’est jamais appelée dans le flux normal.

Grâce à l’analyse statique avec **Jadx**, il a été possible d’identifier la méthode responsable de la génération du mot de passe.  
Ensuite, avec **Frida**, cette méthode a été appelée dynamiquement dans le contexte réel de l’application.

La combinaison de l’analyse statique et de l’instrumentation dynamique a permis de récupérer le mot de passe Firebase, de s’authentifier, puis d’extraire le flag depuis la base de données.

---

<div align="center">

## ✅ Lab terminé avec succès

### Flag final

```text
PWNSEC{C0ngr4ts_Th4t_w45_4N_345y_P4$$w0rd_t0_G3t!!!_0R_!5_!t???}
```

<br>

🔥 **FireStorm solved** 🔥

</div>
