"""Local LLM communication, structured schemas, and mock responses."""

import json
import os
from typing import Dict, Any

from openai import OpenAI
from openai import (
    APITimeoutError,
    APIConnectionError
)

from config import (
    MOCK_MODE,
    MODEL_NAME,
    BASE_URL,
    TIMEOUT_SECONDS,
    MAX_RETRIES
)


# ==========================================
# LM STUDIO CLIENT
# ==========================================

client = OpenAI(
    api_key=os.getenv(
        "OPENAI_API_KEY",
        "lm-studio"
    ),
    base_url=BASE_URL,
    timeout=TIMEOUT_SECONDS,
    max_retries=MAX_RETRIES
)


# ==========================================
# JSON SCHEMAS FOR EACH AGENT
# ==========================================

AUDIO_SCHEMA = {
    "type": "object",
    "properties": {
        "risk_level": {
            "type": "string",
            "enum": ["LOW", "MEDIUM", "HIGH"]
        },
        "confidence_score": {
            "type": "number"
        },
        "indicators": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "analysis_result": {
            "type": "string"
        },
        "next_step": {
            "type": "string"
        }
    },
    "required": [
        "risk_level",
        "confidence_score",
        "indicators",
        "analysis_result",
        "next_step"
    ],
    "additionalProperties": False
}


VIDEO_SCHEMA = {
    "type": "object",
    "properties": {
        "risk_level": {
            "type": "string",
            "enum": ["LOW", "MEDIUM", "HIGH"]
        },
        "confidence_score": {
            "type": "number"
        },
        "indicators": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "analysis_result": {
            "type": "string"
        },
        "next_step": {
            "type": "string"
        }
    },
    "required": [
        "risk_level",
        "confidence_score",
        "indicators",
        "analysis_result",
        "next_step"
    ],
    "additionalProperties": False
}


NETWORK_SCHEMA = {
    "type": "object",
    "properties": {
        "risk_level": {
            "type": "string",
            "enum": ["LOW", "MEDIUM", "HIGH"]
        },
        "threat_score": {
            "type": "integer"
        },
        "attack_vector": {
            "type": "string"
        },
        "indicators": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "recommended_actions": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "next_step": {
            "type": "string"
        }
    },
    "required": [
        "risk_level",
        "threat_score",
        "attack_vector",
        "indicators",
        "recommended_actions",
        "next_step"
    ],
    "additionalProperties": False
}


STRATEGY_SCHEMA = {
    "type": "object",
    "properties": {
        "attack_objective": {
            "type": "string"
        },
        "likely_next_move": {
            "type": "string"
        },
        "overall_risk": {
            "type": "string",
            "enum": [
                "LOW",
                "MEDIUM",
                "HIGH",
                "CRITICAL"
            ]
        },
        "strategy": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "confidence_score": {
            "type": "number"
        },
        "next_step": {
            "type": "string"
        }
    },
    "required": [
        "attack_objective",
        "likely_next_move",
        "overall_risk",
        "strategy",
        "confidence_score",
        "next_step"
    ],
    "additionalProperties": False
}


EVALUATOR_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": [
                "PASS",
                "PARTIAL"
            ]
        },
        "coverage_score": {
            "type": "number"
        },
        "risk_warning": {
            "type": "string"
        },
        "final_summary": {
            "type": "string"
        }
    },
    "required": [
        "status",
        "coverage_score",
        "risk_warning",
        "final_summary"
    ],
    "additionalProperties": False
}


# ==========================================
# CHOOSE SCHEMA
# ==========================================

def get_schema(agent_type: str) -> Dict[str, Any]:
    """
    Return the correct JSON schema for the
    requested agent.

    Args:
        agent_type: Name of the agent.

    Returns:
        JSON schema dictionary.
    """

    schemas = {
        "audio": AUDIO_SCHEMA,
        "video": VIDEO_SCHEMA,
        "network": NETWORK_SCHEMA,
        "strategy": STRATEGY_SCHEMA,
        "evaluator": EVALUATOR_SCHEMA
    }

    return schemas.get(
        agent_type,
        {
            "type": "object"
        }
    )


# ==========================================
# JSON PARSER
# ==========================================

