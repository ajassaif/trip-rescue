# Model evidence

[18 October AWS-hosted runs](aws/) include all four requests, responses and actual environment metadata. They supersede the hybrid-only status of the earlier examples below.

# Live examples — 17 October 2026

These are actual model responses using local CPU Strands Decider and Amazon Bedrock Nova Micro in us-east-1. All travel records are fictional fixtures. No travel booking or message was sent.

- `live-rail.json`: complete UI export, including request and result.
- `live-flight.json`: API response for the preset missed-flight scenario.
- `live-weather.json`: API response for the preset monsoon scenario.

The latter two files contain responses only. The preset inputs are in `src/lib/scenarios.ts`. Provider latencies are measured HTTP round trips. Three successful examples do not establish accuracy, confidence calibration or performance superiority. The Decider and agent API were not hosted on AWS for these runs.

Credentials, AWS account identifiers, SSH keys and private configuration are excluded. See `../verification.md` for limitations and the explanation issue found during testing.
