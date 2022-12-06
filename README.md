# TP_FINAL-itba-cloud-data-engineering
Trabajo Práctico integratorio final de la certificación en data engineering del ITBA


1 Se crea el EC" y se conecta con Putty vía usuario ubuntu
2 Clonar repositorio e instalar docker
3 Dar los permisos necesarios a docker


sudo apt-get update
sudo apt install python3-pip
sudo apt install docker-compose
pip3 install apache-airflow[s3,aws,postgres]
https://phoenixnap.com/kb/install-docker-on-ubuntu-20-04 -> para instalar Docker
sudo chown ubuntu /var/run/docker.sock #Agregar usuario ubunto como permitido en docker
sudo usermod -a -G docker ubuntu #tambien agrega permisos


airflow users create \
    --username admin \
    --password admin \
    --firstname test \
    --lastname test \
    --role Admin \
    --email test
