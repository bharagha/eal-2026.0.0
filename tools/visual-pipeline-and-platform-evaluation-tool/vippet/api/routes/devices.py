from typing import List
from fastapi import APIRouter

import api_schemas as schemas
from device import DeviceDiscovery

router = APIRouter()

@router.get("", response_model=List[schemas.Device])
def get_devices():
    device_discovery = DeviceDiscovery()
    device_list = device_discovery.list_devices()
    return [
        schemas.Device(
            device_name=device.device_name,
            full_device_name=device.full_device_name,
            device_type=device.device_type.name
            if hasattr(device.device_type, "name")
            else str(device.device_type),
            device_family=device.device_family.name
            if hasattr(device.device_family, "name")
            else str(device.device_family),
            gpu_id=getattr(device, "gpu_id", None),
        )
        for device in device_list
    ]
