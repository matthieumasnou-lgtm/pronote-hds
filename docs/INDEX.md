# Dossier technique — Pronote / Home Assistant

Documentation de modifications **locales**, non officielles, comparees au code de hass-pronote **2.4.5** en octobre 2026. Ces notes sont anonymisees et ne contiennent pas de configuration de compte.

1. [Adaptation ENT Hauts-de-Seine et limites](ENT_HDS.md)
2. [Contournement informations/sondages et compaction des cours](FORMATTER_AND_TIMETABLE.md)
3. [Reductions de sollicitations et etat des donnees](ANTI_BAN_ET_DONNEES.md)
4. [Verifications, sauvegardes, futures mises a jour](VERIFICATIONS_ET_MISE_A_JOUR.md)

**Reproductibilite :** [script anti-bannissement 2.4.5](../maintenance/apply_pronote_safety.py). Le connecteur ENT publie a la racine est fourni pour **revue**, pas comme image garantie de l'installation locale. Le script anti-bannissement est limite a la version 2.4.5.

**Pour les developpeurs :** commencer par les deux premiers documents afin de distinguer les modifications potentiellement generalisables des contournements provisoires qui supprimeraient des fonctionnalites.
