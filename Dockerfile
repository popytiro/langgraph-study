FROM ubuntu:24.04

RUN apt update && apt install -y python3.12 python3-pip

CMD [ "bash" ]