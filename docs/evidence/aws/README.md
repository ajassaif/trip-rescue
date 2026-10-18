# AWS live run evidence - 18 October 2026

These four requests ran through the actual FastAPI agent and Strands Decider on AWS EC2 c7i.2xlarge in us-east-1. Explanations for the three ready outcomes came from Amazon Bedrock Nova Micro using the EC2 instance role. All inventory is fictional.

| File | Observed outcome |
| --- | --- |
| rail.json | find_transport, 0.9809 confidence, 2294.96 ms, three options |
| flight.json | find_stay, 0.9847 confidence, 2162.12 ms, two stays |
| weather.json | check_disruptions, 0.9804 confidence, 2147.43 ms, two reports |
| ambiguous.json | model candidate find_transport at 0.5905; gate abstained, no tool or Bedrock call |
| environment.json | Hardware, operating system, package versions, actual model health and cache revisions |

Each scenario file includes the request, UTC recording timestamp and unmodified API result. No credentials, account IDs or private network addresses are included. Four examples are not a benchmark or accuracy estimate. The recorded-runs page renders these saved files and makes no provider calls.
