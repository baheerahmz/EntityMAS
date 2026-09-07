"""Command-line interface for running the Entity Multi-Agent System."""

from workflow import build_workflow #import the workflow builder


#=========================================================
#DEFAULT INCIDENT
#=========================================================

DEFAULT_INCIDENT = ( #set the default incident scenario
    "A suspicious voice recording was sent to employees "
    "while manipulated video footage appeared online "
    "and a network intrusion was detected."
)


#=========================================================
#DISPLAY FUNCTIONS
#=========================================================

def print_section(title):
    """
    Print a clear section heading.

    Args:
        title: Text to display as the section heading.

    Returns:
        None.
    """

    print("\n" + "=" * 50) #print the top separator
    print(title) #print the section title
    print("=" * 50) #print the bottom separator


def print_agent_result(title, data):
    """
    Display an agent result in a structured format.

    Args:
        title: Heading for the displayed agent result.
        data: Dictionary containing the agent result.

    Returns:
        None.
    """

    print_section(title) #print the agent section heading

    if not data: #check if there is no result
        print("No result available.") #show no result message
        return #stop the function

    for key, value in data.items(): #go through each result field

        label = ( #create a readable label
            key #get the field name
            .replace("_", " ") #replace underscores with spaces
            .title() #capitalize the label
        )

        if isinstance(value, list): #check if the value is a list

            print(f"\n{label}:") #print the list label

            if value: #check if the list has values

                for item in value: #go through each list item
                    print( #print each item
                        f"  - {item}"
                    )

            else: #if the list is empty
                print("  None") #show none

        else: #handle normal values

            print( #print the field and value
                f"\n{label}: {value}"
            )


#=========================================================
#MAIN PROGRAM
#=========================================================

def main():
    """
    Start the Entity Multi-Agent System and analyse
    a user-provided incident or the default scenario.

    Returns:
        None.
    """

    print("\n" + "=" * 50) #print the top program separator
    print("ENTITY MULTI-AGENT SYSTEM") #print the system name
    print("=" * 50) #print the bottom program separator

    print( #ask the user for an incident
        "\nEnter an incident description."
    )

    print( #tell the user they can use the default scenario
        "Press ENTER without typing anything"
    )

    print( #explain the default scenario
        "to use the default coordinated attack scenario."
    )

    user_incident = input( #get the incident from the user
        "\nIncident: "
    ).strip() #remove extra spaces

    if user_incident: #check if the user entered an incident

        incident = user_incident #use the user's incident

    else: #if no incident was entered

        incident = DEFAULT_INCIDENT #use the default incident

    #Human modification:
    #The LangGraph workflow is built once before
    #processing the selected incident.
    app = build_workflow() #build the LangGraph workflow

    initial_state = { #create the initial workflow state
        "user_input": incident, #store the incident description
        "errors": [], #start with an empty error list

        #False = normal execution.
        #True = simulate a Network Agent failure
        #for fallback testing.
        "simulate_failure": False #enable Network Agent failure simulation
    }

    result = app.invoke( #run the workflow
        initial_state #send the initial state
    )

    #=====================================================
    #ORIGINAL INCIDENT
    #=====================================================

    print_section( #display the analysis result section
        "ANALYSIS RESULT"
    )

    print( #display the original incident heading
        "\nOriginal Incident:"
    )

    print( #display the incident
        incident.strip()
    )

    #=====================================================
    #ROUTER RESULT
    #=====================================================

    print_agent_result( #display the Router result
        "ROUTER RESULT",
        result.get( #get the Router result
            "router_result",
            {} #use empty dictionary if not available
        )
    )

    #=====================================================
    #AUDIO AGENT RESULT
    #=====================================================

    print_agent_result( #display the Audio Agent result
        "AUDIO AGENT RESULT",
        result.get( #get the Audio result
            "audio_result",
            {} #use empty dictionary if not available
        )
    )

    #=====================================================
    #VIDEO AGENT RESULT
    #=====================================================

    print_agent_result( #display the Video Agent result
        "VIDEO AGENT RESULT",
        result.get( #get the Video result
            "video_result",
            {} #use empty dictionary if not available
        )
    )

    #=====================================================
    #NETWORK AGENT RESULT
    #=====================================================

    print_agent_result( #display the Network Agent result
        "NETWORK AGENT RESULT",
        result.get( #get the Network result
            "network_result",
            {} #use empty dictionary if not available
        )
    )

    #=====================================================
    #OVERALL THREAT SCORE
    #=====================================================

    print_section( #display the overall threat score section
        "OVERALL THREAT SCORE"
    )

    overall_score = result.get( #get the overall threat score
        "overall_threat_score"
    )

    if overall_score is None: #check if no score is available

        print( #display a message when score is missing
            "No overall threat score available."
        )

    else: #if a score is available

        print( #display the overall threat score
            f"\nOverall Threat Score: "
            f"{overall_score}/100"
        )

    #=====================================================
    #STRATEGIC AGENT RESULT
    #=====================================================

    print_agent_result( #display the Strategic Agent result
        "STRATEGIC AGENT RESULT",
        result.get( #get the Strategy result
            "strategy_result",
            {} #use empty dictionary if not available
        )
    )

    #=====================================================
    #SELF-EVALUATION RESULT
    #=====================================================

    print_agent_result( #display the Self-Evaluation result
        "SELF-EVALUATION RESULT",
        result.get( #get the evaluation result
            "evaluation_result",
            {} #use empty dictionary if not available
        )
    )

    #=====================================================
    #FALLBACK RESULT
    #=====================================================

    fallback_result = result.get( #get the fallback result
        "fallback_result",
        {} #use empty dictionary if not available
    )

    if fallback_result: #check if fallback was activated

        print_agent_result( #display the fallback result
            "FALLBACK RESULT",
            fallback_result #send the fallback data
        )

    #=====================================================
    #ERRORS
    #=====================================================

    print_section( #display the errors section
        "ERRORS"
    )

    errors = result.get( #get the list of errors
        "errors",
        [] #use empty list if no errors exist
    )

    if errors: #check if there are errors

        for error in errors: #go through each error

            print( #display the error
                f"\n- {error}"
            )

    else: #if there are no errors

        print( #display no error message
            "\nNo errors detected."
        )

    #=====================================================
    #EXECUTION MODE
    #=====================================================

    print_section( #display the execution mode section
        "EXECUTION MODE"
    )

    simulate_failure = result.get( #get the failure simulation setting
        "simulate_failure",
        initial_state[ #use the initial setting if not available
            "simulate_failure"
        ]
    )

    print( #display whether failure simulation was used
        f"\nSimulated Failure: "
        f"{simulate_failure}"
    )

    #=====================================================
    #COMPLETION MESSAGE
    #=====================================================

    print_section( #display the workflow completion section
        "WORKFLOW COMPLETED"
    )

    if fallback_result: #check if fallback was used

        print( #display the fallback completion message
            "\nThe workflow completed using "
            "the fallback mechanism."
        )

    else: #if fallback was not used

        print( #display the successful completion message
            "\nThe workflow completed successfully."
        )


#=========================================================
#PROGRAM ENTRY POINT
#=========================================================

if __name__ == "__main__": #check if this file is run directly
    main() #start the main program