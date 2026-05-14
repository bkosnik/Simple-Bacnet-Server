import json
import os
import logging
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
from bacpypes.object import AnalogValueObject, BinaryValueObject, MultiStateValueObject
from bacpypes.core import run
from bacpypes.primitivedata import Real, Integer, CharacterString, Enumerated

# --- 1. SILENCE THE LOGS ---
# This stops the internal stack from dumping tracebacks to stderr
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger("bacpypes").setLevel(logging.CRITICAL)

# --- 2. CONFIGURATION ---
DEFAULT_CONFIG = {
    "device_id": 10123,
    "port": 47808,
    "av_count": 10,
    "bv_count": 10,
    "mv_count": 10,
    "object_name": "Simple-Point-Server-01"
}

def load_config():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists("/app/config.json"):
        try:
            with open("/app/config.json", 'r') as f:
                user_config = json.load(f)
                config.update({k: v for k, v in user_config.items() if k in config})
        except: pass
    return config

cfg = load_config()

# 3. DEVICE & APP SETUP
this_device = LocalDeviceObject(
    objectName=cfg["object_name"],
    objectIdentifier=cfg["device_id"],
    vendorIdentifier=15,
)
app = BIPSimpleApplication(this_device, f"0.0.0.0:{cfg['port']}")

# 4. POINT GENERATION
def add_points(count, obj_class, type_str):
    for i in range(1, count + 1):
        # Plain Python defaults
        if type_str == "analogValue":
            p_val, p_type = 0.0, Real
            extra = {"units": 95}
        elif type_str == "binaryValue":
            p_val, p_type = 0, Enumerated # 0=inactive
            extra = {}
        else: # multiStateValue
            p_val, p_type = 1, Integer
            extra = {"numberOfStates": 3}

        # Create object with plain strings for internal mapping
        obj = obj_class(
            objectIdentifier=(type_str, i),
            objectName=f"{type_str.upper()[:2]}-{i}",
            description=f"Simulated {type_str} {i}",
            presentValue=p_val,
            statusFlags=[0,0,0,0],
            outOfService=False,
            **extra
        )

        # OVERRIDE: Tell the property exactly what its network type is
        # This prevents the 'invalid constructor' error during reads/writes
        obj._properties['presentValue'].datatype = p_type
        obj._properties['presentValue'].mutable = True
        
        obj._properties['objectName'].datatype = CharacterString
        obj._properties['objectName'].mutable = True
        
        obj._properties['description'].datatype = CharacterString
        obj._properties['description'].mutable = True

        if type_str == "analogValue":
            obj._properties['units'].datatype = Enumerated
            obj._properties['units'].mutable = True
            
        app.add_object(obj)

# 5. RUN
add_points(cfg["av_count"], AnalogValueObject, "analogValue")
add_points(cfg["bv_count"], BinaryValueObject, "binaryValue")
add_points(cfg["mv_count"], MultiStateValueObject, "multiStateValue")

if __name__ == "__main__":
    print(f"BACnet Server Initialized: ID {cfg['device_id']} Port {cfg['port']}")
    run()
