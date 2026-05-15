FROM debian:12-slim

# Install python and systemd requirements
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    systemd \
    systemd-sysv \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install bacpypes --break-system-packages

WORKDIR /app
COPY server.py /app/server.py
COPY README.md /app/README.md
COPY config.json /app/config.json

# Create the systemd service file
RUN echo '[Unit]\n\
Description=BACnet Server\n\
After=network.target\n\
\n\
[Service]\n\
ExecStart=/usr/bin/python3 /app/server.py\n\
Restart=always\n\
\n\
[Install]\n\
WantedBy=multi-user.target' > /etc/systemd/system/bacnet.service

# Enable the service
RUN systemctl enable bacnet.service

# d2vm requires a root password for the VM
RUN echo "root:<your desired password>" | chpasswd
