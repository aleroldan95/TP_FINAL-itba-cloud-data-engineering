## Trabajo Práctico integratorio final de la certificación en data engineering del ITBA

### **Objetivo**

Definir si Masla está feliz o triste mediante proceso de descarga, análisis de sentimiento y almacenamiento diario de tweet

### **Metodología**

1° Creación de elementos necesarios de AWS para realizar el proyecto: <br />
- RDS: utilizamos una base de datos Postgres, a la cuál solo se puede acceder desde la EC2 <br />
- VPC <br />
- EC2: instancia mediana para alogar airflow <br />
- Modificación de Inbound Roles para poder acceder a la interfás de airflow <br />

2° Puesta a punto de la EC2: <br />
- Instalación de elementos necesarios para el funcionamiento de airflow. Incluyendo upgrades e instalaciones de nuevas librerías

3° Utilización de Airflow: <br />
- Creación de DAGs: <br />
    - creación de tablas en base de datos en caso de ser necesario. Se utiliza la métodología de metabase de sqlalchemy <br />
  - inserción diaria de tweets, descargando directamente mediante API los tweets de Masla <br />
  - utilización de modelo machine learning que genera el sentimiento de los tweets. Valor entre 0 (malo) y 1 (bueno) <br />
  - creación de tweet diario resumiendo el estado de Masla y sus principales métricas <br />
  - Creación de conexión a Postgres y variable con las credenciales de API


### Diagrama de proceso
![Diagrama Proceso](https://github.com/aleroldan95/TP_FINAL-itba-cloud-data-engineering/blob/master/imagenes/Diagrama_TP_final.jpg)

Alogamos ariflow en un EC2 mediano, luego mediante la API de tweeter nos descargamos los tweets del día de la fecha de Masla. 
Como próximo paso procedemos a guardar dichos tweets en una base de datos relacional de RDS (previamente creada con 
columnas id, fecha y texto). Luego analizamos mediante la librería sentiment-spanish si el tweet es bueno, malo o neutral, 
también depositando la data en otra tabla de columnas id, sentimiento. Como último paso corre el tercer proceso, el cuál 
selecciona los tweets del día de la fecha, calcula la mediana del sentimiento y envía un tweet, según una condición arbitraria nuestra, 
si es un día "bearish" o "bullish" para nuestro buen amigo Masla. Utilizamos S3 para seleccionar ímagenes según esa condición,
simplemente para darle mas color al tweet resultante.

### Librerías 

Como librerías importantes utilizamos las siguientes:

- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html): librería de AWS para conectarse a recursos propios vía python. Lo utilizamos para acceder a las imágenes en el S3
- [tweepy](https://www.tweepy.org/): librería para comunicarnos con tweeter, funciona como API para descargar e insertar tweets
- [sentiment-spanish](https://pypi.org/project/sentiment-analysis-spanish/): librería que contiene un modelo ya entrenado de sentiment análisis en español. Debido a la dificultad de
encontrar una base de datos apropiada en español para poder entrenar nuestro propio modelo, preferimos utilizar esta librería 
  con el modelo ya entrenado 


### Resultado

A modo de ejemplo vemos un tweet final del proceso

![tweet_final](https://github.com/aleroldan95/TP_FINAL-itba-cloud-data-engineering/blob/master/imagenes/tweet_result.jpg)