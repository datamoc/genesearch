#!/usr/bin/env python3
"""Point d'entrée unique des outils de généalogie (testé avec Python 3.13, conçu pour 3.8 ou plus ; aucune dépendance obligatoire).

Usage : python genealogie.py <commande> [arguments]

  init      <base.db>                       crée la base d'enquête
  importer  <arbre.ged> <base.db> [--label]  charge un GEDCOM (niveau B)
  exporter  <base.db> <arbre.ged>            écrit un GEDCOM
  analyse   <base.db> <cmd> [options]        stats, tache, frontiere, anomalies, manquants,
                                             correlations, parente A B, trouver MOTIF
  valider   <base.db> [--racine X] [--lecteur "Prénom"]   interface locale de validation
  rapport   <base.db> <sortie.pdf> [--tout|--html|--titre "…"]   rapport de preuves et de questions
  devolution <base.db> <défunt> [--deces ANNEE] [--tous] [--md f.md]   héritiers possibles par ordre (France)

`python genealogie.py <commande> --help` affiche l'aide de l'outil concerné.
"""
import runpy
import sys
from pathlib import Path

COMMANDS = {
    "init": "init_db.py",
    "importer": "gedcom_import.py",
    "exporter": "gedcom_export.py",
    "analyse": "analyse_arbre.py",
    "valider": "validation_ui.py",
    "rapport": "rapport_preuves.py",
    "devolution": "devolution.py",
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help") or sys.argv[1] not in COMMANDS:
        print(__doc__)
        return 0 if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help") else 2
    script = Path(__file__).parent / COMMANDS[sys.argv[1]]
    sys.argv = [str(script)] + sys.argv[2:]
    sys.path.insert(0, str(script.parent))
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as e:
        if isinstance(e.code, str):  # message d'erreur de l'outil : à afficher, pas à avaler
            print(e.code, file=sys.stderr)
            return 1
        return e.code if isinstance(e.code, int) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
