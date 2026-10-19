# AWS cleanup — 18 October 2026

The user requested cleanup before continuing the temporary cloud test. The `trip-rescue-live-test` CloudFormation stack in `us-east-1` reached `DELETE_COMPLETE`; the console shows deletion time 18 October 2026, 11:25:22 IST. The earlier rolled-back attempt also shows `DELETE_COMPLETE`.

| Resource | CloudFormation final status |
| --- | --- |
| TestHost — one c7i.2xlarge | DELETE_COMPLETE |
| ImportedSshKey | DELETE_COMPLETE |
| SshOnlySecurityGroup | DELETE_COMPLETE |
| NovaMicroInstanceProfile | DELETE_COMPLETE |
| NovaMicroRole | DELETE_COMPLETE |

The subsequent unfiltered EC2 inventory contains only an unrelated stopped `bylaw-cpu` instance. The unfiltered EBS inventory contains one 60 GiB disk attached to that unrelated instance; no Trip Rescue 30 GiB root disk remains. Those unrelated resources were left intact. This verifies the Trip Rescue deployment cleanup, not every service or region in the AWS account. Final billing and credit application have not been reconciled.

Raw console resource status and a screenshot are retained locally under ignored `.local/aws-resources-after-cleanup.txt` and `.local/aws-cleanup-complete.png`. Account/resource identifiers are kept out of this public-facing record.

## What the live tests establish

All three scenarios passed using actual local CPU Strands Decider inference and AWS Bedrock Nova Micro. The EC2 infrastructure was created, but no SSH connection, source upload, model installation or AWS-hosted agent inference was completed before cleanup. Infrastructure creation alone does not establish that the agent ran on AWS. Travel data remains fictional.

Before claiming a qualifying hackathon submission, complete AWS-hosted agent verification and publish the public repository, Builder Center article and video under three minutes. The source, deployment runbook, drafts and hybrid live evidence are preserved.

## Later successful test — cleanup verified 19 October 2026

The later approved deployment ran Decider and the agent on EC2 with real Bedrock calls on 18 October. Its timer issued poweroff at 15:05 UTC. CloudFormation deletion was requested and verified on 19 October, with deletion timestamp 04:05:43 UTC (09:35:43 IST).

| Resource | Verified status |
| --- | --- |
| TestHost | DELETE_COMPLETE |
| ImportedSshKey | DELETE_COMPLETE |
| NovaMicroRole | DELETE_COMPLETE |
| NovaMicroInstanceProfile | DELETE_COMPLETE |
| SshOnlySecurityGroup | DELETE_COMPLETE |

The exact test instance no longer appeared in EC2 inventory. Regional EBS inventory contained only the unrelated pre-existing 60 GiB volume; no Trip Rescue root disk remained. The test instance had no allocated address. Its automatically assigned IPv4 was not an Elastic IP and is released with instance termination.

Scope: all resources created by this Trip Rescue temporary deployment. Unrelated infrastructure was left untouched. No account-wide zero-resource or final-billing claim is made. Actual billed cost and credit application have not been reconciled. Model inference was on demand, with no provisioned Bedrock throughput created.
