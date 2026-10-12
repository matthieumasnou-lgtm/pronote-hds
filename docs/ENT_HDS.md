# Connecteur ENT Hauts-de-Seine : adaptation locale

**Statut : prototype pour revue technique.** Le code partage dans [`ent_hauts_de_seine.py`](../ent_hauts_de_seine.py) est experimental et ne constitue pas une version officielle de `pronotepy` ni de `hass-pronote`.

Le 7-8 octobre 2026, l'integration devait utiliser le parcours ENC / CAS / Keycloak a la place du QR code indisponible dans ce parcours. `config_flow.py` ajoute exactement `enc_hauts_de_seine` a `get_ent_list()` si absent. `pronote_helper.py` reconnait ce choix et charge la fonction locale correspondante; les autres choix ENT continuent a passer par `pronotepy.ent`.

## Fonctionnement du module public

Le module verifie les URLs HTTPS attendues, limite les destinations de redirection a l'ENT officiel et au serveur Pronote cible, valide l'action du formulaire de connexion et refuse les redirections 307/308 apres le formulaire. Il utilise le mecanisme de session prevu par le portail, sans traitement de contournement CAPTCHA ou MFA.

## Verification et limites

Un essai reel avec un compte parent et deux profils enfants a ete rapporte comme fonctionnel sans QR code. Aucun jeu de tests reproductible n'est fourni dans ce depot. EduConnect, MFA, CAPTCHA et d'autres etablissements n'ont pas ete verifies.

**Comparaison confirmée le 12 octobre 2026 :** le fichier public (6 075 octets) et le fichier effectivement installe (6 863 octets) ont un **AST Python identique après exclusion des docstrings**. La syntaxe des deux fichiers est valide. Les differences relevees sont de la mise en forme, des commentaires et des docstrings : **la logique executable de l'adaptateur est la meme**. Les fichiers ne sont pas identiques octet pour octet, mais le connecteur publie est fidele au comportement du code installe. Cela ne remplace pas des tests sur d'autres portails ou environnements.

Verification reproductible : hachage SHA-256 de l'AST normalise (sans docstrings) = `67bfc21c4d25256197c56de099946010bd12e919d34604eaa9dcc4de2fe7055f` pour chacun. Comparaison effectuee entre le fichier local HA et la branche `main` du depot public a cette date.
