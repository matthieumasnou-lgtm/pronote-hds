# Corrections locales

Le 9 octobre 2026, un contournement dans `pronote_formatter.py` a evite une erreur avec les informations et sondages, en renoncant temporairement au corps des messages et aux pieces jointes. Il faut restaurer ces fonctionnalites pour une proposition upstream.

La meme journee, `sensor.py` a reduit les attributs volumineux des emplois du temps de periode, pour rester sous la limite Home Assistant observee autour de 16 Kio. Cela ne constitue pas un plafonnement garanti.

## Difference exacte avec upstream 2.4.5

Dans `format_information_and_survey` de `pronote_formatter.py`, `attachments` passe de `format_attachment_list(information_and_survey.attachments())` a `[]`, et `content` passe de `information_and_survey.content()` a `None`.

Le contournement evite les appels sur des objets detaches d'une session fermee, mais supprime le corps et les pieces jointes de cette source. Il n'est pas adequat comme correctif final upstream.

Dans `sensor.py`, la methode `PronoteTimetableSensor.extra_state_attributes` applique aux seuls cours non `single_day` une projection des champs `start_at`, `end_at`, `start_time`, `end_time`, `lesson`, `classroom`, `canceled`, `status`, `teacher_name`, `background_color`, `memo`, `group_name`, `outing`, `exempted`, `test`, `detention`, `num`; valeurs `None` omises.
