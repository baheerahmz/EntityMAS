"""Local LLM communication, structured schemas, and mock responses."""

import json #import JSON module
import os #import operating system module
from typing import Dict, Any #import typing tools

from openai import OpenAI #import OpenAI client
from openai import ( #import API error types
    APITimeoutError, #import timeout error
    APIConnectionError #import connection error
)

from config import ( #import configuration settings
    MOCK_MODE, #import mock mode setting
    MODEL_NAME, #import model name
    BASE_URL, #import LLM server URL
    TIMEOUT_SECONDS, #import timeout setting
    MAX_RETRIES #import retry setting
)


#==========================================
#LM STUDIO CLIENT
#==========================================

client = OpenAI( #create the OpenAI client
    api_key=os.getenv( #get the API key
        "OPENAI_API_KEY", #look for the API key
        "lm-studio" #use LM Studio as default
    ),
    base_url=BASE_URL, #set the local LLM URL
    timeout=TIMEOUT_SECONDS, #set the request timeout
    max_retries=MAX_RETRIES #set the maximum retries
)


#==========================================
#JSON SCHEMAS FOR EACH AGENT
#==========================================

AUDIO_SCHEMA = { #define the Audio Agent output format
    "type": "object", #set the response type
    "properties": { #define the response fields
        "risk_level": { #define the risk level field
            "type": "string", #set the field type
            "enum": ["LOW", "MEDIUM", "HIGH"] #set allowed risk levels
        },
        "confidence_score": { #define the confidence field
            "type": "number" #set the field as a number
        },
        "indicators": { #define the indicators field
            "type": "array", #set the field as a list
            "items": { #define the list item type
                "type": "string" #set each item as text
            }
        },
        "analysis_result": { #define the analysis field
            "type": "string" #set the field as text
        },
        "next_step": { #define the next step field
            "type": "string" #set the field as text
        }
    },
    "required": [ #define required fields
        "risk_level", #require risk level
        "confidence_score", #require confidence score
        "indicators", #require indicators
        "analysis_result", #require analysis result
        "next_step" #require next step
    ],
    "additionalProperties": False #do not allow extra fields
}


VIDEO_SCHEMA = { #define the Video Agent output format
    "type": "object", #set the response type
    "properties": { #define the response fields
        "risk_level": { #define the risk level field
            "type": "string", #set the field type
            "enum": ["LOW", "MEDIUM", "HIGH"] #set allowed risk levels
        },
        "confidence_score": { #define the confidence field
            "type": "number" #set the field as a number
        },
        "indicators": { #define the indicators field
            "type": "array", #set the field as a list
            "items": { #define the list item type
                "type": "string" #set each item as text
            }
        },
        "analysis_result": { #define the analysis field
            "type": "string" #set the field as text
        },
        "next_step": { #define the next step field
            "type": "string" #set the field as text
        }
    },
    "required": [ #define required fields
        "risk_level", #require risk level
        "confidence_score", #require confidence score
        "indicators", #require indicators
        "analysis_result", #require analysis result
        "next_step" #require next step
    ],
    "additionalProperties": False #do not allow extra fields
}


NETWORK_SCHEMA = { #define the Network Agent output format
    "type": "object", #set the response type
    "properties": { #define the response fields
        "risk_level": { #define the risk level field
            "type": "string", #set the field type
            "enum": ["LOW", "MEDIUM", "HIGH"] #set allowed risk levels
        },
        "threat_score": { #define the threat score field
            "type": "integer" #set the score as an integer
        },
        "attack_vector": { #define the attack vector field
            "type": "string" #set the field as text
        },
        "indicators": { #define the indicators field
            "type": "array", #set the field as a list
            "items": { #define the list item type
                "type": "string" #set each item as text
            }
        },
        "recommended_actions": { #define the recommended actions field
            "type": "array", #set the field as a list
            "items": { #define the list item type
                "type": "string" #set each item as text
            }
        },
        "next_step": { #define the next step field
            "type": "string" #set the field as text
        }
    },
    "required": [ #define required fields
        "risk_level", #require risk level
        "threat_score", #require threat score
        "attack_vector", #require attack vector
        "indicators", #require indicators
        "recommended_actions", #require recommended actions
        "next_step" #require next step
    ],
    "additionalProperties": False #do not allow extra fields
}


