# Pronote — ENT Hauts-de-Seine (experimental)

Experimental CAS/Keycloak authentication connector for [delphiki/hass-pronote issue #193](https://github.com/delphiki/hass-pronote/issues/193).

This is a **review-only patch**, not a complete Home Assistant integration or a tested upgrade to 2.4.6.

## Installation points

Copy `ent_hauts_de_seine.py` into `custom_components/pronote/`. In `config_flow.py`, add `enc_hauts_de_seine` to the ENT selector list. In `pronote_helper.py`, resolve that selector to the local `enc_hauts_de_seine` callable instead of looking it up in `pronotepy.ent`.

Do not overwrite the upstream integration with the author's entire local installation.

## Test status and limitations

The public ENT adapter has been **AST-verified against the locally running adapter** (same executable Python structure after removing docstrings; comments and formatting differ). The author reports successful use of one parent account with two child profiles, without a QR code. EduConnect, MFA and CAPTCHA have not been validated. Redirect handling, login error handling, and session renewal need independent review.

**Do not publish credentials, session cookies, tokens, or configuration exports.**

## Home Assistant — correctifs locaux

Voir [PRONOTE_SAFETY.md](maintenance/PRONOTE_SAFETY.md) et [apply_pronote_safety.py](maintenance/apply_pronote_safety.py) pour le correctif anti-bannissement, les sauvegardes, les limites de compatibilité et la marche à suivre avant toute mise à jour HACS.

## Notes de maintenance

Voir [l'index de documentation technique](docs/INDEX.md) pour les changements locaux verifies d'octobre 2026.
