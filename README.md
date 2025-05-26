# flasked

## Scénario

Attaque sur une box avec 2 flags intermédiaires et un flag final.

Les 3 grandes étapes:

- accès initial au panel d'administration
- obtention d'une RCE
- obtention du flag root

## Attaque

### Attaque 1: CSPT (Client-Side Path Traversal)

La première étape consiste à exploiter une CSPT2CSRF en enchaînant 2 attaques CSPT pour déclencher une requête contenant un jeton CSRF sur un endpoint arbitraire, afin de faire passer son propre compte en admin.

### Attaque 2: Environment injection

La deuxième étape consiste à obtenir une RCE sur le serveur en contrôlant l'environnement d'un processus python.

### Attaque 3: Exploitation d'une race condition sur la fonction `find`

La troisième étape consiste à lire le fichier `/root/flag.txt` à l'aide d'un binaire privilégié.

## Matériel

un petit bout de papier à filer à chaque équipe pour leur donner l'adresse (/ le port?) de leur instance. Une instance docker par équipe :D

## Répartition

dryy: création du chall

train & xpholey: beta testeurs

## Flags 🚩

1. `STHACK{I_dub_thee_Kn1ght_of_CSPT—m4y_y0ur_expl0its_be_z3ro-day_and_your_lo6s_forever_clean!}`
2. `STHACK{N0W_you're_3xecu7in6_c0de_on_my_M4ch1ne!}`
3. `STHACK{CSPT_2_CSPT_to_CSRF_2_ENV_1nject10n_RCE_to_r4ce_c0nd1ti0n_in_find_yes_this_flag_is_very_long}`

## Principe 💭

Attaque sur une box. Accès initial par le web.

## Configuration 🛠

Une instance par équipe sur un serveur.

## Write-up 📝

Voir [la solution](./solve/README.md) et [le script de résolution](./solve/solve.py)

## Contact 📲

dryy
