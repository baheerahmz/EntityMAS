"""Tests for fallback routing and safe partial responses."""

import llm_client #import the LLM client

from fallback import create_fallback_response #import the fallback response function
from workflow import build_workflow #import the workflow builder


def enable_mock_mode(monkeypatch):
    """Enable predictable mock responses for workflow testing."""
    monkeypatch.setattr(
        llm_client, #access the LLM client
        "MOCK_MODE", #select the mock mode setting
        True #turn mock mode on
    )


def test_network_failure_activates_fallback(monkeypatch):
    """Route a simulated Network Agent failure to fallback."""
    enable_mock_mode(monkeypatch) #enable mock mode for testing

    app = build_workflow() #build the workflow

    initial_state = {
        "user_input": ( #enter the incident scenario
            "The Entity launched a coordinated attack "
            "involving a suspicious audio message, "
            "manipulated video footage, "
            "and a network intrusion."
        ),
        "errors": [], #start with no errors
        "simulate_failure": True #simulate a Network Agent failure
    }

    result = app.invoke(initial_state) #run the workflow with the test input

    fallback = result["fallback_result"] #get the fallback result

    assert fallback["status"] == "PARTIAL" #check that the status is partial

    assert fallback["risk_warning"] == ( #check the fallback warning
        "Fallback activated because a system component failed."
    )

    assert result["errors"] #check that an error was recorded

    assert "Network Agent failure" in result["errors"][0] #check for Network Agent failure
    assert "Simulated Network Agent failure" in result["errors"][0] #check for simulated failure message

    assert "Audio analysis completed." in fallback["available_results"] #check Audio result is available
    assert "Video analysis completed." in fallback["available_results"] #check Video result is available

    assert fallback["fallback_execution_time"] < 5 #check fallback finishes in less than 5 seconds

    #The workflow must stop before strategy and evaluation.
    assert result.get("strategy_result", {}) == {} #check Strategy Agent did not run
    assert result.get("evaluation_result", {}) == {} #check Evaluation Agent did not run


def test_fallback_preserves_available_result():
    """Report any successful specialist result during fallback."""
    fallback = create_fallback_response( #create a fallback response
        errors=[
            "Video Agent failure: simulated error." #add a Video Agent error
        ],
        audio_result={
            "risk_level": "MEDIUM" #provide the completed Audio result
        },
        video_result={}, #provide empty Video result because it failed
        network_result={} #provide empty Network result
    )

    assert fallback["status"] == "PARTIAL" #check that the status is partial
    assert fallback["errors"] #check that the error is recorded

    assert fallback["available_results"] == [ #check which result is available
        "Audio analysis completed."
    ]

    assert fallback["fallback_execution_time"] < 5 #check fallback finishes in less than 5 seconds


def test_fallback_handles_no_completed_agents():
    """Return a safe warning when every specialist is unavailable."""
    fallback = create_fallback_response( #create a fallback response
        errors=[
            "All specialist agents were unavailable." #record that all agents failed
        ],
        audio_result={}, #no Audio result is available
        video_result={}, #no Video result is available
        network_result={} #no Network result is available
    )

    assert fallback["status"] == "PARTIAL" #check that the status is partial

    assert fallback["available_results"] == [ #check that no analysis was completed
        "No specialist analysis was successfully completed."
    ]

    assert fallback["recommendation"] #check that a recommendation is provided
    assert fallback["fallback_execution_time"] < 5 #check fallback finishes in less than 5 seconds