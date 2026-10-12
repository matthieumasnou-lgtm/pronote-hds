# Tests, limites et sauvegardes — Pronote HA

Observation du **12 octobre 2026** ; integration installee : **2.4.5**, mise a jour **2.4.6 proposee mais ignoree**. Ces resultats concernent une seule installation et ne constituent pas une recette upstream complete.

## Tests effectivement controles

- Dry-run du script de correctifs 2.4.5 : substitutions et syntaxe valides, sans toucher aux fichiers.
- Application avec copie des cinq fichiers originaux (`server_status.py`, `pronote_helper.py`, `coordinator.py`, `sensor.py`, `calendar.py`) dans un dossier horodate situe hors du repertoire HACS.
- Compilation Python des cinq fichiers : reussie.
- Second dry-run : detection des fichiers deja modifies, sans nouvelle ecriture.
- Validation globale de la configuration Home Assistant : reussie.
- Apres redemarrage : deux profils charges a 120 min, capteurs de notes disponibles avec `data_stale=false`, sondes serveur partageant le meme horodatage, serveur HTTP accessible.
