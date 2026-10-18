# Submission readiness

## Completed

- Original recovery desk, bounded agent and reusable typed tool-selection recipe.
- Actual Decider and agent on AWS EC2, paired with Bedrock Nova Micro, 18 October 2026.
- Three successful tool paths and a real low-confidence abstention; requests, responses, model revisions and environment saved in [evidence/aws](evidence/aws/).
- Public source repository: https://github.com/ajassaif/trip-rescue.
- 63 backend tests, seven API smoke checks, lint, TypeScript and production build passed.
- Clearly labeled `/evidence` page for inspecting recorded AWS responses without new cloud calls.
- Prepared [Builder Center article](article.md).
- Completed 2:28 captioned [demo video](demo/README.md), rendered from the saved AWS responses; public hosting verification follows the repository push.

## Still required

- Verify anonymous access to the demo video after pushing it to the public repository.
- Publish the Builder Center article with repository/video links and `#strands-decider-2b` and `#tool-selection`.
- Complete the event's project submission and verify its confirmation.
- Verify termination/root-volume deletion and delete the remaining resources from the later temporary AWS stack. Its timer already shut the host down; authenticated AWS access is needed to finish verification.

Public code and successful cloud inference do not by themselves establish a completed entry. No final submission confirmation has been observed.

## Deadline

The official event page, rechecked 19 October 2026, specifies 23 October 2026 at 11:59 PM PDT, or 24 October at 12:29 PM IST. It requires a public repository with a reusable pattern, a Builder Center article, and a public demonstration video under three minutes.

[Event and requirements](https://builder.aws.com/build/hackathons/4f50957c-1d08-37ab-b11c-97516b9adeb4/agent-experience-hackathon-strands-decider)
