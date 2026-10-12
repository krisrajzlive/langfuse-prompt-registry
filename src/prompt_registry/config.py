import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_host: str
    aws_region: str
    bedrock_model_id: str

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        missing = [k for k in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY") if not os.getenv(k)]
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
        return cls(
            langfuse_public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            langfuse_secret_key=os.environ["LANGFUSE_SECRET_KEY"],
            langfuse_host=os.getenv("LANGFUSE_HOST", "http://localhost:3001"),
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            bedrock_model_id=os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0"),
        )
