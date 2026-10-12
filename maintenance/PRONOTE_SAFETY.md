# Pronote HDS — correctifs locaux anti-bannissement
Date: 12 octobre 2026. Installation Home Assistant OS / Pronote HACS **2.4.5**.

## Pourquoi
Après recréation des profils enfants le 8 octobre 2026, la fréquence de rafraîchissement est revenue sans le vouloir à **15 minutes par profil** (environ 192 connexions complètes par jour). Les journaux montrent une suspension IP lors d'une tentative d'authentification. Chaque profil a maintenant `refresh_interval: 120` via les options HA (environ **24 cycles/jour** ensemble), paramètre persistant dans HA indépendamment des fichiers.

## Correctifs de code
Déployés sur `/homeassistant/custom_components/pronote/` :
- `server_status.py` : vérification HTTP du serveur **toutes les 60 minutes**, cache/lock partagé par URL pour éviter les 2 probes simultanées des profils.
- `pronote_helper.py` : authentifications parent sérialisées, cooldown **2 h, 4 h, 8 h, puis 12 h max** après refus successifs ; remet à zéro après connexion réussie. Cooldown en RAM, réinitialisé après redémarrage HA.
- `coordinator.py` : sur échec complet, conserve les dernières données valides plutôt que d'effacer les capteurs ; sur échec de notes/moyennes, réutilise les données de la **même période scolaire** seulement.
- `sensor.py` : expose l'attribut `data_stale` et `updated_at` correspondant à la dernière acquisition réelle ; sécurise les lectures de données manquantes.
- `calendar.py` : garde-fous contre les données de coordination nulles.

Ce sont des correctifs locaux, **pas une version officielle de l'intégration**. La mutualisation intégrale d'une connexion parent unique (notes, devoirs...) n'est pas réalisée : Alicia et Olivia restent deux entrées distinctes.

## Réinstallation / mises à jour HACS
**ATTENTION : HACS écrase le dossier `custom_components/pronote` lors d'une mise à jour !** Ne pas installer automatiquement la mise à jour du dépôt d'origine. L'option auto-update est désactivée. L'offre **2.4.6** a été ignorée pour éviter un écrasement involontaire.

La source du correctif est versionnée dans `maintenance/apply_pronote_safety.py`, **avec vérification stricte `manifest.json.version == 2.4.5`** et remplacement ancré par signatures exactes. Après chaque mise à jour de Pronote, ne pas forcer l'ancien patch : examiner le diff upstream, porter le correctif sur la nouvelle version, tester, puis exécuter le script adapté.

Pour la **2.4.5 uniquement**, depuis Terminal & SSH de HA :

```sh
python3 /homeassistant/pronote_safety_patch.py               # vérifie sans écrire
python3 /homeassistant/pronote_safety_patch.py --apply       # sauvegarde + corrige
```

Le script est également dans ce dépôt pour archivage permanent. Il est idempotent sur les fichiers déjà patchés. Copie de secours automatique à chaque application dans `/homeassistant/pronote_local_backups/<horodatage>/`. Les fichiers originaux n'y sont jamais gérés par HACS.

## Vérifications après déploiement
1. Vérifier la syntaxe Python puis redémarrer HA pour charger les modules.
2. Confirmer que les deux profils restent `loaded`, à 120 minutes chacun.
3. Surveiller `sensor.pronote_masnou_{alicia,olivia}_grades` et le marqueur `data_stale`.
4. Les sondes `server_status` doivent partager la même date de vérification et avancer seulement toutes les 60 minutes.
5. Vérifier les journaux Pronote et ne pas forcer une reconnexion en boucle si le serveur suspend l'IP.

## Revenir en arrière
Arrêter HA avant restauration des fichiers Python, puis remettre les cinq fichiers depuis le dernier sous-dossier `pronote_local_backups` dans `custom_components/pronote`. Redémarrer HA. Garder les options de fréquence de 120 minutes.

## Limites
Aucune règle de quota officielle de Pronote/ENT n'est connue ici. Le correctif réduit fortement les requêtes et amortit les échecs, sans garantir l'absence de bannissement. Le cache `data_stale` protège l'affichage, mais il ne doit pas être confondu avec une synchronisation réussie.