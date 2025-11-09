"""
Policy Status Tracking Models
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PolicyStatus(str, Enum):
    """Policy implementation status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    FIXED = "fixed"
    VERIFIED = "verified"
    REOPENED = "reopened"


class TimelineEvent(BaseModel):
    """Event in policy timeline"""
    event_type: str = Field(..., description="Type of event (created, assigned, status_changed)")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    user: Optional[str] = Field(None, description="User who triggered the event")
    from_status: Optional[str] = Field(None)
    to_status: Optional[str] = Field(None)
    details: Optional[str] = Field(None)


class PolicyTrackingItem(BaseModel):
    """Individual policy tracking item"""
    policy_id: str = Field(..., description="Unique policy identifier")
    vulnerability_title: str
    vulnerability_type: str = Field(..., description="sast, sca, or dast")
    severity: str
    status: PolicyStatus = Field(default=PolicyStatus.NOT_STARTED)
    assigned_to: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    due_date: Optional[str] = None
    timeline: List[TimelineEvent] = Field(default_factory=list)
    nist_csf_controls: List[str] = Field(default_factory=list)
    iso27001_controls: List[str] = Field(default_factory=list)
    file_path: Optional[str] = None
    priority: Optional[str] = None

    class Config:
        use_enum_values = True


class PolicyTrackingStats(BaseModel):
    """Overall tracking statistics"""
    total_policies: int = 0
    not_started: int = 0
    in_progress: int = 0
    under_review: int = 0
    fixed: int = 0
    verified: int = 0
    reopened: int = 0
    compliance_percentage: float = 0.0
