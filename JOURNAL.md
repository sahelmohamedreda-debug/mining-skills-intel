# Journal de bord — Projet d'analyse des compétences minières

Ce document trace, étape par étape, ce qui a été réalisé, les décisions prises et les difficultés rencontrées (et comment elles ont été résolues). Utile pour la présentation finale et pour se souvenir du raisonnement derrière chaque choix.

---

## Semaine 1

### Jour 1 — Setup du projet
**Réalisé :**
- Création du compte GitHub et du repo `mining-skills-intel`
- Installation de Git et Claude Code sur le poste (Windows)
- Structure de dossiers créée : `src/collectors`, `src/extraction`, `src/db`, `src/dashboard`, `data/`, `docs/`, `tests/`
- Fichier `.gitignore` configuré (exclut `venv/`, `__pycache__/`, `.env`, `data/jobs.db`)

**Difficultés rencontrées et résolues :**
- Confusion initiale entre CMD et PowerShell (certaines commandes comme `Test-Path` ou `New-Item` ne fonctionnent qu'en PowerShell)
- Politique d'exécution PowerShell bloquant les scripts (`.ps1`) par défaut → résolu avec `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Identité Git non configurée au premier commit → résolu avec `git config --global user.name/user.email`

---

### Jour 2 — Identification des sources (ATS)
**Réalisé :**
- Vérification de 25+ entreprises minières et mining-tech (majors, mid-caps, juniors, startups)
- Identification de la plateforme ATS de chacune via l'analyse du pattern d'URL
- Constat clé : les grandes entreprises minières traditionnelles utilisent majoritairement des systèmes fermés (Workday, Oracle Recruiting Cloud, ADP, SAP SuccessFactors, Cornerstone OnDemand) sans API publique exploitable
- Les entreprises mining-tech/juniors plus jeunes utilisent davantage des ATS modernes avec API publique

**5 sources retenues avec API publique confirmée :**
1. KoBold Metals — Greenhouse
2. Redwood Materials — Greenhouse
3. American Battery Technology Company — Workable
4. Mariana Minerals — Ashby
5. Lilac Solutions — Rippling

**Document produit :** `docs/SOURCES_CANDIDATES.md`

---

### Jour 3 — Droits de collecte
**Réalisé :**
- Vérification du `robots.txt` des sites principaux des 5 entreprises retenues
- Distinction établie entre robots.txt du site vitrine (non pertinent ici) et l'API de la plateforme ATS réellement interrogée (ce qui compte)
- Confirmation que Greenhouse et Workable documentent officiellement leurs API Job Board pour un usage par des tiers
- Conclusion : les 5 sources sont autorisées, la méthode de collecte se limite à la lecture d'API publiques en lecture seule (GET), sans authentification ni contournement

**Document produit :** `docs/SOURCES.md`

---

### Jour 4 — Premier collector (KoBold Metals / Greenhouse)
**Réalisé :**
- Script `src/collectors/greenhouse.py` : appel de l'API publique Greenhouse (`GET boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true`)
- Fonction `fetch_jobs()` : récupère la liste brute des offres en JSON
- Fonction `clean_description()` : nettoie le HTML des descriptions (décodage des entités HTML en 2 passes car Greenhouse double-encode parfois, puis suppression des balises)
- Vérification manuelle : comparaison du nombre d'offres (29) et des titres affichés avec le site public de KoBold Metals — correspondance confirmée

**Difficultés rencontrées et résolues :**
- Premier nettoyage insuffisant : les entités HTML (`&lt;p&gt;`) n'étaient pas décodées avant le retrait des balises → ajout de `html.unescape()`
- Un seul décodage ne suffisait pas (double encodage côté Greenhouse) → décodage appliqué deux fois

---

### Jour 5 — Stockage en base de données SQLite
**Réalisé :**
- Schéma SQL (`src/db/schema.sql`) : table `jobs` avec contrainte `UNIQUE(company, external_id)` pour empêcher les doublons au niveau de la base elle-même
- Module `src/db/db.py` : fonctions `init_db()`, `insert_job()`, `count_jobs()`
- Anti-doublon géré via `try/except sqlite3.IntegrityError` : une tentative d'insertion en double est automatiquement rejetée par SQLite plutôt que vérifiée manuellement avant insertion
- Intégration du collector Greenhouse avec la base de données
- **Résultat du test d'idempotence :** 1ère exécution → 29 offres insérées, 0 doublon. 2ème exécution → 0 nouvelle offre, 29 doublons ignorés, total stable à 29 ✅
- Vérification directe en base via requête `SELECT COUNT(*) FROM jobs` et affichage complet du tableau

**Difficultés rencontrées et résolues :**
- Fichiers créés sans extension dans VS Code (`db` au lieu de `db.py`, `schema` au lieu de `schema.sql`) → Python ne reconnaissait pas les modules → correction en renommant avec les bonnes extensions
- Fichier `schema.sql` initialement vide (contenu jamais collé) → table `jobs` inexistante → erreur `no such table: jobs` → correction en collant le contenu SQL et en sauvegardant

**Livrable de fin de Semaine 1 validé :** ✅
- Au moins une entreprise avec offres réelles stockées en base (KoBold Metals — 29 offres)
- `SOURCES.md` complet et défendable
- Code versionné sur GitHub

---

## Semaine 2 — À venir
- Ajout de 2-3 sources supplémentaires (Redwood Materials, American Battery Technology Co., Mariana Minerals, Lilac Solutions)
- Généralisation du collector par ATS (actuellement spécifique à Greenhouse)
- Extraction et classification des compétences par LLM dans les 4 catégories définies
- Vérification manuelle sur un échantillon de 30 offres
