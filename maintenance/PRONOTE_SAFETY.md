# Correctifs locaux Pronote — 12 octobre 2026

**Compatible seulement avec hass-pronote 2.4.5.** Ce fichier est un sommaire public anonymise. Les modifications, limites et tests sont documentes en detail dans [docs/INDEX.md](../docs/INDEX.md).

Deux profils actifs ont ete configures avec `refresh_interval: 120`. Le script [apply_pronote_safety.py](apply_pronote_safety.py) modifie cinq fichiers : `server_status.py` (sonde HTTP horaire mutualisee), `pronote_helper.py` (delais apres erreur), `coordinator.py` (conservation des anciennes donnees), `sensor.py` (attribut `data_stale`), `calendar.py` (gestion des cours absents).

Executer d'abord le script sans argument (verification), puis `--apply` pour creer une sauvegarde et appliquer les changements. Les originaux sont conserves dans `/homeassistant/pronote_local_backups/`.

Attention : une mise a jour HACS peut ecraser les correctifs. La version 2.4.6 a ete ignoree sur l'installation de reference. Ne jamais appliquer ce script a une autre version sans une revue de compatibilite.
