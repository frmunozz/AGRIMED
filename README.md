# AGRIMED
proyecto de prediccion de heladas

## Notas para el equipo:
* definiremos una estructura de trabajo para mantener un orden, 
algunas carpetas/secciones no las usaremos aun, la estructura debera ser:


    	$ ls
	        |- notebooks/
	            |- exploracion.ipynb
	            |- filtrado.ipynb
	            ...
	            |- archive/
		            |- reduccion_no_en_uso.ipynb
		            ...
		    |- HITO/
		        |- HITO1
		            |- entrega.ipynb
		            |- entrega.pdf
		            ...
		        |- HITO2
		            ...
		        ...
	        |- projectname/
	            |- projectname/
		            |- __init__.py
		            ...
	            |- setup.py
	        |- README.md
	        |- data/
	            |- PAULA/
	            |- processed/
	            |- cleaned/
	            ...
	        |- scripts/
	            |- script1.py
	            ...
	            |- archive/
	                |- no-longer-useful.py
	                ...


Explicando el objetivo de cada carpeta:
* notebooks: meteremos todos los notebooks que registren algun avance 
* HITO: para dejar aqui todo el codigo utilizado para generar cada entrega de avance
* projectname: al final del proyecto debemos dejar un codigo funcional, posiblemente sea recomendable hacerlo como proyecto, creando un paquete python, entonces dejo esta carpeta planteada para dicho paquete, pero NO CREADA
* data: esta carpeta la manejaremos cada uno y los datos relevantes los compartiremos por drive o algun otro medio, es importante recordar que todo dato debe ir dentro de esta carpeta.
* scripts: en caso que para ejecutar algun notebook creen un scriopt, lo ponen aqui. 

Si tienen alguna duda de porque defini esta estructura, ya la use antes y ayuda bastante a ordenar codigo cuando los proyectos crecen. 
Tambien pueden ver este enlace que detalla casi la misma estructura: https://gist.github.com/ericmjl/27e50331f24db3e8f957d1fe7bbbe510


## Commits y trabajo en paralelo

* a corto plazo no creo que terminemos trabajando sobre los mismos archivos, pero en caso que ocurra lo mejor es crear branches y asi evitar conflitos,
para ello les dejo este enlace que los detalla bien: https://jameschambers.co/writing/git-team-workflow-cheatsheet/.
Si mantenemos todo moodular, no caeremos en estos problemas hasta la etapa final.

## Mantener el trello siempre actualizado

* siempre que inicien o terminen de trabajar en algun tema, actualicen trello para mantener la comunicacion entre nosotros.
