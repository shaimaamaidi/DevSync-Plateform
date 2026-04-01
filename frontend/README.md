![Node.js](https://img.shields.io/badge/node-%3E=18.0.0-brightgreen)
![Vite](https://img.shields.io/badge/vite-5.x-blue)
![React](https://img.shields.io/badge/react-18.x-blue)

# Frontend

Ceci est le frontend de la plateforme, développé avec **React**, **TypeScript**, **Vite** et **Tailwind CSS**. Il consomme l’API backend pour la gestion des membres, dépôts, déploiements et intégrations ClickUp.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Client & Auth](#api-client--auth)
- [Main Features](#main-features)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)
- [Main Dependencies](#main-dependencies)
- [Additional Notes](#additional-notes)
- [Contact](#contact)

---

## 🚀 Quick Start

1. **Cloner le dépôt et aller dans le dossier frontend :**
   ```bash
   git clone <repo-url>
   cd frontend
   ```

2. **Installer les dépendances :**
   ```bash
   npm install
   ```

3. **Configurer les variables d’environnement :**
   - Copier `openapitools.json` et `.env.example` si besoin.
   - Adapter les variables dans `.env` (voir section dédiée).

4. **Générer le client API (si modif backend) :**
   ```bash
   npm run generate:api
   ```

5. **Lancer l’application en développement :**
   ```bash
   npm run dev
   ```

---

## 🛠️ Project Structure

```
frontend/
  src/
    api/           # Client API généré (OpenAPI)
    components/    # Composants React (UI, tables, modals...)
    hooks/         # Custom React hooks
    lib/           # Fonctions utilitaires
    pages/         # Pages principales (Home, NotFound...)
    services/      # Services métiers (auth, membres, dépôts...)
    assets/        # Images, logos, etc.
    App.tsx        # Point d’entrée principal
    main.tsx       # Bootstrap React
  public/          # Fichiers statiques
  index.html       # HTML principal
  package.json     # Dépendances et scripts
  vite.config.ts   # Config Vite
  tailwind.config.js # Config Tailwind
```

---

## 🔐 API Client & Auth

- **Client API** généré automatiquement depuis le backend (OpenAPI) : voir `src/api/` et `src/apiClient.ts`.
- **Authentification** :
  - Utilise JWT en cookie HttpOnly/Secure/SameSite pour le token d’accès (géré automatiquement par le navigateur).
  - Le token de rafraîchissement est stocké côté client (cookie ou localStorage).
  - Intercepteur Axios pour rafraîchir automatiquement le token d’accès en cas de 401.
  - Les routes frontend sont protégées selon l’état d’authentification.

---

## ✨ Main Features

- Gestion des membres (inscription, connexion, édition)
- Gestion des dépôts GitHub
- Suivi des déploiements
- Intégration ClickUp (espaces, associations)
- UI moderne et responsive (Tailwind CSS)
- Notifications d’erreur et succès globales

---

## ⚙️ Environment Variables

Créer un fichier `.env` à la racine du frontend si besoin. Principales variables :

| Variable           | Description                        | Exemple                |
|--------------------|------------------------------------|------------------------|
| VITE_API_BASE_URL  | URL de l’API backend               | http://localhost:8000  |

---

## 🧪 Running Tests

Lancer les tests unitaires (si présents) :
```bash
npm run test
```

---

## 📦 Main Dependencies

- react
- react-dom
- typescript
- vite
- tailwindcss
- axios
- @tanstack/react-query
- openapi-typescript-codegen

Voir `package.json` pour la liste complète.

---

## 📚 Additional Notes

- Le code est typé TypeScript et suit les bonnes pratiques React modernes.
- Le client API doit être régénéré (`npm run generate:api`) après toute modification du backend.
- Pour toute question ou bug, ouvrir une issue ou contacter le mainteneur.

---

## 📞 Contact

Pour toute question ou support, contacter : amaidi.shaima@gmail.com
