# Sources candidates — Identification des ATS

## ✅ TABLEAU FINAL — Sources retenues (Jour 2 terminé)

| # | Entreprise | Domaine d'activité | ATS | Board / Identifiant | Type d'accès |
|---|---|---|---|---|---|
| 1 | **KoBold Metals** | Exploration minière assistée par IA (Zambie/RDC/US) | Greenhouse | `koboldmetals` (+ `zambold`, `koboldmetalsdrc`) | API publique JSON |
| 2 | **Redwood Materials** | Recyclage batteries / matériaux critiques | Greenhouse | `redwoodmaterials` | API publique JSON |
| 3 | **American Battery Technology Company** | Recyclage batteries / lithium | Workable | `americanbatterytechnologycompany` | API publique JSON |
| 4 | **Mariana Minerals** | Exploration minière | Ashby | `marianaminerals` | API publique JSON |
| 5 | **Lilac Solutions** | Extraction directe de lithium | Rippling | `lilac-solutions` | API publique JSON documentée (`api.rippling.com/platform/api/ats/v1/board/{slug}/jobs`) |

**Pistes secondaires (2e priorité, scraping HTML nécessaire) :** Ivanhoe Mines (Simplify HR), Core Lithium (BambooHR)

---

Jour 2 du projet. Pour chaque entreprise : trouve la page carrières, clique sur une offre précise, regarde l'URL, remplis le tableau.

Rappel des types d'ATS à repérer dans l'URL :
- `boards.greenhouse.io/...` ou `job-boards.greenhouse.io/...` → **Greenhouse**
- `jobs.lever.co/...` → **Lever**
- `jobs.ashbyhq.com/...` → **Ashby**
- `apply.workable.com/...` → **Workable**
- `[entreprise].wd1.myworkdayjobs.com/...` (wd1, wd3, wd5...) → **Workday**
- domaine propre à l'entreprise, rien d'autre → **Propriétaire**

---

