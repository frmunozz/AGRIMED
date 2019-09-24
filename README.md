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
	            |- figures/
	                |- image.png
	                |- plot.png
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
* notebooks: meteremos todos los notebooks que registren algun avance.

    * si su notebook guarda imagenes es recomendable derivarlas al subfolder figures/, pero esto depende de la situación.
* HITO: para dejar aqui todo el codigo utilizado para generar cada entrega de avance (esto es opcional dependiendo de cada entrega, pero seria bueno dejar un registro aqui de los avances)

* projectname: al final del proyecto debemos dejar un codigo funcional, posiblemente sea recomendable hacerlo como proyecto, creando un paquete python, entonces dejo esta carpeta planteada para dicho paquete, pero NO CREADA

* data: esta carpeta la manejaremos cada uno y los datos pesados los compartiremos por drive o algun otro medio, es importante recordar que todo dato debe ir dentro de esta carpeta.
    * la carpeta de los datos brutos "PAULA" cada uno la agrega a su data, el git esta configurado para ignorar esta carpeta al momento de realizar commits
    * si generan alguna carpeta de datos pesada procuren no subirla en su commit para que el repo no sea muy pesado.
* scripts: en caso que para ejecutar algun notebook creen un scriopt, lo ponen aqui. 

Si tienen alguna duda sobre esta estructura, pueden ver este enlace que la detalla mucho mas: https://gist.github.com/ericmjl/27e50331f24db3e8f957d1fe7bbbe510


## Commits y trabajo en paralelo

* a corto plazo no creo que terminemos trabajando sobre los mismos archivos, pero en caso que ocurra lo mejor es crear branches y asi evitar conflitos,
para ello les dejo este enlace que los detalla bien: https://jameschambers.co/writing/git-team-workflow-cheatsheet/.
Si mantenemos todo moodular, no caeremos en estos problemas hasta la etapa final.

* Como consejo, para evitar problemas muy serios, SIEMPRE hagan

        git pull
        
    antes de hacer un
        
        git push

## Mantener el trello siempre actualizado

* siempre que inicien o terminen de trabajar en algun tema, actualicen trello para mantener la comunicacion entre nosotros.
