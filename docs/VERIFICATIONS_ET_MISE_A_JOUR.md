# Tests, limites et sauvegardes — Pronote HA

Observation du **12 octobre 2026** ; integration installee : **2.4.5**, mise a jour **2.4.6 proposee mais ignoree**. Ces resultats concernent une seule installation et ne constituent pas une recette upstream complete.

## Tests effectivement controles

- Dry-run du script de correctifs 2.4.5 : substitutions et syntaxe valides, sans toucher aux fichiers.
- Application avec copie des cinq fichiers originaux (`server_status.py`, `pronote_helper.py`, `coordinator.py`, `sensor.py`, `calendar.py`) dans un dossier horodate situe hors du repertoire HACS.
- Compilation Python des cinq fichiers : reussie.
- Second dry-run : detection des fichiers deja modifies, sans nouvelle ecriture.
- Validation globale de la configuration Home Assistant : reussie.
- Apres redemarrage : deux profils charges a 120 min, capteurs de notes disponibles avec `data_stale=false`, sondes serveur partageant le meme horodatage, serveur HTTP accessible.

## Procedures reproductibles et limites

Le script public [`maintenance/apply_pronote_safety.py`](../maintenance/apply_pronote_safety.py) accepte la version **2.4.5 uniquement** et controle les ancres avant toute modification. L'execution sans `--apply` est une verification sans ecriture; `--apply` sauvegarde puis applique. Il n'est pas prevu pour la 2.4.6.

HACS peut **remplacer les modifications locales** lors d'une mise a jour manuelle ou automatique. Ne pas mettre a jour directement sans effectuer un diff du nouveau code upstream et porter les correctifs compatibles. Les sauvegardes locales sont hors du dossier `custom_components` gere par HACS. Les mises a jour automatiques n'etaient pas activees et la version 2.4.6 avait ete ignoree.

Avant un retour arriere, arreter HA, restaurer individuellement les cinq originaux depuis le dernier dossier de sauvegarde puis redemarrer. Eviter toute restauration de sauvegarde systeme complete pour cette seule modification.
