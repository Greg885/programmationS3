nom = "auth.txt"
try:
    with open(nom, "r") as infile, open("copie.txt", "w") as outfile:
        # Lecture d’une ligne
        ligne = infile.readline()
        print("ligne 1 = ", ligne)
        input("Press enter to continue")
        # Lecture du restant des lignes

except (FileNotFoundError):
    print("le fichier n'est pas trouver")

except (IOError):
    print("pas acces au Disque Dur")

except (FileExistsError):
    print("Le fichier existe déjà")

except (PermissionError):
    print("Vous n'avez pas les permissions")
