from pydantic import BaseModel
from typing import Optional

class MachineStatusBreakdown(BaseModel):
    normal :int
    surveillance: int
    maintenance: int
    critique: int


class GlobalKPIs(BaseModel):
    total_machines: int
    machines_by_alert_level: MachineStatusBreakdown
    active_alerts_count: int
    alerts_by_level: MachineStatusBreakdown
    mttr_hours: Optional[float]
    availability_rate: float