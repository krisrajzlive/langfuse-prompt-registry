"""Build LangChain runnables from prompts managed in Langfuse."""
from langchain_aws import ChatBedrockConverse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langfuse.langchain import CallbackHandler

from .config import Settings


def to_langchain_prompt(managed_prompt) -> ChatPromptTemplate:
    """Convert {{var}} placeholders to LangChain {var} templates and keep the version link."""
    template = ChatPromptTemplate.from_messages(managed_prompt.get_langchain_prompt())
    template.metadata = {"langfuse_prompt": managed_prompt}  # links traces to this version
    return template


def build_chain(managed_prompt, settings: Settings):
    cfg = managed_prompt.config or {}
    llm = ChatBedrockConverse(
        model=settings.bedrock_model_id,
        region_name=settings.aws_region,
        temperature=cfg.get("temperature", 0.0),
        max_tokens=cfg.get("max_tokens", 512),
    )
    return to_langchain_prompt(managed_prompt) | llm | StrOutputParser()


def run(managed_prompt, variables: dict, settings: Settings, **trace_metadata) -> str:
    chain = build_chain(managed_prompt, settings)
    return chain.invoke(
        variables,
        config={"callbacks": [CallbackHandler()], "metadata": trace_metadata},
    )
