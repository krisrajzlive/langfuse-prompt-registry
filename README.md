# Prompt Registry

Manage LLM prompts in a self-hosted [Langfuse](https://langfuse.com) instance and serve them to
LangChain applications, with every trace linked to the exact prompt version that produced it.

## Capabilities

| Capability | Implementation |
|---|---|
| System and user prompts | Chat prompts defined in `prompts/*.yaml` and stored in Langfuse |
| Parameterization | `{{variable}}` placeholders compiled into a LangChain `ChatPromptTemplate` |
| Versioning | Every `publish` creates an immutable version |
| Release labels | `staging` / `production` labels select the served version; moving a label is a rollback |
| Model config | Temperature and max tokens stored with the prompt version |
| Tracing | Langfuse `CallbackHandler` on each chain run, with prompt-version linkage |

## Prerequisites

- A Langfuse project: [Langfuse Cloud](https://langfuse.com) (any region) or a self-hosted instance
- Python 3.11+ and [uv](https://docs.astral.sh/uv/)
- AWS credentials with Amazon Bedrock model access

## Setup

```bash
uv venv
uv pip install -e ".[dev]"
cp .env.example .env
```

Create the API keys in the Langfuse UI (**Project Settings → API Keys → Create new API key**) and
set `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` in `.env`, along with `LANGFUSE_HOST` for your
region (for example `https://jp.cloud.langfuse.com`). `.env` is git-ignored; never commit it.

## Usage

```bash
uv run prompt-registry check
uv run prompt-registry publish prompts/support_reply.yaml
uv run prompt-registry promote support-reply 1 production
uv run prompt-registry run support-reply --label production \
  --vars '{"company":"Acme","tone":"friendly","max_sentences":3,"customer_name":"Priya","product":"Router X","issue":"Wi-Fi drops hourly"}'
```

Release flow: edit the YAML, `publish` (new version, labelled `staging`), validate, then
`promote <name> <version> production`. Roll back by promoting the previous version.

## Tests

```bash
uv run pytest
```
