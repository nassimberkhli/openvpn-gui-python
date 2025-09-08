# OpenVPN GUI Client (Python)

Une interface graphique légère en **Tkinter** pour piloter un client **OpenVPN** depuis Python.  
Ce projet encapsule la logique de lancement et d’arrêt d’OpenVPN dans une classe contrôleur, tout en séparant clairement l’interface graphique de la logique de subprocess.

---

## ✨ Fonctionnalités

- Interface graphique simple en **Tkinter**  
- Sélection d’un fichier de configuration `.ovpn`  
- Support des identifiants (username/password)  
- Journalisation en temps réel des logs OpenVPN  
- Boutons **Connect** / **Disconnect**  
- Gestion propre du processus OpenVPN (démarrage, arrêt, SIGINT)  
- Suppression sécurisée des fichiers temporaires contenant les identifiants  

---

## 📂 Structure du projet

```
.
├── auth\_file.py        # Gestion des fichiers temporaires pour username/password
├── gui.py              # Interface graphique Tkinter
├── main.py             # Point d'entrée de l'application
├── vpn\_controller.py   # Contrôleur du processus OpenVPN
```
---

## ▶️ Utilisation

Lancer l’application avec :

```bash
python main.py
```

Interface :

* Sélectionner un fichier `.ovpn`
* Entrer vos identifiants (si nécessaires)
* Cliquer sur **Connect**
* Observer les logs en direct dans la fenêtre
* Cliquer sur **Disconnect** pour arrêter le VPN

---

## ⚠️ Sécurité

* Les identifiants (username/password) sont écrits temporairement en **clair** dans un fichier via `AuthFile`.
* Ce fichier est supprimé à la fermeture/déconnexion, mais **ne pas utiliser ce projet en production** tel quel.
* Ce projet est conçu pour **tests/démos uniquement**.

---

## 🛠️ Compatibilité

* **OS supportés** : Linux, macOS, Windows
* **Python** : ≥ 3.7
* **OpenVPN** doit être installé séparément
