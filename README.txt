Document d'installation - CE DOCUMENT N'EST PAS FINAL

1) https://github.com/Greg885/programmationS3
2) Pour le serveur sur une VM (Debian12):
	passer en super_user
	apt install python3
	apt install git
	git clone https://github.com/Greg885/programmationS3
3) Puis lancer le serveur : 
	cd programmationS3/SAE3.02/Graphique/PyQt/
	cre un environement :
		apt install python3.11-venv
		python3 -m venv venv
		source venv/bin/activate
	Lancer le serveur :
		pip install psutil
		python3 master.py 5 <<<<< nombe de tache avant slave
	Prendre l'ip :
		ip a

4) Lancer le client :
	Telecharger l'archive ZIP
	Extraire les fichiers
	Dans un CMD se déplacer jusqu'à ..\programmationS3-main\programmationS3-main\SAE3.02\Graphique\PyQt
		Sur un client (Windows):
			Ping l'@IP du serveur pour verifier la communication
			>python client.py
		Renseigner l'@IP du Serveur dans le champs correspondant
	Charger un fichier > Remonter l'arborescence jusqu'à SAE3.02 > ScriptTest
	Selectionner le bon type de fichier dans l'interface
	Envoyer au serveur
	
		

		

	
