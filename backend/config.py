from dataclasses import dataclass
import math
import os
from pathlib import Path
from urllib.parse import urlparse

from patterns.tool_selection import DEFAULT_MODEL


@dataclass(frozen=True)
class Settings:
    decider_url: str = ""
    decider_model: str = DEFAULT_MODEL
    bedrock_model_id: str = ""
    aws_region: str = "ap-south-1"
    confidence_threshold: float = 0.8
    provider_timeout_seconds: float = 30
    credentials_configured: bool = False

    def __post_init__(self):
        if not math.isfinite(self.confidence_threshold) or not 0 <= self.confidence_threshold <= 1:
            raise ValueError("DECIDER_CONFIDENCE_THRESHOLD must be between 0 and 1.")
        if not math.isfinite(self.provider_timeout_seconds) or not 1 <= self.provider_timeout_seconds <= 60:
            raise ValueError("PROVIDER_TIMEOUT_SECONDS must be between 1 and 60.")
        if self.decider_url:
            parsed = urlparse(self.decider_url)
            if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
                raise ValueError("STRANDS_DECIDER_URL must be an HTTP(S) base URL without credentials, query or fragment.")

    @classmethod
    def from_env(cls):
        credentials = bool(
            os.getenv("AWS_BEARER_TOKEN_BEDROCK", "").strip()
            or (os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))
            or os.getenv("AWS_PROFILE")
            or os.getenv("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI")
            or os.getenv("AWS_CONTAINER_CREDENTIALS_FULL_URI")
            or (os.getenv("AWS_WEB_IDENTITY_TOKEN_FILE") and os.getenv("AWS_ROLE_ARN"))
            or os.getenv("AWS_USE_INSTANCE_ROLE", "").lower() == "true"
            or Path(os.getenv("AWS_SHARED_CREDENTIALS_FILE", str(Path.home() / ".aws" / "credentials"))).is_file()
        )
        return cls(
            decider_url=os.getenv("STRANDS_DECIDER_URL", "").strip(),
            decider_model=os.getenv("STRANDS_DECIDER_MODEL", DEFAULT_MODEL),
            bedrock_model_id=os.getenv("BEDROCK_MODEL_ID", "").strip(),
            aws_region=os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "ap-south-1")),
            confidence_threshold=float(os.getenv("DECIDER_CONFIDENCE_THRESHOLD", "0.8")),
            provider_timeout_seconds=float(os.getenv("PROVIDER_TIMEOUT_SECONDS", "30")),
            credentials_configured=credentials,
        )

    def missing(self):
        missing = []
        if not self.decider_url: missing.append("STRANDS_DECIDER_URL")
        if not self.bedrock_model_id: missing.append("BEDROCK_MODEL_ID")
        if not self.credentials_configured: missing.append("AWS credentials or role configuration")
        return missing
