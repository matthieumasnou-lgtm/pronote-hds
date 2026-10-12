# Connecteur ENT Hauts-de-Seine : adaptation locale

**Statut : prototype pour revue technique.** Le code partage dans [`ent_hauts_de_seine.py`](../ent_hauts_de_seine.py) est experimental et ne constitue pas une version officielle de `pronotepy` ni de `hass-pronote`.

Le 7-8 octobre 2026, l'integration devait utiliser le parcours ENC / CAS / Keycloak a la place du QR code indisponible dans ce parcours. `config_flow.py` ajoute exactement `enc_hauts_de_seine` a `get_ent_list()` si absent. `pronote_helper.py` reconnait ce choix et charge la fonction locale correspondante; les autres choix ENT continuent a passer par `pronotepy.ent`.