| # | Entreprise | URL fournie | ATS identifié (via pattern URL) | Confiance | API publique connue ? | Retenue ? | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Barrick Mining | jobs.barrick.com/...#en/sites/CX_1001 | Oracle Recruiting Cloud | Élevée | Non | ❌ Non | SPA en JS, pas d'API simple |
| 2 | Rio Tinto | jobs.riotinto.com/fr/details-du-poste/... | Plateforme non identifiée avec certitude (structure type "career site" générique, possiblement Talentsoft/Cegid) | Faible | Inconnue | ⚠️ À vérifier | Regarder le code source (Ctrl+U) pour confirmer |
| 3 | Newmont | jobs.newmont.com/us/en/mining-operations | Plateforme de type "career site builder" (probablement Phenom People, backend Workday possible) | Faible | Inconnue | ⚠️ À vérifier | Pattern `/us/en/` typique de Phenom |
| 4 | OCP Group | careers.ocpgroup.ma/en/careers/... | Portail propriétaire | Moyenne | Non | ❌ Non | Site custom OCP |
| 5 | Anglo American | angloamerican.com/careers/job-opportunities/apply | Portail propriétaire (sur domaine propre) | Élevée | Non | ❌ Non | |
| 6 | Vale | vale.com/programa-de-formacao-profissional | Portail propriétaire | Élevée | Non | ❌ Non | Attention : ce lien est une page de programme spécifique (stage/formation), pas la liste générale des offres |
| 7 | Groupe Managem | managem.csod.com/ux/ats/careersite/4/... | **Cornerstone OnDemand (CSOD)** | Élevée | Non documentée publiquement | ❌ Non (a priori) | Identifiable au domaine `csod.com` |
| 8 | Freeport-McMoRan | talent.fmjobs.com/careers | Plateforme non identifiée avec certitude | Faible | Inconnue | ⚠️ À vérifier | |
| 9 | Lithium Americas | (vu précédemment) | **Workday** | Élevée (confirmé) | API interne existe mais non publique/stable | ⚠️ Possible mais complexe | |
| 10 | MP Materials | workforcenow.adp.com/... | **ADP Workforce Now (recrutement)** | Élevée | Non | ❌ Non | Domaine `adp.com` = confirmation directe |
| 11 | Ivanhoe Mines | ivanhoemines.simplify.hr/Vacancy/... | **Simplify HR** (ATS sud-africain) | Élevée | Inconnue | ⚠️ À vérifier | Domaine `simplify.hr` = confirmation directe |
| 12 | First Quantum Minerals | first-quantum.com/careers/join-us/?job_id=... | Portail propriétaire (probablement plugin sur site WordPress/CMS) | Moyenne | Non | ❌ Non | |
| 13 | Teck Resources | jobs.teck.com/job/.../52033-en_US | Probablement **Avature** (pattern d'URL caractéristique) | Moyenne | Non | ❌ Non | À confirmer via code source |
| 14 | Kinross Gold | jobs.kinross.com/go/.../1552100/ | Plateforme non identifiée avec certitude (pattern `/go/.../ID/`) | Faible | Inconnue | ⚠️ À vérifier | |
| 15 | Coeur Mining ⚠️ | career17.**sapsf.com**/...company=**newgoldinc**... | **SAP SuccessFactors** | Élevée | Non | ❌ Non | ⚠️ Le paramètre `company=newgoldinc` indique que ce lien pointe vers **New Gold Inc**, pas Coeur Mining — à revérifier ! |
| 16 | Hecla Mining | workforcenow.adp.com/... | **ADP Workforce Now (recrutement)** | Élevée | Non | ❌ Non | Même plateforme que MP Materials |

---

---

## Nouvelles pistes — entreprises mining-tech / juniors (plus prometteuses)

| # | Entreprise | Ce qu'on sait | ATS identifié | Confiance | Retenue ? |
|---|---|---|---|---|---|
| 17 | **KoBold Metals** (exploration minière assistée par IA — Zambie/RDC/US) | Confirmé directement via les URLs de postes trouvées | **Greenhouse** — 3 boards distincts : `koboldmetals`, `zambold` (Zambie), `koboldmetalsdrc` (RDC) | Élevée (confirmé) | ✅ **Oui — excellent candidat** |
| 18 | **Redwood Materials** (recyclage batteries/matériaux critiques) | Confirmé via URL d'offre trouvée par l'utilisateur | **Greenhouse** — board `redwoodmaterials` | Élevée (confirmé) | ✅ **Oui** |
| 19 | **American Battery Technology Company** | Confirmé via URL d'offre trouvée par l'utilisateur | **Workable** — `americanbatterytechnologycompany` | Élevée (confirmé) | ✅ **Oui — 1er exemple Workable** |
| 20 | **Mariana Minerals** | Confirmé via URL d'offre trouvée par l'utilisateur | **Ashby** — `marianaminerals` | Élevée (confirmé) | ✅ **Oui — 1er exemple Ashby** |
| 21 | **Lilac Solutions** | Confirmé via URL d'offre trouvée par l'utilisateur | **Rippling** — board `lilac-solutions`, API documentée `api.rippling.com/platform/api/ats/v1/board/{slug}/jobs` | Élevée (confirmé) | ✅ **Oui — 4ème ATS différent** |
| 20 | Perpetua Resources | Pas encore vérifié | — | — | ⚠️ À vérifier |
| 21 | Solaris Resources | Pas encore vérifié | — | — | ⚠️ À vérifier |

**Ressource utile trouvée :** un guide technique récent recense les ATS avec API publique documentée (endpoints exacts) — Greenhouse, Lever, Ashby, Workable, Recruitee, Personio. Utile pour la Semaine 1-2 quand tu coderas les collectors : https://cavuno.com/blog/ats-platforms-public-job-posting-apis

---

## Légende colonne "Retenue pour le projet ?"
- ✅ Oui — ATS avec API publique simple (Greenhouse, Lever, Ashby, Workable)
- ⚠️ Peut-être — Workday (API plus complexe mais possible, à tester)
- ❌ Non — portail propriétaire fermé, pas d'API accessible

## Objectif de fin de journée
Avoir identifié au moins **5 à 8 entreprises "✅ Oui"**, prêtes à être utilisées pour la collecte (Semaine 1, Jour 4-5 et Semaine 2, Jour 7).

## Rappel
N'oublie pas de reporter aussi dans `docs/SOURCES.md` la vérification des droits de collecte (robots.txt + CGU) pour chaque source retenue — c'est une étape séparée, obligatoire avant de coder le collector (Jour 3).
