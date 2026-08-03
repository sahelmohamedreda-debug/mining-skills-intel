# CATEGORIES.md — Référentiel de classification des compétences

**Statut : DOCUMENT DE RÉFÉRENCE FIXE**
Ces définitions ne doivent plus être modifiées une fois la classification démarrée (Jour 8). Toute modification ultérieure impliquerait de reclasser l'intégralité des offres déjà traitées.

---

## Principe général

Chaque compétence extraite d'une offre d'emploi doit être classée dans **une seule** des 4 catégories ci-dessous. Si une offre entière ne relève d'aucune des 4 catégories (ex : poste purement administratif/corporate), elle est marquée **hors périmètre** plutôt que classée de force (voir section "Cas hors périmètre").

---

## 1. Operational & Technical

**Définition :** compétences directement liées aux opérations minières concrètes — extraction, traitement du minerai, planification technique du site, ingénierie du terrain.

**Exemples de compétences :**
- Forage (drilling) et dynamitage (blasting)
- Planification et ordonnancement de mine (mine planning/scheduling)
- Géologie d'exploration et cartographie géologique
- Traitement et valorisation du minerai (ore processing, beneficiation)
- Métallurgie extractive
- Conduite d'engins miniers lourds (haul trucks, excavatrices)
- Ingénierie géotechnique (stabilité des parois et des sols)
- Gestion des résidus miniers (tailings management)
- Hydrogéologie appliquée à la mine

---

## 2. Health, Safety & Risk Management

**Définition :** compétences liées à la sécurité des personnes, la gestion des risques opérationnels, et la conformité réglementaire du site.

**Exemples de compétences :**
- Identification et évaluation des dangers
- Réponse d'urgence et premiers secours en milieu isolé
- Gestion des risques géotechniques (effondrements, glissements)
- Audits et inspections de sécurité
- Conformité réglementaire minière (normes nationales/internationales)
- Gestion de crise
- Sécurité incendie et gestion des explosifs
- Systèmes de management HSE (ex : ISO 45001)

---

## 3. Digital & Automation

**Définition :** compétences technologiques et numériques appliquées à l'exploration, l'exploitation ou l'optimisation minière.

**Exemples de compétences :**
- Télé-opération d'engins à distance
- Analyse de données de capteurs (IoT minier)
- Modélisation géologique 3D
- Intelligence artificielle / machine learning appliqués à l'exploration minière
- Automatisation des équipements (mine autonome)
- Systèmes SCADA / contrôle-commande
- Data science et ingénierie de données appliquées au secteur
- Développement logiciel pour des outils miniers/scientifiques

---

## 4. Soft & Leadership

**Définition :** compétences comportementales et de gestion, transversales à tous les métiers miniers.

**Exemples de compétences :**
- Communication (interne, parties prenantes, communautés locales)
- Gestion d'équipe et leadership
- Résolution de conflits
- Gestion de projet
- Prise de décision sous pression ou incertitude
- Négociation avec communautés/fournisseurs
- Mentorat et formation d'équipe

---

## Cas ambigus tranchés (référence pour le Jour 8)

| Compétence | Catégorie retenue | Justification |
|---|---|---|
| Data Scientist / Data Engineer (même appliqué à la mine) | Digital & Automation | Nature du métier fondamentalement numérique |
| Ingénieur sécurité utilisant l'IA (surveillance automatisée) | Health, Safety & Risk | La finalité (sécurité) prime sur l'outil utilisé |
| Gestion de projet minier | Soft & Leadership | Compétence de gestion transversale, pas technique au sens métier |
| Ingénieur géotechnique | Operational & Technical | Fait partie du cœur technique de la conception de mine |

---

## Cas hors périmètre (non classés)

Les offres purement corporate/administratives — comptabilité, juridique, ressources humaines, direction générale, exécutif — **ne sont pas classées** dans les 4 catégories ci-dessus.

**Justification :** le projet analyse la demande de *compétences minières* spécifiquement. Forcer un classement de ces postes dans une des 4 catégories fausserait les statistiques et n'apporterait pas d'information utile à l'objectif du projet (comprendre les besoins en formation/talents du cœur de métier minier).

**Traitement technique :** ces offres restent stockées en base de données (elles font partie des données collectées), mais sont marquées avec un champ distinct (ex : `category = "out_of_scope"` ou équivalent) plutôt que forcées dans une des 4 catégories. Elles peuvent être comptées séparément dans le dashboard final (ex : "X% des offres sont hors périmètre mining-skills"), ce qui est en soi une donnée intéressante à présenter.

**Exemples de postes hors périmètre observés (KoBold Metals) :** Assistant General Counsel, Corporate Accounting Lead, International Tax Senior Manager, Executive Assistant, Senior Treasury Accountant.

---

## Règle pour le flag `compliance_relevant`

Une compétence est marquée `compliance_relevant = true` si elle est **directement liée à une norme, une certification obligatoire, ou une obligation légale/réglementaire**, c'est-à-dire :
- Elle fait référence explicite à une norme ou certification (ex : ISO 45001, permis d'exploitation, certification HSE)
- Elle est requise par la loi ou la réglementation minière du pays concerné (ex : conformité environnementale obligatoire, habilitations de sécurité)
- Son absence exposerait l'entreprise à un risque légal ou réglementaire direct

**Ne sont PAS `compliance_relevant`** (même si liées à la sécurité) :
- Les compétences de sécurité générales sans référence normative explicite (ex : "bon esprit d'équipe en environnement à risque" reste `false`)
- Les compétences de gestion de risque business (financier, stratégique) sans lien réglementaire

**Exemples concrets :**
| Compétence | compliance_relevant |
|---|---|
| "Certification ISO 45001" | true |
| "Connaissance des réglementations minières locales" | true |
| "Habilitation permis de tir (explosifs)" | true |
| "Sensibilité à la sécurité au travail" | false |
| "Gestion des risques financiers" | false |
