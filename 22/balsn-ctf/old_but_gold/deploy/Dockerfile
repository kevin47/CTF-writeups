FROM ubuntu:20.04
MAINTAINER kevin47
RUN useradd -m old_but_gold
RUN chmod 774 /tmp
RUN chmod -R 774 /var/tmp
RUN chmod -R 774 /dev
RUN chmod -R 774 /run
RUN chmod 1733 /tmp /var/tmp /dev/shm
RUN chown -R root:root /home/old_but_gold
WORKDIR /home/old_but_gold
CMD ["/home/old_but_gold/old_but_gold"]
