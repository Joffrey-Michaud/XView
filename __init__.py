from update_project import is_up_to_date
print("c est l'init de xview")

if not is_up_to_date():
    print("# -------------------------------------------------------------------------- #")
    print("Votre version du projet XView n'est pas à jour. Vous pouvez le mettre à jour en exécutant 'git pull' dans le répertoire du projet.")
    print("# -------------------------------------------------------------------------- #")
else:
    print("Votre version du projet XView est à jour.")