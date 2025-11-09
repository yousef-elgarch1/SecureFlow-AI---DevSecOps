"""
User Profile Model for Adaptive Policy Generation
Stores user expertise level, role, certifications, and preferences
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ExpertiseLevel(str, Enum):
    """User's security knowledge level"""
    BEGINNER = "beginner"          # Junior developers, new to security
    INTERMEDIATE = "intermediate"  # Senior developers, basic security knowledge
    ADVANCED = "advanced"          # Security engineers, compliance experts


class UserRole(str, Enum):
    """User's professional role"""
    JUNIOR_DEVELOPER = "junior_developer"
    SENIOR_DEVELOPER = "senior_developer"
    SECURITY_ENGINEER = "security_engineer"
    DEVOPS_ENGINEER = "devops_engineer"
    COMPLIANCE_OFFICER = "compliance_officer"
    MANAGER = "manager"
    CISO = "ciso"


class Certification(BaseModel):
    """Professional security certification"""
    name: str = Field(..., description="Certification name (e.g., CISSP, CEH, Security+)")
    issuer: str = Field(..., description="Issuing organization (e.g., ISC2, EC-Council, CompTIA)")
    obtained_date: Optional[str] = Field(None, description="Date obtained (YYYY-MM-DD)")
    expiry_date: Optional[str] = Field(None, description="Expiration date (YYYY-MM-DD)")
    is_active: bool = Field(True, description="Whether certification is currently valid")


class UserProfile(BaseModel):
    """
    Complete user profile for adaptive policy generation
    """
    # Basic Info
    user_id: Optional[str] = Field(None, description="Unique user identifier")
    name: Optional[str] = Field(None, description="User's full name")
    email: Optional[str] = Field(None, description="User's email address")

    # Expertise & Role
    expertise_level: ExpertiseLevel = Field(
        ExpertiseLevel.INTERMEDIATE,
        description="User's security knowledge level"
    )
    role: UserRole = Field(
        UserRole.SENIOR_DEVELOPER,
        description="User's professional role"
    )

    # Experience
    years_of_experience: Optional[int] = Field(
        None,
        description="Years of professional experience in tech/security"
    )
    security_experience_years: Optional[int] = Field(
        None,
        description="Years specifically in security roles"
    )

    # Certifications
    certifications: List[Certification] = Field(
        default_factory=list,
        description="List of professional security certifications"
    )

    # Preferences
    preferred_detail_level: str = Field(
        "medium",
        description="Preferred level of detail (low, medium, high)"
    )
    include_code_examples: bool = Field(
        True,
        description="Whether to include code examples in policies"
    )
    include_compliance_details: bool = Field(
        True,
        description="Whether to include detailed compliance mappings"
    )
    focus_areas: List[str] = Field(
        default_factory=list,
        description="Specific security focus areas (e.g., 'web security', 'cloud security')"
    )

    # Metadata
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Profile creation timestamp"
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Last profile update timestamp"
    )

    class Config:
        use_enum_values = True

    @classmethod
    def default(cls) -> "UserProfile":
        """Create a default profile for intermediate users"""
        return cls(
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            role=UserRole.SENIOR_DEVELOPER,
            include_code_examples=True,
            include_compliance_details=True
        )

    @classmethod
    def beginner_profile(cls) -> "UserProfile":
        """Create profile for beginners - maximum detail and learning resources"""
        return cls(
            expertise_level=ExpertiseLevel.BEGINNER,
            role=UserRole.JUNIOR_DEVELOPER,
            preferred_detail_level="high",
            include_code_examples=True,
            include_compliance_details=False  # Don't overwhelm beginners
        )

    @classmethod
    def advanced_profile(cls) -> "UserProfile":
        """Create profile for security experts - compliance-heavy, technical depth"""
        return cls(
            expertise_level=ExpertiseLevel.ADVANCED,
            role=UserRole.SECURITY_ENGINEER,
            preferred_detail_level="high",
            include_code_examples=True,
            include_compliance_details=True
        )

    def get_active_certifications(self) -> List[Certification]:
        """Get only currently active certifications"""
        return [cert for cert in self.certifications if cert.is_active]

    def has_certification(self, cert_name: str) -> bool:
        """Check if user has a specific certification"""
        return any(
            cert.name.lower() == cert_name.lower() and cert.is_active
            for cert in self.certifications
        )

    def get_expertise_description(self) -> str:
        """Get human-readable expertise description"""
        descriptions = {
            ExpertiseLevel.BEGINNER: "New to security - needs detailed guidance and learning resources",
            ExpertiseLevel.INTERMEDIATE: "Has security basics - can implement technical solutions",
            ExpertiseLevel.ADVANCED: "Security expert - needs compliance details and advanced strategies"
        }
        return descriptions.get(self.expertise_level, "Unknown")

    def get_role_description(self) -> str:
        """Get human-readable role description"""
        descriptions = {
            UserRole.JUNIOR_DEVELOPER: "Junior Developer - Learning security best practices",
            UserRole.SENIOR_DEVELOPER: "Senior Developer - Implementing security solutions",
            UserRole.SECURITY_ENGINEER: "Security Engineer - Designing security architectures",
            UserRole.DEVOPS_ENGINEER: "DevOps Engineer - Securing CI/CD pipelines",
            UserRole.COMPLIANCE_OFFICER: "Compliance Officer - Ensuring regulatory adherence",
            UserRole.MANAGER: "Manager - Overseeing security initiatives",
            UserRole.CISO: "CISO - Strategic security leadership"
        }
        return descriptions.get(self.role, "Unknown")

    def to_prompt_context(self) -> str:
        """
        Generate context string for LLM prompts
        This tells the LLM who they're writing policies for
        """
        context = f"Target Audience: {self.get_role_description()}\n"
        context += f"Expertise Level: {self.get_expertise_description()}\n"

        if self.certifications:
            active_certs = self.get_active_certifications()
            if active_certs:
                cert_names = ", ".join([cert.name for cert in active_certs])
                context += f"Certifications: {cert_names}\n"

        if self.years_of_experience:
            context += f"Experience: {self.years_of_experience} years in tech"
            if self.security_experience_years:
                context += f", {self.security_experience_years} years in security"
            context += "\n"

        if self.focus_areas:
            context += f"Focus Areas: {', '.join(self.focus_areas)}\n"

        return context


