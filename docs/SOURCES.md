# SOURCES.md — Droits de collecte des données

Ce document vérifie, pour chaque source retenue, si la collecte automatisée des offres d'emploi est autorisée. Deux niveaux sont distingués :
1. **Le site web principal de l'entreprise** (ex. `koboldmetals.com`) — non utilisé pour la collecte, vérifié par transparence
2. **La plateforme ATS réellement interrogée** (ex. `job-boards.greenhouse.io`) — c'est celle-ci qui compte, car c'est elle qu'on appelle techniquement

**Méthode de collecte du projet :** appel de l'API publique JSON de chaque ATS (endpoint documenté, lecture seule, sans authentification). Aucun scraping du site vitrine des entreprises n'est effectué.

---

## 1. KoBold Metals

- **ATS utilisé (source réelle des données) :** Greenhouse — board `koboldmetals` (+ `zambold`, `koboldmetalsdrc`)
- **robots.txt du site principal (koboldmetals.com) :** bloque uniquement `/wp-admin/` (configuration WordPress standard), sitemap fourni — aucune restriction générale
- **robots.txt de la plateforme ATS (job-boards.greenhouse.io) :** aucune directive disallow bloquante ; l'API Job Board est documentée officiellement par Greenhouse pour un usage par des tiers (developers.greenhouse.io)
- **Statut : ✅ AUTORISÉ**
- **Justification :** la collecte se fait via l'API publique documentée de Greenhouse, prévue pour cet usage. Le robots.txt du site principal, bien que non directement concerné, ne présente de toute façon aucune restriction.

## 2. Redwood Materials

- **ATS utilisé :** Greenhouse — board `redwoodmaterials`
- **robots.txt du site principal (redwoodmaterials.com) :** aucune restriction (`User-agent: * / Allow: *`), sitemap fourni
- **robots.txt de la plateforme ATS :** identique à KoBold Metals (même plateforme Greenhouse)
- **Statut : ✅ AUTORISÉ**
- **Justification :** même raisonnement que KoBold Metals — API publique Greenhouse documentée, site principal entièrement ouvert.

## 3. American Battery Technology Company

- **ATS utilisé :** Workable — `americanbatterytechnologycompany`
- **robots.txt du site principal (americanbatterytechnology.com) :** bloque des chemins techniques internes (recherche, flux RSS/trackback, wp-admin) via un bloc Yoast SEO standard — restrictions non liées aux offres d'emploi ni à l'ATS
- **robots.txt de la plateforme ATS (apply.workable.com) :** Workable documente et expose une API Job Board publique sans authentification, conçue pour un usage tiers, retournant les offres publiques par compte client
- **Statut : ✅ AUTORISÉ**
- **Justification :** la collecte passe uniquement par l'API publique Workable, prévue à cet effet. Les restrictions du site principal ne concernent pas les données collectées.

## 4. Mariana Minerals

- **ATS utilisé :** Ashby — `marianaminerals`
- **robots.txt du site principal (marianaminerals.com) :** `Allow: /` — totalement ouvert, sitemap fourni
- **robots.txt de la plateforme ATS (jobs.ashbyhq.com) :** à vérifier directement avant la mise en production (non bloquant a priori, Ashby propose également un accès public en lecture à ses job boards)
- **Statut : ✅ AUTORISÉ** (sous réserve de vérification finale du robots.txt d'ashbyhq.com avant le Jour 4)
- **Justification :** site principal sans restriction ; collecte prévue via l'API/JSON public du job board Ashby.

## 5. Lilac Solutions

- **ATS utilisé :** Rippling — board `lilac-solutions`
- **robots.txt du site principal (lilacsolutions.com) :** bloque des dossiers techniques (`/cpresources/`, `/vendor/`, `/.env`, `/cache/`) et bloque explicitement certains robots d'IA (GPTBot, Google-Extended, PerplexityBot) pour l'indexation du site vitrine
- **robots.txt de la plateforme ATS (ats.rippling.com) :** Rippling documente une API Job Board publique (`GET api.rippling.com/platform/api/ats/v1/board/{slug}/jobs`), sans authentification requise pour les offres publiques
- **Statut : ✅ AUTORISÉ**
- **Justification importante :** le blocage des bots IA (GPTBot etc.) sur `lilacsolutions.com` concerne l'**indexation par des moteurs de recherche/assistants IA du contenu du site vitrine** (pages produit, blog...), pas l'appel à l'API ATS de Rippling, qui est un service tiers séparé, distinct du site web de l'entreprise, et documenté pour un accès programmatique en lecture. On n'accède à aucun contenu du site `lilacsolutions.com` lui-même.

---

## Synthèse

| # | Entreprise | ATS | Statut | Méthode |
|---|---|---|---|---|
| 1 | KoBold Metals | Greenhouse | ✅ Autorisé | API publique JSON |
| 2 | Redwood Materials | Greenhouse | ✅ Autorisé | API publique JSON |
| 3 | American Battery Technology Co. | Workable | ✅ Autorisé | API publique JSON |
| 4 | Mariana Minerals | Ashby | ✅ Autorisé (à confirmer robots.txt ashbyhq.com) | API publique JSON |
| 5 | Lilac Solutions | Rippling | ✅ Autorisé | API publique JSON documentée |

## Principe général appliqué
- Seules les **API publiques documentées** des plateformes ATS sont utilisées — jamais de scraping agressif ni de contournement d'authentification
- Aucune donnée personnelle n'est collectée (uniquement les offres d'emploi : titre, lieu, description, département, date)
- Fréquence de collecte limitée à un run quotidien (Semaine 3), pas de sollicitation excessive des serveurs
- En cas de doute sur une source (ex. Ivanhoe Mines, Core Lithium — accès uniquement via scraping HTML, pas d'API), la source est classée en 2e priorité et documentée séparément avant toute utilisation
