# Demo recording script — target 2 minutes 35 seconds

Record only after a successful live Decider + Bedrock run on AWS. Keep the app in **Live models** mode. Demo mode is useful for rehearsal but cannot substantiate the model integration. Do not display AWS credentials, account identifiers or shell history containing secrets.

| Time | Screen | Narration |
| --- | --- | --- |
| 0:00–0:15 | Recovery desk, train scenario | “A cancelled train leaves you with several possible next moves. Trip Rescue gives a small decision model the job of choosing which action to take.” |
| 0:15–0:35 | Show route, ₹3,000 and arrival deadline; run recovery | “I’m in Varkala and need to get to Kochi. Decider sees the request and chooses one of four typed tools. These travel options are fictional fixtures.” |
| 0:35–1:00 | Show actual decision log and confidence | “The choice is in the execution path. Here is the returned tool, its confidence, and the measured HTTP round trip. The chosen tool filters options against my budget and timing.” |
| 1:00–1:20 | Expand a recovery option and show explanation | “Bedrock explains the filtered evidence. It does not choose the tool or make a booking. The interface keeps model provenance separate from inventory provenance.” |
| 1:20–1:45 | Switch to missed flight, run live, show `find_stay` | “Now I missed the last flight and need somewhere tonight. Changing the need changes the selected tool. These stays are in Kochi, not a promise of arrival in Bengaluru.” |
| 1:45–2:05 | Show threshold code and a saved, genuine low-confidence run if available | “The agent validates every choice. Below our experimental threshold, it asks for clarification before running a tool. The threshold still needs evaluation.” |
| 2:05–2:25 | Show `patterns/tool_selection.py` and README | “The reusable asset is the typed question, option set, validator and wiring. Replace the tool criteria to reuse the pattern in another agent.” |
| 2:25–2:35 | Export run evidence and return to desk | “Trip Rescue: a visible next decision, followed by an explanation grounded in what the tool found.” |

If a live inference is slow, disclose the edit and cut the wait. Do not replace measured latency with an animation duration. If no real low-confidence example has been captured, show the gate code and describe its behavior without inventing a model result. Keep the final published video under three minutes and accessible without signing in.
