# BACnet Point Server

This virtual appliance provides a standalone BACnet/IP simulation environment for testing and integration purposes. 
It is built on **Debian 12** and utilizes the **BACpypes** stack.

## 🛠 Device Configuration

The server's identity on the network is determined by its **Device ID**. You can customize this without modifying the source code.

### ⚙️ Advanced Configuration
Edit `/app/config.json` to customize the server. 

**Example `config.json`:**
```json
{
  "device_id": 5555,
  "port": 47809,
  "av_count": 50,
  "bv_count": 20,
  "mv_count": 5,
  "object_name": "Custom-Gateway"
}


3. **Enter a new ID**: Replace the existing number with your desired ID (range: `0` to `4,194,302`), Device name, desired point counts, be reasaonable.
4. **Save and Exit**: Press `Ctrl+O`, `Enter`, then `Ctrl+X`.
5. **Restart the Service**:
```bash
systemctl restart bacnet

```

> [!NOTE] Default Config is as follows:
# --- Default Configuration ---
DEFAULT_CONFIG = {
    "device_id": 10123,
    "port": 47808,
    "av_count": 10,
    "bv_count": 10,
    "mv_count": 10,
    "object_name": "Simple-Point-Server-01"
}

---

## 📊 Point Map

The server hosts 30 objects, all of which are **writable** and support **mutable names and descriptions**.

| Object Type | Count | Instance Range | Units / States |
| --- | --- | --- | --- |
| **Analog Value (AV)** | 10 | 1 - 10 | No-Units (95) |
| **Binary Value (BV)** | 10 | 1 - 10 | Inactive/Active |
| **Multi-State Value (MV)** | 10 | 1 - 10 | 3 States (1, 2, 3) |

---

## 📡 Network Requirements

For proper discovery and operation:

* **Protocol**: BACnet/IP
* **Port**: `47808` (UDP)
* **Network Mode**: The VM must be set to **Bridged Networking** in your hypervisor (VMware, VirtualBox, or KVM) to allow BACnet broadcast traffic to reach other devices on your subnet.

---

## 🔍 Troubleshooting

To view live server logs and see incoming write requests in real-time, run:

```bash
journalctl -u bacnet.service -f

```

To verify the service is running:

```bash
systemctl status bacnet.service

```

---

## ⚙️ Development Info

* **OS**: Debian 12 (Slim)
* **Language**: Python 3.11
* **Library**: BACpypes v0.18+
* **Service Name**: `bacnet.service` (Systemd)

```

```
