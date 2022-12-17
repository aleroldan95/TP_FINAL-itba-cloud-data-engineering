# TP_FINAL-itba-cloud-data-engineering
Trabajo Práctico integratorio final de la certificación en data engineering del ITBA

Objetivo

Definir si Masla está feliz o triste

Metodología

1° Creación de elementos necesarios de AWS para realizar el proyecto:
    - RDS: utilizamos una base de datos Postgres, a la cuál solo se puede acceder desde la EC2
    - VPC
    - EC2: instancia mediana para alogar airflow
    - Modificación de Inbound Roles para poder acceder a la interfás de airflow

2° Puesta a punto de la EC2:
    - Instalación de elementos necesarios para el funcionamiento de airflow

3° Utilización de Airflow:
    - Creación de DAGs:
        > creación de tablas en base de datos en caso de ser necesario. Se utiliza la métodología de metabase de sqlalchemy
        > inserción diaria de tweets, descargando directamente mediante API los tweets de Masla
        > utilización de modelo mahcine learning que genera el sentimiento de los tweets. Valor entre 0 (malo) y 1 (bueno)
        > creación de tweet diario resumiendo el estado de Masla y sus principales métricas
    - Creación de conexión a Postgres y variable con las credenciales de API



