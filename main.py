"""Command-line interface for running the Entity Multi-Agent System."""

from workflow import build_workflow


# =========================================================
# DEFAULT INCIDENT
# =========================================================

DEFAULT_INCIDENT = (
    "A suspicious voice recording was sent to employees "
    "while manipulated video footage appeared online "
    "and a network intrusion was detected."
)


# =========================================================
# DISPLAY FUNCTIONS
# =========================================================

def print_section(title):
    """
    Print a clear section heading.

    Args:
        title: Text to display as the section heading.

    Returns:
        None.
    """

    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def print_agent_result(title, data):
    """
    Display an agent result in a structured format.

    Args:
        title: Heading for the displayed agent result.
        data: Dictionary containing the agent result.

    Returns:
        None.
    """

    print_section(title)

    if not data:
        print("No result available.")
        return

    for key, value in data.items():

        label = (
            key
            .replace("_", " ")
            .title()
        )

        if isinstance(value, list):

            print(f"\n{label}:")

            if value:

                for item in value:
                    print(
                        f"  - {item}"
                    )

            else:
                print("  None")

        else:

            print(
                f"\n{label}: {value}"
            )


# =========================================================
# MAIN PROGRAM
# =========================================================

def main():
    """
    Start the Entity Multi-Agent System and analyse
    a user-provided incident or the default scenario.

    Returns:
        None.
    """

    print("\n" + "=" * 50)
    print("ENTITY MULTI-AGENT SYSTEM")
    print("=" * 50)

    print(
        "\nEnter an incident description."
    )

    print(
        "Press ENTER without typing anything"
    )

    print(
        "to use the default coordinated attack scenario."
    )

    user_incident = input(
        "\nIncident: "
    ).strip()

    if user_incident:

        incident = user_incident

    else:

        incident = DEFAULT_INCIDENT

    # Human modification:
    # The LangGraph workflow is built once before
    # processing the selected incident.
    app = build_workflow()

    initial_state = {
        "user_input": incident,
        "errors": [],

        # False = normal execution.
        # True = simulate a Network Agent failure
        # for fallback testing.
        "simulate_failure": False
    }

    result = app.invoke(
        initial_state
    )

    # =====================================================
    # ORIGINAL INCIDENT
    # =====================================================

    print_section(
        "ANALYSIS RESULT"
    )

    print(
        "\nOriginal Incident:"
    )

    print(
        incident.strip()
    )

    # =====================================================
    # ROUTER RESULT
    # =====================================================

    print_agent_result(
        "ROUTER RESULT",
        result.get(
            "router_result",
            {}
        )
    )

    # =====================================================
    # AUDIO AGENT RESULT
    # =====================================================

    print_agent_result(
        "AUDIO AGENT RESULT",
        result.get(
            "audio_result",
            {}
        )
    )

    # =====================================================
    # VIDEO AGENT RESULT
    # =====================================================

    print_agent_result(
        "VIDEO AGENT RESULT",
        result.get(
            "video_result",
            {}
        )
    )

    # =====================================================
    # NETWORK AGENT RESULT
    # =====================================================

    print_agent_result(
        "NETWORK AGENT RESULT",
        result.get(
            "network_result",
            {}
        )
    )

    # =====================================================
    # OVERALL THREAT SCORE
    # =====================================================

    print_section(
        "OVERALL THREAT SCORE"
    )

    overall_score = result.get(
        "overall_threat_score"
    )

    if overall_score is None:

        print(
            "No overall threat score available."
        )

    else:

        print(
            f"\nOverall Threat Score: "
            f"{overall_score}/100"
        )

    # =====================================================
    # STRATEGIC AGENT RESULT
    # =====================================================

    print_agent_result(
        "STRATEGIC AGENT RESULT",
        result.get(
            "strategy_result",
            {}
        )
    )

    # =====================================================
    # SELF-EVALUATION RESULT
    # =====================================================

    print_agent_result(
        "SELF-EVALUATION RESULT",
        result.get(
            "evaluation_result",
            {}
        )
    )

    # =====================================================
    # FALLBACK RESULT
    # =====================================================

    fallback_result = result.get(
        "fallback_result",
        {}
    )

    if fallback_result:

        print_agent_result(
            "FALLBACK RESULT",
            fallback_result
        )

    # =====================================================
    # ERRORS
    # =====================================================

    print_section(
        "ERRORS"
    )

    errors = result.get(
        "errors",
        []
    )

    if errors:

        for error in errors:

            print(
                f"\n- {error}"
            )

    else:

        print(
            "\nNo errors detected."
        )

    # =====================================================
    # EXECUTION MODE
    # =====================================================

    print_section(
        "EXECUTION MODE"
    )

    simulate_failure = result.get(
        "simulate_failure",
        initial_state[
            "simulate_failure"
        ]
    )

    print(
        f"\nSimulated Failure: "
        f"{simulate_failure}"
    )

    # =====================================================
    # COMPLETION MESSAGE
    # =====================================================

    print_section(
        "WORKFLOW COMPLETED"
    )

    if fallback_result:

        print(
            "\nThe workflow completed using "
            "the fallback mechanism."
        )

    else:

        print(
            "\nThe workflow completed successfully."
        )


# =========================================================
# PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()