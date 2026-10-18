# Submission readiness

## Present in this repository

- Original Trip Rescue interface and bounded agent workflow.
- Three fictional disruption scenarios with honest demo provenance.
- Real Decider HTTP and Amazon Bedrock Converse integration paths.
- Reusable typed tool-selection pattern and its agent wiring.
- Constraint, abstention and provider-contract tests.
- Private AWS deployment instructions, article draft and recording script.
- Verified local Decider + AWS Bedrock runs for all three tools, with live UI screenshot and exported evidence.

## Still required before claiming a qualifying submission

- Run the actual Decider 2B checkpoint and Bedrock model successfully on AWS.
- Capture AWS-hosted model identity, hardware, region and exported live evidence (hybrid local/cloud evidence already exists).
- Evaluate ambiguous requests and uncertain cases with the actual models; all three preset tool choices have passed.
- Publish this original source to a public repository with the reusable recipe clearly labeled.
- Finalize and publish the Builder Center article with actual results and repository/video links.
- Record and publicly host a demonstration under three minutes.
- Apply `#strands-decider-2b` and `#tool-selection` and submit before the verified deadline.

Real Bedrock cloud inference succeeded from the local agent on 17 October. The temporary EC2 stack was launched, then deleted on 18 October before agent/model installation or testing. No AWS-hosted agent run, public repository, article or video has been completed by this build. The project does not yet satisfy the agent-on-AWS submission gate. See [cleanup record](aws-cleanup.md).

## Deadline note

Rechecked on 18 October 2026: the official event page specifies 23 October 2026 at 11:59 PM PDT, corresponding to 24 October at 12:29 PM IST. Required materials include a public repository with the reusable pattern, a Builder Center article and a public demonstration video under three minutes.

[Event](https://builder.aws.com/build/hackathons/4f50957c-1d08-37ab-b11c-97516b9adeb4/agent-experience-hackathon) · [Rules](https://builder.aws.com/build/hackathons/4f50957c-1d08-37ab-b11c-97516b9adeb4/agent-experience-hackathon?tab=rules)
