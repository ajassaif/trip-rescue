# Trip Rescue: a small model chooses the next move

**Unpublished draft.** The implementation and local demo exist. Before publishing, run the actual Decider and Bedrock workflow on AWS, attach the public repository and video URLs, and update this draft with observed results. Do not present demo-mode runs as model evidence.

Tags: `#strands-decider-2b` `#tool-selection`

A cancelled train creates a very practical question: what should I do next? Search for another route, find a room, check whether the road is closed, or ask for more information? Those are different actions, and a fluent answer alone does not choose the right one.

Trip Rescue is an experimental recovery desk for that moment. It gives the next-tool decision to Strands Decider 2B and the explanation to Amazon Bedrock.

## The experience

The prototype includes three fictional travel disruptions. A cancelled train from Varkala to Kochi calls for alternative transport. A missed last flight from Kochi to Bengaluru calls for somewhere to stay in Kochi. Heavy rain on the Munnar–Kochi journey calls for a disruption report before making further plans.

Travelers can change their location, destination, budget, and same-day deadline. The interface shows the selected tool, filtered options, and an inspectable trace. A schematic route map provides context. No tickets or rooms are booked, and all travel inventory is clearly labeled as fictional.

## The decision handed to Decider

The typed question asks which recovery tool should run next. Its options are `find_transport`, `find_stay`, `check_disruptions`, and `clarify`, each with an explicit description. The decision sits directly before an allowlisted dispatcher. Choosing a different option changes which evidence the agent obtains.

The client validates the returned choice, model identifier, confidence, and probability distribution. An unknown choice or malformed answer is an error. A `clarify` choice or confidence below the initial 0.8 threshold pauses the workflow. That threshold is a hypothesis to evaluate, not an accuracy guarantee.

The selected tool then applies deterministic route, budget and schedule constraints. A ₹100 budget cannot produce a ₹680 coach ticket. Empty inventory stays empty. For accommodation, arrival means check-in in the current city, not arrival at the original destination.

## Bedrock’s role

Bedrock Converse receives filtered evidence and structured trip constraints. Its job is to explain the available next step in a few sentences. The raw user message is excluded from this explanation prompt, and the system instruction requires it to acknowledge fictional inventory and avoid invented fares, timings or reservations.

The application has an explicit offline demo mode so the interface and constraint behavior can be explored without cloud credentials. It uses deterministic rules and written summaries, with no model confidence or model timing displayed. Live mode calls the actual services. An unavailable provider produces an error instead of quietly becoming a demo run.

## What another builder can reuse

The `patterns/` directory contains the typed question, option definitions, HTTP client, strict response validation, and a short integration guide. Builders can replace the criteria with their own tool set. The important seam is that the decision is evaluated before tool execution, and low-confidence cases have a concrete way to stop.

## What remains to learn

The 63 backend tests cover constraints, service failures, malformed responses, confidence handling and an observed explanation contradiction. Separately, actual local CPU Decider plus AWS Bedrock runs chose the expected tools for all three presets. Their Decider HTTP times were approximately 24.3, 42.9 and 14.6 seconds, respectively. These are individual observations, not a performance comparison or accuracy estimate. The next evaluation should include ambiguous requests, competing needs, missing information, and threshold sensitivity, with a separate held-out set for reporting results. AWS hosting of the agent remains pending.

The hypothesis is practical: separating a bounded decision from its explanation can make an agent easier to inspect and evaluate. Trip Rescue makes that separation visible, one next move at a time.
