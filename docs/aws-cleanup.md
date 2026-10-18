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

## Later successful test — cleanup verification pending

A later approved deployment on 18 October ran the actual models successfully. It is separate from the deleted attempts above. Its two-hour timer issued poweroff at 15:05 UTC on 18 October, closing the SSH session. The template specifies termination on instance shutdown and root-disk deletion, but those AWS states still need verification. The CloudFormation stack also needs deletion to remove the remaining IAM role/profile, security group and public key. AWS sign-in expired before that verification could be completed. No claim of account-wide cleanup or final billing reconciliation is made.
