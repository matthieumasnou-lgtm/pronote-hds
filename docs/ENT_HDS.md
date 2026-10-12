# Connecteur ENT Hauts-de-Seine : adaptation locale

**Statut : prototype pour revue technique.** Le code partage dans [`ent_hauts_de_seine.py`](../ent_hauts_de_seine.py) est experimental et ne constitue pas une version officielle de `pronotepy` ni de `hass-pronote`.

Le 7-8 octobre 2026, l'integration devait utiliser le parcours ENC / CAS / Keycloak a la place du QR code indisponible dans ce parcours. `config_flow.py` ajoute exactement `enc_hauts_de_seine` a `get_ent_list()` si absent. `pronote_helper.py` reconnait ce choix et charge la fonction locale correspondante; les autres choix ENT continuent a passer par `pronotepy.ent`.

## Fonctionnement du module public

Le module verifie les URLs HTTPS attendues, limite les destinations de redirection a l'ENT officiel et au serveur Pronote cible, valide l'action du formulaire de connexion et refuse les redirections 307/308 apres le formulaire. Il utilise le mecanisme de session prevu par le portail, sans traitement de contournement CAPTCHA ou MFA.

## Verification et limites

Un essai reel avec un compte parent et deux profils enfants a ete rapporte comme fonctionnel sans QR code. Aucun jeu de tests reproductible n'est fourni dans ce depot. EduConnect, MFA, CAPTCHA et d'autres etablissements n'ont pas ete verifies.

Le fichier localement installe n'a **pas** ete confirme identique octet pour octet au fichier publie : les tailles observees different. La version publique reste une **proposition pour revue**, pas un export du Raspberry Pi. Il faut examiner manuellement les differences, sans exposer la configuration de l'installation, avant toute contribution.
