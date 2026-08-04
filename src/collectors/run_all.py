import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from db.db import init_db, count_jobs

import greenhouse
import workable
import ashby
import rippling
from sources_config import SOURCES

# Associe chaque nom d'ATS au module qui sait le gérer
COLLECTORS = {
    "greenhouse": greenhouse,
    "workable": workable,
    "ashby": ashby,
    "rippling": rippling,
}


if __name__ == "__main__":
    init_db()

    print(f"Lancement de la collecte sur {len(SOURCES)} sources...\n")

    for ats_name, identifier, company_name in SOURCES:
        collector_module = COLLECTORS[ats_name]
        print(f"→ {company_name} ({ats_name})")
        try:
            collector_module.run(identifier, company_name)
        except Exception as e:
            print(f"  ERREUR sur {company_name} : {e}")

    print(f"\nTotal en base après collecte : {count_jobs()}")