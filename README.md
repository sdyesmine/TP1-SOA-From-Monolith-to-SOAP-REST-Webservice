# Compte Rendu : Lab 1 - From Monolith to SOAP & REST Webservice

**Réalisé par :** Yesmine Saied IA3.1
**Cours :** Architecture Orientée Service (SOA)

---

## Partie 1 : Version monolithique (sans SOA)

**Objectif :** Implémenter toute la logique de gestion de la bibliothèque dans un seul script Python. L'interface utilisateur (PyQt5) et l'accès à la base de données (SQLAlchemy/PostgreSQL) sont centralisés dans le fichier `monolith.py`.

**Fonctionnalités implémentées :**
- Connexion à la base de données PostgreSQL via SQLAlchemy.
- Opérations CRUD (Ajouter, Lire, Modifier, Supprimer) fonctionnelles sur la table `Book`.
- Validation stricte des données : blocage des ID invalides, et interdiction des stocks et tarifs négatifs.

**Réponse à la question du TP : Quelles sont les limites de cette approche monolithique ?**
L'approche monolithique, bien que simple à mettre en place initialement, présente plusieurs limites majeures :
1. **Couplage fort :** Le code de l'interface graphique (UI) est intimement lié à la logique métier et à l'accès aux données. Une modification de la base de données implique souvent de retoucher l'interface.
2. **Fermeture au réseau :** Le système n'est pas distribué et s'exécute uniquement en local. Il est impossible pour d'autres clients (comme une application mobile ou un site web externe) de consommer ces données, car aucune API n'est exposée.
3. **Problème d'évolutivité (Scalability) :** Si l'application s'enrichit de nouvelles fonctionnalités, le fichier unique deviendra très lourd, difficile à maintenir, à tester et à faire évoluer en équipe.

### Captures d'écran - Tests de la Partie 1

**1. Test de succès (Ajout et affichage des livres) :**
![Test Succès Monolithe](captures/p1_succes.png)

**2. Test de validation (Erreur bloquée lors d'une saisie invalide) :**
![Test Erreur Monolithe](captures/p1_erreur.png)

---