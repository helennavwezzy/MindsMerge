import enum
import warnings
from typing import Any, Literal

from google.adk.auth.auth_tool import AuthConfig
from google.adk.events import Event
from google.adk.models import BaseLlm, Gemini
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from pydantic import BaseModel

from libs.custom_logger import getLogger
from libs.miscs import crunch

_logger = getLogger(__name__)

# ignore all warnings
warnings.filterwarnings("ignore")


_retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=4,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

llm_models: dict[
    Literal[
        "gemini-3-pro",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gpt-5.1",
        "gpt-5-mini",
        "gpt-5-nano",
    ],
    BaseLlm,
] = {
    "gemini-3-pro": Gemini(model="gemini-3-pro-preview", retry_options=_retry_config),
    "gemini-2.5-pro": Gemini(model="gemini-2.5-pro", retry_options=_retry_config),
    "gemini-2.5-flash": Gemini(model="gemini-2.5-flash", retry_options=_retry_config),
    "gpt-5.1": LiteLlm(model="openai/gpt-5.1"),
    "gpt-5-mini": LiteLlm(model="openai/gpt-5-mini"),
    "gpt-5-nano": LiteLlm(model="openai/gpt-5-nano"),
}


class LongRunningRequestType(enum.StrEnum):
    CRED = "adk_request_credential"
    CONF = "adk_request_confirmation"


class EventCleanData(BaseModel):
    text: list[str] = []
    request: list[tuple[LongRunningRequestType, types.FunctionCall]] = []


def handle_adk_event(event: Event) -> EventCleanData:
    """Handle the event streamed by a Runner.

    The result data contains:
    - text: List of text parts from the event.
    - request: List of tuples (LongRunningRequestEnum, FunctionCall)
    corresponding to long-running tool requests.
    """

    result = EventCleanData()

    # If the event has no content
    if not event.content or not event.content.parts:
        return result

    for part in event.content.parts:
        if part.text:
            if event.content.role == "user":
                crunch("🧑 User:", part.text.strip())
            else:
                text = part.text.strip()
                result.text.append(text)
                crunch(f"🤖 Agent [[{event.author}]]:", text)

        elif part.function_call:
            crunch(
                f"⚙️ Function call ({part.function_call.name}):", part.function_call.args
            )
            if (
                event.long_running_tool_ids
                and part.function_call.id in event.long_running_tool_ids
            ):
                try:
                    req = LongRunningRequestType(part.function_call.name)
                except ValueError:
                    _logger.error(
                        "Unexpected long running function: %s", part.function_call.name
                    )
                    raise

                result.request.append((req, part.function_call))

        elif part.function_response:
            crunch(
                f"📬 Function resp ({part.function_response.name}):",
                part.function_response.response,
            )

        else:
            crunch("❓ Unknown part in event:", part)

    return result


def get_auth_config(func_call: types.FunctionCall) -> AuthConfig:
    # Extracts the AuthConfig object from the arguments of the auth request function call
    if not func_call.args or not (auth_config := func_call.args.get("authConfig")):
        raise ValueError(f"Cannot get auth config from function call: {func_call}")
    if isinstance(auth_config, dict):
        auth_config = AuthConfig.model_validate(auth_config)
    assert isinstance(auth_config, AuthConfig)
    return auth_config


def make_func_response(*, func_call: types.FunctionCall, response: dict[str, Any]):
    """Make response content for a FunctionCall."""

    return types.Content(
        role="user",
        parts=[
            types.Part(
                function_response=types.FunctionResponse(
                    id=func_call.id,
                    name=func_call.name,
                    response=response,
                )
            )
        ],
    )