def parse_json_response(
    response_text: str
) -> Dict[str, Any]:
    """
    Convert JSON text returned by the local LLM
    into a Python dictionary.

    Args:
        response_text: Raw model response.

    Returns:
        Parsed Python dictionary.

    Raises:
        ValueError: If the response is not valid JSON.
    """

    try:
        return json.loads(
            response_text
        )

    except json.JSONDecodeError as error:

        # Human modification:
        # Model output is explicitly validated because
        # malformed JSON must not crash the MAS.
        raise ValueError(
            "The local AI returned invalid JSON."
        ) from error


# ==========================================
# REAL / LOCAL LLM CALL
# ==========================================

def call_llm(
    system_prompt: str,
    user_input: str,
    agent_type: str
) -> Dict[str, Any]:
    """
    Send agent instructions and incident information
    to Qwen running locally through LM Studio.

    Args:
        system_prompt: Agent-specific system prompt.
        user_input: Incident information to analyse.
        agent_type: Name of the requesting agent.

    Returns:
        Structured dictionary generated by the LLM.

    Raises:
        TimeoutError: If the request exceeds the timeout.
        ConnectionError: If LM Studio cannot be reached.
        ValueError: If the model returns invalid JSON.
    """

    if MOCK_MODE:
        return get_mock_response(
            agent_type
        )

    schema = get_schema(
        agent_type
    )

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],

            temperature=0.2,

            response_format={
                "type": "json_schema",

                "json_schema": {
                    "name":
                        f"{agent_type}_response",

                    "strict": True,

                    "schema":
                        schema
                }
            }
        )

        response_text = (
            response
            .choices[0]
            .message
            .content
        )

        if not response_text:

            raise ValueError(
                "The local AI returned an empty response."
            )

        return parse_json_response(
            response_text
        )

    except APITimeoutError as error:

        # Human modification:
        # Timeout is converted into a predictable error
        # that LangGraph can route to fallback.
        raise TimeoutError(
            "The local AI request exceeded "
            "the allowed timeout."
        ) from error

    except APIConnectionError as error:

        raise ConnectionError(
            "Unable to connect to LM Studio."
        ) from error


# ==========================================
# MOCK RESPONSES
# ==========================================

def get_mock_response(
    agent_type: str
) -> Dict[str, Any]:
    """
    Return simulated responses when MOCK_MODE
    is enabled.

    Args:
        agent_type: Name of the requesting agent.

    Returns:
        Simulated structured response.
    """

    if agent_type == "audio":

        return {
            "risk_level": "HIGH",
            "confidence_score": 0.88,
            "indicators": [
                "suspicious audio message",
                "possible synthetic voice"
            ],
            "analysis_result":
                "Possible synthetic voice and "
                "social-engineering attack.",
            "next_step": "continue"
        }

    if agent_type == "video":

        return {
            "risk_level": "HIGH",
            "confidence_score": 0.90,
            "indicators": [
                "reported manipulated video footage",
                "possible synthetic media alteration"
            ],
            "analysis_result":
                "The video evidence contains suspicious "
                "manipulation indicators.",
            "next_step": "continue"
        }

    if agent_type == "network":

        return {
            "risk_level": "HIGH",
            "threat_score": 80,
            "attack_vector":
                "Possible unauthorized network intrusion",

            "indicators": [
                "network intrusion",
                "suspicious access activity"
            ],

            "recommended_actions": [
                "isolate affected systems",
                "preserve network logs",
                "disable suspicious accounts"
            ],

            "next_step": "continue"
        }

    if agent_type == "strategy":

        return {
            "attack_objective":
                "Use synthetic media and network "
                "intrusion to deceive personnel and "
                "gain unauthorized access.",

            "likely_next_move":
                "The attacker may attempt further "
                "privileged actions or additional "
                "social-engineering requests.",

            "overall_risk":
                "CRITICAL",

            "strategy": [
                "isolate affected systems",
                "disable suspicious privileged accounts",
                "preserve network logs and original media",
                "verify suspicious communications independently"
            ],

            "confidence_score":
                0.90,

            "next_step":
                "evaluate"
        }

    if agent_type == "evaluator":

        return {
            "status":
                "PASS",

            "coverage_score":
                0.95,

            "risk_warning":
                "Media authenticity should still "
                "be confirmed using dedicated "
                "forensic analysis.",

            "final_summary":
                "The incident represents a coordinated "
                "multi-vector attack involving suspicious "
                "audio, manipulated video, and network intrusion."
        }

    return {
        "risk_level": "LOW",
        "confidence_score": 0.50,
        "indicators": [],
        "analysis_result":
            "No result available.",
        "next_step": "continue"
    }