# System Audio Recorder (مسجل صوت النظام)

Une application d'enregistrement audio en Python avec une interface graphique moderne (CustomTkinter). Ce projet est conçu pour enregistrer le **son interne du système** (loopback) de manière transparente, avec détection automatique du niveau sonore.

L'interface est entièrement en arabe avec une prise en charge complète du texte de droite à gauche (RTL).

## 🚀 Fonctionnalités

- **Enregistrement du Son Système** : Capture l'audio interne (ce que l'ordinateur joue) via *Windows WASAPI*.
- **Détection Automatique de l'Audio** : Un indicateur visuel et un journal (log) vous alertent quand l'application détecte un son au-dessus d'un certain seuil.
- **Support Arabe Natif (RTL)** : Intégration parfaite de la langue arabe avec des lettres attachées correctement via `arabic_reshaper` et `python-bidi`.
- **Interface Graphique Moderne** : Basée sur `customtkinter` (thème sombre par défaut).
- **Enregistrement Non-bloquant** : L'interface reste fluide pendant l'enregistrement et la sauvegarde du fichier WAV (via le multi-threading).

## 📋 Prérequis

- **Système d'exploitation** : Windows (nécessaire pour l'interface WASAPI Loopback).
- **Python** : 3.8 ou supérieur.

## 🛠️ Installation

1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/Ba7athproject/Record_sys.git
   cd Record_sys
   ```

2. **Créer un environnement virtuel (recommandé) :**
   ```bash
   python -m venv .venv
   .venv\scripts\activate
   ```

3. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Utilisation

Pour lancer l'application, exécutez le script principal :

```bash
python enregistreur_sys.py
```

1. Cliquez sur **📁 اختيار مجلد الحفظ** pour choisir où enregistrer le fichier audio.
2. Cliquez sur **▶️ بدء التسجيل** pour lancer l'écoute et l'enregistrement du son système.
3. Le statut et les détails s'afficheront dans la zone de texte au fur et à mesure (horodatage, intensité sonore détectée).
4. Cliquez sur **⛔ إيقاف التسجيل** pour arrêter et sauvegarder automatiquement l'enregistrement au format `.wav`.

## 📦 Dépendances Principales

Les librairies suivantes sont utilisées (voir `requirements.txt`) :
- `customtkinter` : Pour l'interface graphique.
- `sounddevice` / `numpy` : Pour la capture et le traitement du flux audio en direct.
- `arabic-reshaper` / `python-bidi` : Pour le rendu du texte en arabe.

---
© Ba7athproject
