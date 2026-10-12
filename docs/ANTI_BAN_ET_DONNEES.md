# Mesures locales anti-bannissement et fiabilite (12 octobre 2026)

**Cible stricte :** integration HACS Pronote **2.4.5** sur Home Assistant. Code exact des modifications dans [`maintenance/apply_pronote_safety.py`](../maintenance/apply_pronote_safety.py) et procedure dans [`maintenance/PRONOTE_SAFETY.md`](../maintenance/PRONOTE_SAFETY.md).

## Frequence reelle

Les deux profils actifs etaient revenus au reglage par defaut de **15 minutes** lors de leur recreation. Le 12 octobre, leurs options `refresh_interval` ont ete fixees a **120 minutes** et relues apres application. Une ancienne entree de profil reste desactivee. Le total theorique passe de **192 a 24 cycles par jour** (2 profils). Un cycle produit plusieurs requetes; ce chiffre ne mesure pas les acces HTTP exacts. Une suspension d'adresse IP a ete constatee dans le journal, sans preuve du seuil ou de sa cause unique.
