# Entity Multi-Agent System

## 1. Project Scenario

The Entity is suspected of launching a coordinated attack involving a suspicious audio message, manipulated video footage, and a network intrusion.

## 2. Project Objective

This project implements a Multi-Agent System (MAS) that analyses a coordinated multi-vector security incident using several specialised AI agents.

The system:

- identifies audio, video, and network threats;
- routes the incident to the relevant specialist agents;
- calculates an overall threat score;
- produces a defensive strategy for high-risk incidents;
- evaluates the completeness and quality of the analysis; and
- activates a fallback mechanism when a component fails.

## 3. Software Framework

The system uses **LangGraph** as its Multi-Agent System orchestration framework.

LangGraph manages:

- shared state;
- agent execution;
- workflow dependencies;
- conditional routing; and
- fallback routing.

The system uses **LM Studio** to run a local language model.

The selected model is:

```text
qwen/qwen3-4b-2507
```

The local LM Studio server runs at:

```text
http://127.0.0.1:1234/v1
```

## 4. System Architecture

The system follows a shared-state LangGraph workflow.

```text
Incident Input
      |
      v
    Router
      |
      v
Selected Specialist Agents
(Audio, Video and/or Network)
      |
      v
Overall Risk Calculation
      |
      v
Is Threat Score 70 or Higher?
      |
   +--+--+
   |     |
  Yes    No
   |     |
   v     |
Strategic|
 Agent   |
   |     |
   +--+--+
      |
      v
Self-Evaluation Agent
      |
      v
Final Result
```

If a component fails, the workflow redirects execution to the Fallback Node.

## 5. Routing Mechanism

The system uses **static, rule-based routing**.

The Router examines the incident description using predefined keywords associated with three threat categories:

- audio;
- video; and
- network.

Examples of audio keywords include:

```text
audio
voice
speech
recording
voicemail
deepfake audio
```

Examples of video keywords include:

```text
video
footage
deepfake video
manipulated video
lip-sync
frame
```

Examples of network keywords include:

```text
network
intrusion
login
admin
administrator
account
malware
phishing
password
```

The Router returns Boolean routing decisions together with an explanation of the activated agents.

Example:

```python
{
    "audio": True,
    "video": True,
    "network": True,
    "reason": (
        "Routing decision based on detected incident indicators. "
        "Activated: Audio Agent, Video Agent, Network Agent."
    )
}
```

LangGraph conditional edges use the routing result to determine which specialist agents should execute.

For example:

```text
Audio incident        → Audio Agent
Video incident        → Video Agent
Network incident      → Network Agent
Combined incident     → Multiple specialist agents
```

A second conditional decision occurs after the overall risk score is calculated:

```text
Threat score ≥ 70     → Strategic Agent
Threat score < 70     → Self-Evaluation Agent
System error          → Fallback Node
```

## 6. Agent Roles

### 6.1 Router

The Router receives the original incident description, detects relevant threat indicators, and determines which specialist agents should be activated.

### 6.2 Audio Deepfake Analysis Agent

The Audio Agent analyses only the supplied audio-related evidence.

Its responsibilities are:

- identify audio-related indicators;
- assess the possible audio risk;
- acknowledge insufficient acoustic evidence;
- avoid analysing video or network information; and
- return structured JSON output.

### 6.3 Video Manipulation Analysis Agent

The Video Agent analyses only the supplied video-related evidence.

Its responsibilities are:

- identify reported video-manipulation indicators;
- assess the possible video risk;
- acknowledge when forensic visual evidence is insufficient;
- avoid analysing audio or network information; and
- return structured JSON output.

### 6.4 Network Intrusion Analysis Agent

The Network Agent analyses only network-security evidence.

Its responsibilities are:

- identify network indicators;
- use the deterministic network threat score;
- describe the possible attack vector;
- recommend defensive actions;
- avoid inventing unsupported network evidence; and
- return structured JSON output.

### 6.5 Overall Risk Agent

The Overall Risk Agent combines the available specialist results and calculates an overall threat score between 0 and 100.

The calculation considers:

- audio risk;
- video risk;
- network risk;
- deterministic network threat score; and
- the number of simultaneous active threats.

### 6.6 Strategic Response Agent

The Strategic Agent executes when the overall threat score is 70 or higher.

Its responsibilities are:

- identify a possible attack objective;
- predict a plausible next move;
- estimate the overall strategic risk;
- recommend defensive actions; and
- preserve uncertainty from the specialist findings.

### 6.7 Self-Evaluation Agent

The Self-Evaluation Agent compares:

- the original incident;
- the Router decision;
- the Audio Agent result;
- the Video Agent result;
- the Network Agent result; and
- the Strategic Agent result.

It checks whether every Router-selected threat category was addressed and whether unsupported evidence was introduced.

### 6.8 Fallback Node

The Fallback Node produces a safe partial response when a component fails.

It returns:

- a partial status;
- a risk warning;
- recorded errors;
- available completed results;
- recommended actions; and
- fallback execution time.

## 7. Custom Tools

The project contains three custom Python tools in `tools.py`.

### 7.1 `extract_incident_indicators()`