STRATEGY_SCHEMA = { #define the Strategy Agent output format
    "type": "object", #set the response type
    "properties": { #define the response fields
        "attack_objective": { #define the attack objective field
            "type": "string" #set the field as text
        },
        "likely_next_move": { #define the next move field
            "type": "string" #set the field as text
        },
        "overall_risk": { #define the overall risk field
            "type": "string", #set the field type
            "enum": [ #set allowed risk levels
                "LOW",
                "MEDIUM",
                "HIGH",
                "CRITICAL"
            ]
        },
        "strategy": { #define the strategy field
            "type": "array", #set the field as a list
            "items": { #define the list item type
                "type": "string" #set each item as text
            }
        },
        "confidence_score": { #define the confidence field
            "type": "number" #set the field as a number
        },
        "next_step": { #define the next step field
            "type": "string" #set the field as text
        }
    },
    "required": [ #define required fields
        "attack_objective", #require attack objective
        "likely_next_move", #require likely next move
        "overall_risk", #require overall risk
        "strategy", #require strategy
        "confidence_score", #require confidence score
        "next_step" #require next step
    ],
    "additionalProperties": False #do not allow extra fields
}


EVALUATOR_SCHEMA = { #define the Evaluator Agent output format
    "type": "object", #set the response type
    "properties": { #define the response fields
        "status": { #define the evaluation status
            "type": "string", #set the field type
            "enum": [ #set allowed evaluation results
                "PASS",
                "PARTIAL"
            ]
        },
        "coverage_score": { #define the coverage score
            "type": "number" #set the field as a number
        },
        "risk_warning": { #define the warning field
            "type": "string" #set the field as text
        },
        "final_summary": { #define the summary field
            "type": "string" #set the field as text
        }
    },
    "required": [ #define required fields
        "status", #require status
        "coverage_score", #require coverage score
        "risk_warning", #require risk warning
        "final_summary" #require final summary
    ],
    "additionalProperties": False #do not allow extra fields
}


#==========================================
#CHOOSE SCHEMA
#==========================================

def get_schema(agent_type: str) -> Dict[str, Any]:
    """
    Return the correct JSON schema for the
    requested agent.

    Args:
        agent_type: Name of the agent.

    Returns:
        JSON schema dictionary.
    """

    schemas = { #create a dictionary for all schemas
        "audio": AUDIO_SCHEMA, #connect audio to its schema
        "video": VIDEO_SCHEMA, #connect video to its schema
        "network": NETWORK_SCHEMA, #connect network to its schema
        "strategy": STRATEGY_SCHEMA, #connect strategy to its schema
        "evaluator": EVALUATOR_SCHEMA #connect evaluator to its schema
    }

    return schemas.get( #get the schema for the agent
        agent_type, #use the requested agent type
        {
            "type": "object" #use a basic object if not found
        }
    )


#==========================================
#JSON PARSER
#==========================================

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

    try: #try to convert the response into JSON
        return json.loads( #parse the JSON response
            response_text #use the model response
        )

    except json.JSONDecodeError as error: #handle invalid JSON

        #Human modification:
        #Model output is explicitly validated because
        #malformed JSON must not crash the MAS.
        raise ValueError( #raise a controlled error
            "The local AI returned invalid JSON."
        ) from error


