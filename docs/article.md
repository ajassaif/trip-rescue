# Trip Rescue: a small model chooses the next move

A cancelled train creates a practical question: what should I do next? Search for another route, find a room, check a disruption report, or ask for more information? Those are different actions. A fluent answer alone does not choose the right one.

Trip Rescue is an experimental travel recovery desk that gives **tool selection to Strands Decider 2B** and the explanation to **Amazon Bedrock Nova Micro**. The decision changes which tool actually runs.

- [Public source and setup](https://github.com/ajassaif/trip-rescue)
- [Reusable decision recipe](https://github.com/ajassaif/trip-rescue/tree/main/patterns)
- [Demo video](https://ajassaif.github.io/trip-rescue/)
- [Original AWS run evidence](https://github.com/ajassaif/trip-rescue/tree/main/docs/evidence/aws)

The 2:28 demo is a silent, captioned walkthrough of saved responses from the actual AWS runs. Its result panels are rendered from the original JSON; it does not depict new inference. The introductory app screenshot is labeled as an earlier offline-demo view.

## A recovery desk for the next decision

The prototype covers three fictional disruptions in Kerala. A cancelled Varkala-to-Kochi train calls for alternative transport. A missed last flight from Kochi to Bengaluru calls for somewhere to stay in Kochi. Heavy rain on the Munnar-to-Kochi journey calls for a disruption report before planning another leg.

Travelers can edit their location, destination, budget and same-day deadline. The interface shows the selected tool, filtered recovery options and decision trace. It also exports the request and response as JSON.

**All travel inventory is fictional.** The app does not check real availability, establish road safety, buy tickets or book rooms. Real model inference and real travel inventory are separate claims; this project demonstrates the former.

## The decision handed to Decider

The typed question asks which tool should run next, with four allowlisted options:

- `find_transport`: look for another way to reach the destination.
- `find_stay`: find accommodation in the current city when the traveler needs somewhere tonight.
- `check_disruptions`: consult disruption evidence before proceeding when weather or closures matter.
- `clarify`: ask about an ambiguous immediate need.

The client validates the choice, model identifier, confidence and probability distribution before dispatch. Unknown choices and malformed responses fail explicitly. A `clarify` choice or confidence below the experimental **0.80 threshold** pauses the workflow before any recovery tool or Bedrock call.

After selection, deterministic code filters the fictional inventory by route, budget and applicable schedule constraints. A ₹100 budget cannot produce a ₹680 coach ticket. Empty inventory stays empty. A Kochi hotel is not presented as arrival in Bengaluru.

## Bedrock explains the evidence

Bedrock Converse receives the chosen tool's filtered evidence and structured trip constraints. Nova Micro explains the available next step in a few sentences. It cannot choose a different tool or execute a booking. The raw traveler message is excluded from this explanation prompt.

An explicit offline demo mode uses deterministic rules and written summaries, with no model confidence or inference timing. Live mode calls the actual providers and reports errors instead of silently falling back to demo output.

## What ran on AWS

On 18 October 2026, I ran the FastAPI agent and the actual Strands Decider checkpoint on an EC2 `c7i.2xlarge` in `us-east-1`: eight vCPUs, 16 GiB RAM, Ubuntu 24.04, CPU inference. Bedrock used `amazon.nova-micro-v1:0` through an instance role restricted to that model. The local Next.js interface reached the private agent through an SSH tunnel.

| Request | Model choice | Confidence | Decider HTTP time | Agent outcome |
| --- | --- | --- | --- | --- |
| Cancelled train | `find_transport` | 0.9809 | 2,294.96 ms | Three transport options and Bedrock explanation |
| Missed flight | `find_stay` | 0.9847 | 2,162.12 ms | Two Kochi stays and Bedrock explanation |
| Monsoon disruption | `check_disruptions` | 0.9804 | 2,147.43 ms | Two reports and Bedrock explanation |
| Uncertain next step | `find_transport` | 0.5905 | 2,156.77 ms | Gate abstained and asked for clarification; no tool or Bedrock call |

The last result matters: the model's candidate choice was transport, but its confidence did not clear the gate. The application therefore stopped. It did not pretend that Decider had chosen `clarify`.

These four examples are **not an accuracy, calibration or latency benchmark**. Timing measures the Decider HTTP round trip inside the agent. The repository includes requests, responses, package versions and downloaded model revisions so the observations can be inspected and reproduced. The `/evidence` page clearly labels these as recorded AWS results; changing its example does not make a new model call.

The temporary host had a two-hour shutdown timer. The model and agent ran on loopback, SSH was restricted to the operator's IP, and no public application endpoint was exposed. CloudFormation cleanup was verified on 19 October: all five temporary resources were deleted, and no Trip Rescue root disk remained. The deployment can be reproduced from the included CloudFormation template and runbook.

## What I learned

During an earlier hybrid test, a Bedrock explanation incorrectly said no options fit even though the tool returned three. I added result-specific instructions and a narrow contradiction guard, with a regression test for that observed failure. This does not prove general factuality; generated explanations still need review.

The project passed 63 backend tests, seven API smoke checks, TypeScript checking, lint and a production build. Those tests establish software behavior, not model quality. The next evaluation should cover competing needs, adversarial phrasing and threshold sensitivity on a held-out set.

## Reuse the pattern

The `patterns/` directory contains the typed question, option definitions, HTTP client, validator and integration guide. Replace the criteria with your own tools and keep the decision before execution. Give uncertainty a concrete behavior, and preserve provenance so a recorded result cannot be mistaken for a fresh call.

Trip Rescue makes a bounded decision visible: choose the next useful tool, check what it returns, and explain the evidence.

#strands-decider-2b #tool-selection
