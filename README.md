# rsmfExports

## A propos
Cet outil permet de télécharger des fichiers automatiquement sans avoir à parcourir l'interface RSMF. 
Il suffit de spécifier les écrans que l'outil doit parcourir et les champs d'exportation qui nous intéresses.

## Installation de l'outil
### Installation de Gecko driver
Gecko driver est indispensable, il permet de faire le lien entre le code python et le navigateur.
Gecko driver "geckodriver.exe" se trouve dans le repertoire Github, vous pouvez le copier dans n'importe quel dossier. Il faudra spécifier son emplacement dans le fichier de configuration de l'outil.

### Installation de Firefox
Si ce n'est pas deja fait un faut installer le navigateur Firefox sur votre ordinateur.

### Installation de Python
Depuis le centre logiciel installer Python 3.9

### Installation des modules Python requis
Tapez dans le terminal:\n
pip3 install selenium, keyring, eel\n
Puis encore dans le terminal, nous allons configurer votre mot de passe RSMF:\n
Tapez\n
python3\n
keyring.set_password("darwin", "username", "password")\n
Votre mot de passe a été enregistré par le système.
L'outil est prêt a être utilisé.

## Utilisation
Il faut maintenant configurer l'outil.
Dans le fichier config.json vous trouverez toutes informations qu'il faut renseigner. En particulier le nom d'utilisateur RSMF et le lien de l'éxecutable Geckodriver.

## Lancement
Dans un terminal dans le repertoire de l'outil, tapez:\n
python3 main.py
