##Trabajo Práctico integratorio final de la certificación en data engineering del ITBA

###**Objetivo**

Definir si Masla está feliz o triste

###**Metodología**

1° Creación de elementos necesarios de AWS para realizar el proyecto: <br />
- RDS: utilizamos una base de datos Postgres, a la cuál solo se puede acceder desde la EC2 <br />
- VPC <br />
- EC2: instancia mediana para alogar airflow <br />
- Modificación de Inbound Roles para poder acceder a la interfás de airflow <br />

2° Puesta a punto de la EC2: <br />
- Instalación de elementos necesarios para el funcionamiento de airflow

3° Utilización de Airflow: <br />
- Creación de DAGs: <br />
    - creación de tablas en base de datos en caso de ser necesario. Se utiliza la métodología de metabase de sqlalchemy <br />
  - inserción diaria de tweets, descargando directamente mediante API los tweets de Masla <br />
  - utilización de modelo mahcine learning que genera el sentimiento de los tweets. Valor entre 0 (malo) y 1 (bueno) <br />
  - creación de tweet diario resumiendo el estado de Masla y sus principales métricas <br />
  - Creación de conexión a Postgres y variable con las credenciales de API



