# Integration dans les tableaux de bord Home Assistant

Ces modifications de configuration HA sont **distinctes du code de `hass-pronote`** et ne sont pas proposees comme patch upstream.

Les 8–12 octobre 2026, des vues familiales et deux vues de suivi scolaire ont ete configurees pour afficher les cours, devoirs, notes et moyennes. Un correctif de rendu des dates de devoirs a accepte les valeurs de type `date` ou texte. Des notifications suivent les nouvelles notes ou notes corrigees, les evolutions de moyenne, les absences, les retards, les absences de professeurs et les cours annules. Le suivi des devoirs coches a egalement fait l'objet d'une automatisation.

Lors de l'inspection du 12 octobre, les automatisations de notes et de moyennes inspectees reposaient sur des declencheurs de changement d'etat des capteurs; elles n'executaient pas `homeassistant.update_entity` et ne provoquaient donc pas de sollicitation supplementaire du portail.

Les configurations privees (identifiants d'entites nominatifs, destinataires et contenu des notifications, personnes et appareils) ne sont pas exportees. Cette note decrit les **usages** et des correctifs d'affichage, sans pretendre verifier l'etat actuel de chaque carte ou automatisation.