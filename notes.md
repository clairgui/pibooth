# liste de problème
- Image qui freez ==> Dimension de la fenetre sur écran avec grosse résolution
- Image qui se mets parfois en miroir parfois non lors de la preview
- dimension photo crop preview non valable + dimension de la préview != dimension photo. Dimension de la preview != de dimension photo sur la configuration preview par défaut raspberrypi
-la preveiw n'est pas le flux video mais des images en mode préview affichées en loop => trop lent
- Flash de l'écran toujours actif même lorsque l'option est à false --> un écran blanc supplémentaire s'affiche lorsque le falsh est actif. 
- Cacher le nombre de photo prise depuis le début

- la classe base.py est la classe mère de libcamera.py (et toutes les classes filles camera_x.py)
23/08/2023: remettre en place l'effet mirroir sur la préview (Flip)


10/09/2023: le ratio entre la hauteur est la largeur de la preview est important. 
Une fenetre en 720 * 1280 (ratio de 1.77) ne donne pas le même rendu qu'une fentre en 640 * 480 (ratio de 1.33)
Il faut donc jouer sur ce ratio pour avoir une image de preview correspondant au format de photo voulu.
Pour le format de photo, celui ci s'adapte au template, 1 photo, 2 photos, 3 photos ou 4 photos.
Dans tous les cas les formats ne sont pas identique. A voir comment les faire correspondre avec la preview. 

14/10/2023: Version de pillow > 10.0 incomptable pour pibooth template pour le moment 

29/10/2023: croper les photos à la bonne taille (taille de preview)