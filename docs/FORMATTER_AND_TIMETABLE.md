# Corrections locales

Le 9 octobre 2026, un contournement dans `pronote_formatter.py` a evite une erreur avec les informations et sondages, en renoncant temporairement au corps des messages et aux pieces jointes. Il faut restaurer ces fonctionnalites pour une proposition upstream.

La meme journee, `sensor.py` a reduit les attributs volumineux des emplois du temps de periode, pour rester sous la limite Home Assistant observee autour de 16 Kio. Cela ne constitue pas un plafonnement garanti.
