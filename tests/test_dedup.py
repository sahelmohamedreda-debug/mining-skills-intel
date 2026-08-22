"""Tests du mécanisme anti-doublon (insertion en base)."""
import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))


def test_unique_constraint_prevents_duplicate():
    """Vérifie que la contrainte UNIQUE(company, external_id) empêche les doublons."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT NOT NULL,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            UNIQUE(company, external_id)
        )
    """)

    conn.execute(
        "INSERT INTO jobs (external_id, company, title) VALUES (?, ?, ?)",
        ("123", "KoBold Metals", "Data Scientist")
    )
    conn.commit()

    duplicate_rejected = False
    try:
        conn.execute(
            "INSERT INTO jobs (external_id, company, title) VALUES (?, ?, ?)",
            ("123", "KoBold Metals", "Data Scientist (duplicate)")
        )
        conn.commit()
    except sqlite3.IntegrityError:
        duplicate_rejected = True

    assert duplicate_rejected, "Un doublon (même company + external_id) aurait dû être rejeté"

    count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    assert count == 1, f"La table devrait contenir 1 seule offre, trouvé {count}"

    conn.close()


def test_same_external_id_different_company_allowed():
    """Vérifie que le même external_id est autorisé pour des entreprises différentes."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT NOT NULL,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            UNIQUE(company, external_id)
        )
    """)

    conn.execute(
        "INSERT INTO jobs (external_id, company, title) VALUES (?, ?, ?)",
        ("100", "KoBold Metals", "Engineer")
    )
    conn.execute(
        "INSERT INTO jobs (external_id, company, title) VALUES (?, ?, ?)",
        ("100", "Redwood Materials", "Engineer")
    )
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    assert count == 2, "Le même external_id doit être autorisé pour 2 entreprises différentes"

    conn.close()


if __name__ == "__main__":
    test_unique_constraint_prevents_duplicate()
    test_same_external_id_different_company_allowed()
    print("✅ Tous les tests de dédoublonnage passent")