# Predefined profile templates for quick selection
PROFILE_TEMPLATES = {
    "beginner": UserProfile.beginner_profile(),
    "intermediate": UserProfile.default(),
    "advanced": UserProfile.advanced_profile(),
    "junior_dev": UserProfile(
        expertise_level=ExpertiseLevel.BEGINNER,
        role=UserRole.JUNIOR_DEVELOPER,
        preferred_detail_level="high",
        include_code_examples=True
    ),
    "senior_dev": UserProfile(
        expertise_level=ExpertiseLevel.INTERMEDIATE,
        role=UserRole.SENIOR_DEVELOPER,
        preferred_detail_level="medium",
        include_code_examples=True
    ),
    "security_eng": UserProfile(
        expertise_level=ExpertiseLevel.ADVANCED,
        role=UserRole.SECURITY_ENGINEER,
        preferred_detail_level="high",
        include_compliance_details=True
    ),
    "devops": UserProfile(
        expertise_level=ExpertiseLevel.INTERMEDIATE,
        role=UserRole.DEVOPS_ENGINEER,
        preferred_detail_level="medium",
        include_code_examples=True,
        focus_areas=["CI/CD security", "infrastructure security"]
    ),
    "compliance": UserProfile(
        expertise_level=ExpertiseLevel.ADVANCED,
        role=UserRole.COMPLIANCE_OFFICER,
        preferred_detail_level="high",
        include_compliance_details=True,
        include_code_examples=False  # Compliance officers care more about frameworks than code
    ),
    "manager": UserProfile(
        expertise_level=ExpertiseLevel.INTERMEDIATE,
        role=UserRole.MANAGER,
        preferred_detail_level="low",
        include_code_examples=False,
        include_compliance_details=True
    )
}


def get_profile_template(template_name: str) -> UserProfile:
    """Get a predefined profile template by name"""
    return PROFILE_TEMPLATES.get(template_name, UserProfile.default())