This tool detects audio, video, and network indicators from the original incident description.

It provides:

- category-detection Boolean values;
- detected keywords; and
- category-specific evidence descriptions.

### 7.2 `calculate_network_threat_score()`

This tool calculates a deterministic network threat score using weighted security indicators.

Each detected network indicator contributes a predefined weight to the score. Duplicate indicators are counted only once.

The final network score is limited to a maximum of 100.

### 7.3 `calculate_overall_risk()`

This tool combines the specialist-agent results and calculates an overall multi-vector risk score between 0 and 100.

The calculation uses specialist risk levels, part of the deterministic network threat score, and an additional coordination penalty when multiple threat categories are simultaneously active.

## 8. Prompt Design

Each LLM-based agent has its own specialised system prompt.

The prompts:

- define the agent's persona and role;
- limit the agent to its assigned threat domain;
- prevent unsupported evidence from being invented;
- preserve uncertainty;
- require strict JSON output; and
- specify the next workflow step where applicable.

The Audio Agent prompt contains two explicit few-shot input/output examples.

### Few-Shot Example 1

The first example demonstrates how the Audio Agent should respond when explicit synthetic-audio indicators are supplied.

### Few-Shot Example 2

The second example demonstrates how the Audio Agent should respond when a suspicious audio message is reported without sufficient acoustic evidence.

These examples help guide the local language model toward grounded and consistently structured responses.

## 9. Structured Output

The system defines separate JSON schemas for:

- Audio Agent;
- Video Agent;
- Network Agent;
- Strategic Agent; and
- Self-Evaluation Agent.

The schemas define:

- required fields;
- allowed risk levels where applicable;
- expected data types; and
- whether additional properties are permitted.

The local LLM is called using strict JSON-schema structured output.

Structured output improves communication between agents and reduces malformed LLM responses.

If malformed JSON is returned, the response is rejected and the error can be handled by the workflow's fallback mechanism.

## 10. Shared State

The system uses `MASState` to pass information between LangGraph nodes.

The shared state contains:

```text
user_input
router_result
audio_result
video_result
network_result
overall_threat_score
strategy_result
evaluation_result
errors
simulate_failure
fallback_result
```

Each agent reads the information it requires and returns an update to the shared state.

This allows completed specialist results to remain available even when a later component fails.

## 11. Robustness and Error Handling

The system contains targeted exception handling for:

- connection errors;
- LLM timeouts;
- malformed JSON;
- missing state values;
- invalid risk calculations; and
- simulated component failures.

The local LLM client uses:

```text
Timeout: 30 seconds
Maximum retries: 3
```

Errors are stored in the shared state instead of immediately terminating the complete workflow.

LangGraph then uses conditional routing to redirect recoverable failures to the Fallback Node.

The Fallback Node records its execution time so that the system can verify that a partial response is returned in under five seconds.

## 12. Project Structure

```text
EntityMAS_Final/
|
|-- .env.example
|-- .gitignore
|-- agents.py
|-- config.py
|-- fallback.py
|-- llm_client.py
|-- main.py
|-- prompts.py
|-- README.md
|-- requirements.txt
|-- router.py
|-- state.py
|-- tools.py
|-- workflow.py
|
`-- tests/
    |-- test_fallback.py
    |-- test_router.py
    |-- test_tools.py
    `-- test_workflow.py
```

The `.env` file, Python cache directories, pytest cache, and virtual environment directories are excluded from the final repository/submission package.

## 13. Installation

Open PowerShell inside the project directory.

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate the virtual environment:

```powershell
.venv\Scripts\activate
```

If PowerShell prevents activation, the required commands can still be executed using the installed Python interpreter.

Install the required dependencies:

```powershell
py -m pip install -r requirements.txt
```

The required packages are:

```text
langgraph
openai
python-dotenv
pydantic
pytest
```

## 14. LM Studio Configuration

1. Open LM Studio.
2. Load the `qwen/qwen3-4b-2507` model.
3. Open the Local Server section.
4. Start the LM Studio local server.
5. Confirm that the server is running at:

```text
http://127.0.0.1:1234/v1
```

The project can use mock responses by changing the following value in `config.py`:

```python
MOCK_MODE = True
```

Use the real local LM Studio model by setting:

```python
MOCK_MODE = False
```

For the final normal execution, the project uses:

```python
MOCK_MODE = False
```

## 15. Running the System

Run the main program:

```powershell
py main.py
```

The system will ask for an incident description.

Press Enter without typing anything to use the default coordinated-attack scenario:

```text
A suspicious voice recording was sent to employees while manipulated video footage appeared online and a network intrusion was detected.
```

During normal execution, ensure that:

```python
"simulate_failure": False
```

is set in `main.py`.

## 16. Verified Normal Execution

The complete multi-vector scenario was successfully executed using the local LLM.

The Router detected:

```text
Audio: True
Video: True
Network: True
```

The specialist agents successfully returned structured results.

The verified deterministic overall threat score was:

```text
Overall Threat Score: 90/100
```

Because the score was greater than or equal to 70, the Strategic Agent was activated.

