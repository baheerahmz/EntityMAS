"""Integration tests for the complete LangGraph workflow."""

import llm_client #import the LLM client

from workflow import build_workflow #import the workflow builder


def enable_mock_mode(monkeypatch):
    """Enable predictable mock LLM responses during testing."""
    monkeypatch.setattr(
        llm_client, #access the LLM client
        "MOCK_MODE", #select the mock mode setting
        True #enable mock mode
    )


def test_complete_multivector_workflow(monkeypatch):
    """Execute all specialists for a combined incident."""
    enable_mock_mode(monkeypatch) #enable mock mode

    app = build_workflow() #build the workflow

    initial_state = {
        "user_input": ( #enter the combined incident
            "The Entity launched a coordinated attack "
            "involving a suspicious audio message, "
            "manipulated video footage, "
            "and a network intrusion."
        ),
        "errors": [], #start with no errors
        "simulate_failure": False #do not simulate a failure
    }

    result = app.invoke(initial_state) #run the workflow

    assert result["router_result"]["audio"] is True #check Audio Agent is selected
    assert result["router_result"]["video"] is True #check Video Agent is selected
    assert result["router_result"]["network"] is True #check Network Agent is selected

    assert result["audio_result"]["risk_level"] == "HIGH" #check Audio risk level
    assert result["video_result"]["risk_level"] == "HIGH" #check Video risk level
    assert result["network_result"]["risk_level"] == "HIGH" #check Network risk level

    assert result["overall_threat_score"] == 100 #check the overall threat score

    assert result["strategy_result"]["next_step"] == "evaluate" #check Strategy Agent moves to evaluation
    assert result["evaluation_result"]["status"] == "PASS" #check the evaluation passes

    assert result["errors"] == [] #check there are no errors


def test_audio_only_workflow(monkeypatch):
    """Execute only the Audio Agent for an audio incident."""
    enable_mock_mode(monkeypatch) #enable mock mode

    app = build_workflow() #build the workflow

    initial_state = {
        "user_input": ( #enter an audio-only incident
            "A suspicious audio message was received."
        ),
        "errors": [], #start with no errors
        "simulate_failure": False #do not simulate a failure
    }

    result = app.invoke(initial_state) #run the workflow

    assert result["router_result"]["audio"] is True #check Audio Agent is selected
    assert result["router_result"]["video"] is False #check Video Agent is not selected
    assert result["router_result"]["network"] is False #check Network Agent is not selected

    assert result["audio_result"]["risk_level"] == "HIGH" #check Audio risk level

    assert result.get("video_result", {}) == {} #check Video result is empty
    assert result.get("network_result", {}) == {} #check Network result is empty

    assert result["overall_threat_score"] == 30 #check the overall threat score

    #A score below 70 must skip the Strategic Agent.
    assert result.get("strategy_result", {}) == {} #check Strategy Agent is skipped

    assert result["evaluation_result"]["status"] == "PASS" #check the evaluation passes
    assert result["errors"] == [] #check there are no errors


def test_network_only_workflow(monkeypatch):
    """Execute only the Network Agent for a network incident."""
    enable_mock_mode(monkeypatch) #enable mock mode

    app = build_workflow() #build the workflow

    initial_state = {
        "user_input": ( #enter a network-only incident
            "A network intrusion was reported."
        ),
        "errors": [], #start with no errors
        "simulate_failure": False #do not simulate a failure
    }

    result = app.invoke(initial_state) #run the workflow

    assert result["router_result"]["audio"] is False #check Audio Agent is not selected
    assert result["router_result"]["video"] is False #check Video Agent is not selected
    assert result["router_result"]["network"] is True #check Network Agent is selected

    assert result.get("audio_result", {}) == {} #check Audio result is empty
    assert result.get("video_result", {}) == {} #check Video result is empty

    assert result["network_result"]["risk_level"] == "HIGH" #check Network risk level
    assert result["network_result"]["threat_score"] == 50 #check Network threat score

    assert result["overall_threat_score"] == 40 #check the overall threat score

    #A score below 70 must skip the Strategic Agent.
    assert result.get("strategy_result", {}) == {} #check Strategy Agent is skipped

    assert result["evaluation_result"]["status"] == "PASS" #check the evaluation passes
    assert result["errors"] == [] #check there are no errors