#==========================================
#REAL / LOCAL LLM CALL
#==========================================

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

    if MOCK_MODE: #check if mock mode is enabled
        return get_mock_response( #return a mock response
            agent_type #use the requested agent type
        )

    schema = get_schema( #get the correct schema
        agent_type #use the requested agent type
    )

    try: #try to call the local LLM

        response = client.chat.completions.create( #send request to the LLM
            model=MODEL_NAME, #use the selected model

            messages=[ #send system and user messages
                {
                    "role": "system", #set the message as system instructions
                    "content": system_prompt #provide the agent prompt
                },
                {
                    "role": "user", #set the message as user input
                    "content": user_input #provide the incident information
                }
            ],

            temperature=0.2, #set a low temperature for consistent results

            response_format={ #request structured JSON output
                "type": "json_schema", #use JSON schema format

                "json_schema": { #define the JSON schema settings
                    "name":
                        f"{agent_type}_response", #name the response schema

                    "strict": True, #require the model to follow the schema

                    "schema":
                        schema #use the selected agent schema
                }
            }
        )

        response_text = ( #get the model response text
            response #access the response
            .choices[0] #get the first response choice
            .message #get the message
            .content #get the message content
        )

        if not response_text: #check if the response is empty

            raise ValueError( #raise an error for empty response
                "The local AI returned an empty response."
            )

        return parse_json_response( #parse the model response
            response_text #send the response text to the parser
        )

    except APITimeoutError as error: #handle LLM timeout

        #Human modification:
        #Timeout is converted into a predictable error
        #that LangGraph can route to fallback.
        raise TimeoutError( #raise a controlled timeout error
            "The local AI request exceeded "
            "the allowed timeout."
        ) from error

    except APIConnectionError as error: #handle connection problems

        raise ConnectionError( #raise a controlled connection error
            "Unable to connect to LM Studio."
        ) from error


#==========================================
#MOCK RESPONSES
#==========================================

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

    if agent_type == "audio": #check if Audio Agent is requested

        return { #return a mock Audio result
            "risk_level": "HIGH", #set Audio risk level
            "confidence_score": 0.88, #set Audio confidence score
            "indicators": [ #list Audio indicators
                "suspicious audio message",
                "possible synthetic voice"
            ],
            "analysis_result": #provide Audio analysis
                "Possible synthetic voice and "
                "social-engineering attack.",
            "next_step": "continue" #continue to the next step
        }

    if agent_type == "video": #check if Video Agent is requested

        return { #return a mock Video result
            "risk_level": "HIGH", #set Video risk level
            "confidence_score": 0.90, #set Video confidence score
            "indicators": [ #list Video indicators
                "reported manipulated video footage",
                "possible synthetic media alteration"
            ],
            "analysis_result": #provide Video analysis
                "The video evidence contains suspicious "
                "manipulation indicators.",
            "next_step": "continue" #continue to the next step
        }

    if agent_type == "network": #check if Network Agent is requested

        return { #return a mock Network result
            "risk_level": "HIGH", #set Network risk level
            "threat_score": 80, #set Network threat score
            "attack_vector": #provide the possible attack vector
                "Possible unauthorized network intrusion",

            "indicators": [ #list Network indicators
                "network intrusion",
                "suspicious access activity"
            ],

            "recommended_actions": [ #list recommended actions
                "isolate affected systems",
                "preserve network logs",
                "disable suspicious accounts"
            ],

            "next_step": "continue" #continue to the next step
        }

    if agent_type == "strategy": #check if Strategy Agent is requested

        return { #return a mock Strategy result
            "attack_objective": #provide the possible attack objective
                "Use synthetic media and network "
                "intrusion to deceive personnel and "
                "gain unauthorized access.",

            "likely_next_move": #provide a possible next move
                "The attacker may attempt further "
                "privileged actions or additional "
                "social-engineering requests.",

            "overall_risk": #set the overall risk
                "CRITICAL",

            "strategy": [ #list defensive strategies
                "isolate affected systems",
                "disable suspicious privileged accounts",
                "preserve network logs and original media",
                "verify suspicious communications independently"
            ],

            "confidence_score": #set the confidence score
                0.90,

            "next_step": #set the next workflow step
                "evaluate"
        }

    if agent_type == "evaluator": #check if Evaluator Agent is requested

        return { #return a mock evaluation result
            "status": #set the evaluation status
                "PASS",

            "coverage_score": #set the coverage score
                0.95,

            "risk_warning": #provide a risk warning
                "Media authenticity should still "
                "be confirmed using dedicated "
                "forensic analysis.",

            "final_summary": #provide the final summary
                "The incident represents a coordinated "
                "multi-vector attack involving suspicious "
                "audio, manipulated video, and network intrusion."
        }

    return { #return a default response for unknown agents
        "risk_level": "LOW", #set the default risk level
        "confidence_score": 0.50, #set the default confidence score
        "indicators": [], #return an empty indicator list
        "analysis_result": #provide a default analysis
            "No result available.",
        "next_step": "continue" #continue to the next step
    }