The final strategic risk was:

```text
CRITICAL
```

The Self-Evaluation Agent returned:

```text
Status: PASS
Coverage Score: 1.0
```

The normal execution completed with:

```text
No errors detected.
Simulated Failure: False
The workflow completed successfully.
```

## 17. Selective Routing Verification

The static Router was also tested using an audio-only incident:

```text
An employee received a suspicious voice recording claiming to be from the company director.
```

The verified routing result was:

```text
Audio: True
Video: False
Network: False
```

Only the Audio Agent was executed.

The Video and Network Agents were intentionally skipped.

The resulting overall threat score was:

```text
Overall Threat Score: 20/100
```

Because the score was below 70, the Strategic Agent was not required.

The Self-Evaluation Agent returned:

```text
Status: PASS
Coverage Score: 1.0
```

This demonstrates that the Router selectively activates only the specialist agents required by the detected incident indicators.

## 18. Running the Automated Tests

The project uses `pytest` for automated testing.

Run all tests with:

```powershell
py -m pytest -v
```

The project contains 15 automated tests covering:

- incident-indicator extraction;
- deterministic network scoring;
- overall risk calculation;
- combined-threat routing;
- audio-only routing;
- video-only routing;
- network-only routing;
- case-insensitive routing;
- incidents without recognised indicators;
- complete multi-vector LangGraph execution;
- audio-only workflow execution;
- network-only workflow execution;
- simulated Network Agent failure;
- preservation of partial specialist results; and
- fallback operation when no specialist result is available.

The final verified test result was:

```text
15 passed in 2.71s
```

## 19. Simulating a System Failure

The project contains a controlled failure mechanism for demonstrating fallback behaviour.

Open `main.py`.

Locate:

```python
"simulate_failure": False
```

Change it temporarily to:

```python
"simulate_failure": True
```

Run:

```powershell
py main.py
```

When the default coordinated incident is used, the Network Agent deliberately raises:

```text
Network Agent failure: Simulated Network Agent failure.
```

The system does not crash.

The verified fallback result was:

```text
Status: PARTIAL

Risk Warning:
Fallback activated because a system component failed.

Available Results:
- Audio analysis completed.
- Video analysis completed.

Fallback Execution Time: 0.0
```

The fallback mechanism therefore returned a partial response in under five seconds while preserving successfully completed specialist results.

After completing the fallback demonstration, change the value back to:

```python
"simulate_failure": False
```

The final submitted version should use normal execution mode with simulated failure disabled.

## 20. Human Modifications and AI-Assisted Development

AI-assisted development was used during implementation, testing, debugging, prompt refinement, and documentation.

Human review and modification were applied to important architectural decisions.

Examples include:

- restricting specialist agents to domain-specific evidence;
- calculating the Network Agent threat score deterministically rather than allowing the LLM to invent the numerical score;
- keeping the deterministic network score authoritative after LLM execution;
- providing the Strategic Agent with specialist results instead of allowing it to re-analyse unrestricted raw evidence;
- generating a grounded evaluator summary when a local-model response leaves the summary blank;
- calculating overall escalation using deterministic logic;
- preserving partial specialist results when later components fail;
- redirecting recoverable failures to the common fallback mechanism; and
- using a deterministic score threshold to control Strategic Agent execution.

These modifications were retained because they improve reliability, grounding, explainability, and robustness.

## 21. Security and Configuration

Sensitive configuration values should not be committed to the repository.

The `.gitignore` file excludes:

```text
.env
__pycache__/
*.pyc
.venv/
venv/
.vscode/
.pytest_cache/
```

The project includes `.env.example` as a safe configuration template.

The actual `.env` file should not be included in the final GitHub repository or submission ZIP.

## 22. Limitations

The current system is a prototype.

Its limitations include:

- it analyses textual incident descriptions rather than raw media files;
- routing depends on predefined keywords;
- audio and video files are not directly processed;
- network packets and logs are not directly inspected;
- threat scoring uses predefined deterministic weights; and
- local LLM performance depends on the selected model.

These limitations are intentionally documented so that the prototype's capabilities are not overstated.

## 23. Future Improvements

Possible future improvements include:

- direct audio-file analysis;
- video-forensics integration;
- network-log and packet analysis;
- dynamic semantic routing;
- human-in-the-loop verification;
- persistent incident storage;
- a graphical monitoring dashboard; and
- integration with real cybersecurity tools.

## 24. Conclusion

The Entity Multi-Agent System demonstrates how LangGraph can coordinate specialised agents to analyse a coordinated multi-vector security incident.

The system combines:

- static rule-based routing;
- conditional workflow execution;
- specialised LLM agents;
- strict structured outputs;
- deterministic security tools;
- deterministic overall risk calculation;
- strategic assessment;
- self-evaluation;
- targeted exception handling; and
- safe fallback handling.

The final implementation was successfully verified through 15 automated tests, a complete multi-vector execution, an audio-only selective-routing demonstration, and a simulated Network Agent failure.

The final configuration should use normal execution with:

```python
MOCK_MODE = False
```

and:

```python
"simulate_failure": False
```