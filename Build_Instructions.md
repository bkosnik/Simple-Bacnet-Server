## 🛠 Prerequisites

Ensure the following tools are installed on your **mrrobot** host:

* **Docker:** To build the initial container image.
* **d2vm:** The tool that converts Docker images to bootable disk formats.
* **qemu-utils:** Required for `qemu-img` conversions.

---

## 🏗 Build Phase 1: The Docker Image

The VM is based on a slim Debian 12 environment. Your directory structure should look like this:

```text
project-dir/
├── Dockerfile
├── server.py
├── config.json
└── README.md

```

### 1. Create the Dockerfile

```dockerfile
FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    systemd \
    systemd-sysv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up application directory
WORKDIR /app
COPY . .

# Install Python requirements
RUN pip install --no-cache-dir bacpypes

# Setup systemd service for the BACnet server
RUN echo '[Unit]\n\
Description=BACnet Server\n\
After=network.target\n\
\n\
[Service]\n\
ExecStart=/usr/bin/python3 /app/server.py\n\
WorkingDirectory=/app\n\
Restart=always\n\
\n\
[Install]\n\
WantedBy=multi-user.target' > /etc/systemd/system/bacnet.service

# Enable the service
RUN systemctl enable bacnet.service

# Standard BACnet/IP port
EXPOSE 47808/udp

```

### 2. Build the image

```bash
docker build -t bacnet-appliance:v1 .

```

---

## 💿 Build Phase 2: The VM Conversion

Now, use `d2vm` to extract the Docker filesystem into a bootable QCOW2 image.

```bash
# Convert to QCOW2 with 20GB of virtual space (sparse)
# -p sets the root password to 'root'
d2vm build -p root -o bacnet-server.qcow2 bacnet-appliance:v1

```

## If the VM Conversion fails you can create the VM direclty using this command:
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/build \
  -v $(pwd):/output \
  --workdir /build \
  --privileged \
  linkacloud/d2vm:latest build . \
  --output /output/bacnet-server.qcow2 \
  --network-manager ifupdown

  or below for vmdk

  docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/build \
  -v $(pwd):/output \
  --workdir /build \
  --privileged \
  linkacloud/d2vm:latest build . \
  --output /output/bacnet-server.vmdk \
  --network-manager ifupdown


---

## 📉 Optimization: Shrinking for Distribution

To ensure the file is small enough for the client, follow the **"Zero and Reclaim"** method.

### 1. Internal Cleanup (Inside the VM)

Boot the VM via QEMU:

```bash
qemu-system-x86_64 -m 1G -drive file=bacnet-server.qcow2 -nographic

```

Inside the VM console, run:

```bash
# Purge package cache
apt-get clean && apt-get autoremove --purge

# Zero out free space (This allows the host to compress the disk)
dd if=/dev/zero of=/zero_file bs=1M || rm /zero_file

# Shut down
poweroff

```

### 2. Final Conversion & Compression (On mrrobot)

Convert the "zeroed" image to the final distribution formats.

```bash
# Shrink and Reclaim QCOW2
qemu-img convert -f qcow2 -O qcow2 bacnet-server.qcow2 bacnet-server-dist.qcow2

# Convert to VMware/VirtualBox VMDK
qemu-img convert -f qcow2 -O vmdk -o subformat=monolithicSparse bacnet-server-dist.qcow2 bacnet-server-dist.vmdk

```

---

## 📦 Final Packaging

Bundle the optimized images with the configuration guide for the client.

```bash
tar -cvzf bacnet_gateway_release_v1.tar.gz \
    bacnet-server-dist.qcow2 \
    bacnet-server-dist.vmdk \
    README.md \
    config.json

```

---

## 🚀 Post-Build Verification

Verify the build works in a headless environment:

```bash
qemu-system-x86_64 -m 1G -drive file=bacnet-server-dist.qcow2,format=qcow2 -net nic -net user,hostfwd=udp::47808-:47808 -nographic

```

If the output shows `BACnet Server Initialized` and no `Tracebacks` appear in `journalctl -f` upon discovery, the build is ready for deployment.