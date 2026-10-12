# Mesures locales anti-bannissement et fiabilite (12 octobre 2026)

**Cible stricte :** integration HACS Pronote **2.4.5** sur Home Assistant. Code exact des modifications dans [`maintenance/apply_pronote_safety.py`](../maintenance/apply_pronote_safety.py) et procedure dans [`maintenance/PRONOTE_SAFETY.md`](../maintenance/PRONOTE_SAFETY.md).

## Frequence reelle

Les deux profils actifs etaient revenus au reglage par defaut de **15 minutes** lors de leur recreation. Le 12 octobre, leurs options `refresh_interval` ont ete fixees a **120 minutes** et relues apres application. Une ancienne entree de profil reste desactivee. Le total theorique passe de **192 a 24 cycles par jour** (2 profils). Un cycle produit plusieurs requetes; ce chiffre ne mesure pas les acces HTTP exacts. Une suspension d'adresse IP a ete constatee dans le journal, sans preuve du seuil ou de sa cause unique.

## Sondes HTTP et connexion

`server_status.py` : `PROBE_INTERVAL` de 5 a **60 minutes**, cache partage par URL et verrou `asyncio.Lock` pour que deux profils du meme serveur ne lancent pas deux sondes identiques. Le controle serveur se fait par GET HTTP; il ne constitue pas une connexion a la session parent.

`pronote_helper.py` : verrou global `threading.Lock` pendant la creation d'un client ; un compteur par couple (URL, utilisateur configure) limite les tentatives apres echec. Delais successifs **2 h, 4 h, 8 h, puis 12 h maximum**. Reinitialisation apres reussite. Etat uniquement en memoire : un redemarrage supprime l'historique de ces pauses. Tout echec de creation de client declenche le delai, pas seulement un bannissement reconnu.

Le verrou serialise aussi des comptes distincts dans ce processus. Aucune session parent unique n'est partagee entre les enfants : chaque profil conserve son cycle de recuperation.

## Repli sur anciennes donnees

`coordinator.py` : en cas d'echec complet, renvoie les anciennes donnees si elles existent au lieu de les remplacer par des valeurs vides. Lorsqu'une acquisition ne renvoie pas certaines notes ou moyennes, reprend uniquement `grades`, `averages`, `overall_average` pour la **meme periode scolaire**. Conservation d'un etat `stale` et de l'horodatage du dernier succes connu par cle.

`sensor.py` : verification de l'existence de `coordinator.data` avant acces aux valeurs; attribut `data_stale` et horodatage `updated_at` de la derniere acquisition connue. Une valeur ancienne ne doit pas etre interpretee comme une synchronisation recente.

`calendar.py` : une absence de `lessons_period` ne provoque plus la lecture d'une valeur `None`; `async_get_events` utilise une liste vide en l'absence de cours.

**Limites :** pas de persistance du cache ou du cooldown apres redemarrage, pas de mutualisation complete des clients parent, pas de verification du quota officiel ENT et pas d'assurance que tous les types de capteurs conservent leurs attributs durant une panne longue.
