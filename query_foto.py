#!/usr/bin/python2
# -*- coding: utf-8 -*-

#import foto, os, sys, time

# Directorio con imágenes jpg a comparar con la base de datos
query_dir="/home/lola/Documents/libvot/Pedro/capturas"

# Directorio en el que se encuentran los ejecutables de la librería libvot
exe_dir="/home/lola/Downloads/libvot-master/build/bin"

# Directorio de las imágenes de la base de datos completa
img_db_dir="/home/lola/Pictures/CdPas"

# Directorio del arbol creado por la función image_search
db_tree_dir="/home/lola/Documents/libvot/CdPas"

# Directorio base de partida y retorno
base_dir="/home/lola/Documents/libvot"

def get_photo(queue):
	while True:
		os.chdir(query_dir)
		img = foto.foto(640, 480)
		base = os.path.basename(img)
		name = os.path.splitext(base)[0]
		rank = "%s.rank" % name
		bashCommand="ls -d %s > image_list" % img
		os.system(bashCommand)

		bashCommand="%s/libvot_feature image_list" % exe_dir
		os.system(bashCommand)

		bashCommand="%s/web_search %s/%s.sift %s/image_list %s/db.out" %(exe_dir, query_dir, name, img_db_dir, db_tree_dir)
		os.system(bashCommand)

		f = open(rank, "r")
		db = f.readline()

		if "pasillo" in db:
			print("Pasillo")
		else:
			print("Caldo de pollo")
			queue.put("Stop!")

		return
