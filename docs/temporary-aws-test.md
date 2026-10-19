# Temporary AWS live test — real inference verified

Updated 19 October 2026: the first two deployment attempts were deleted and verified before model installation. A later approved deployment on 18 October successfully installed and ran the actual Decider and FastAPI agent, using Bedrock Nova Micro through the instance role. Four requests were captured: three successful recovery tools and one low-confidence abstention. See [original evidence](evidence/aws/). Its two-hour timer shut the host down at 15:05 UTC on 18 October; all five stack resources were subsequently deleted, and EC2/EBS cleanup verified on 19 October. Both the earlier attempts and this later deployment have verified cleanup records.

The setup below was exercised for that successful run. Local AWS CLI installation was blocked by automatic approval review, so deployment used authenticated AWS CloudShell. SSH authentication used EC2 Instance Connect with a 60-second temporary public key; the private key remained local.

## Concrete scope and expected cost

One Ubuntu 24.04 x86_64 `c7i.2xlarge` in `us-east-1`: 8 vCPU, 16 GiB RAM, encrypted 30 GB gp3 root disk, one automatically assigned public IPv4. Run Decider on `127.0.0.1:8099` and FastAPI on `127.0.0.1:8100`. Keep Next.js on the laptop and reach FastAPI over an SSH tunnel. There is no load balancer, NAT gateway, Elastic IP, new VPC, container platform, S3 bucket, SSM agent role, or public application port.

Prices checked 2026-10-17, before tax or credits:

| Item | Rate | Two-hour test estimate |
| --- | --- | --- |
| Linux shared On-Demand c7i.2xlarge, us-east-1 | $0.357/hour | $0.714 |
| One public IPv4 | $0.005/hour | $0.010 |
| 30 GB gp3, baseline 3,000 IOPS / 125 MiB/s | approximately $0.08/GB-month | $0.0067 using a 30-day month |
| Nova Micro, 30 calls at 2,000 input / 220 output tokens each | $0.000035/1K input; $0.00014/1K output | $0.0031 |
| **Expected total** | | **About $0.74; allow $1 for the initial test** |

The target is below $5, not a hard billing cap. Account quotas, plan restrictions, taxes, other account activity and credit eligibility still apply. Do not assume c7i is free-tier eligible. Verify the existing credit balance/expiry in Billing; estimate gross cost first. Model downloads are inbound to EC2; application responses are small. Keep the test sequential and under 30 live runs initially. No provisioned throughput or custom-model training is involved.

Sources: the [official AWS Linux us-east-1 EC2 price feed](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20(N.%20Virginia)/Linux/index.json) returned `c7i.2xlarge` at `0.3570000000` (rate `D23DFG4YVGYMSX7G.JRTCKXETXF.6YS6EN2CT7`); [C7i specifications](https://aws.amazon.com/ec2/instance-types/c7i/); [VPC IPv4 pricing](https://aws.amazon.com/vpc/pricing/); [EBS pricing](https://aws.amazon.com/ebs/pricing/); [official regional Bedrock price catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/current/us-east-1/index.json), whose Nova Micro On-demand Inference entries returned the token rates above. Recheck rates before a later launch.

## Reviewable files and permissions

`infra/temporary-live-test.json` creates exactly one EC2 instance, one SSH security group, one imported public key, one IAM role and one instance profile. The key parameter accepts a public OpenSSH key; CloudFormation does not generate/store a private key. The role permits only `bedrock:InvokeModel` on `arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0`, conditioned on `us-east-1`. That action supports [non-streaming Converse](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html). No streaming, cross-region inference profile, wildcard model, management, PassRole or logging permission is given to the instance.

Inbound traffic is TCP 22 from the operator's supplied IPv4 `/32` only. Outbound is HTTPS 443 for Ubuntu/Python packages, Hugging Face and regional Bedrock. VPC-provided DNS and IMDS remain available. IMDSv2 is mandatory with hop limit 1. The root disk is encrypted with the account's default EBS key and deleted on termination. API credentials come from the role; do not upload `.env`, AWS profiles, access keys or the SSH private key.

Boot first installs an absolute, persistent systemd expiry timer for two hours later, then prepares Python. The timer invokes OS poweroff; EC2's `InstanceInitiatedShutdownBehavior=terminate` makes this terminate the host and delete the root disk. A reboot does not reset the saved deadline. This is a local OS safeguard, not an independent AWS billing control: verify the armed timer immediately; a failed boot or disabled timer needs manual termination. Expiry does not delete the CloudFormation stack's remaining IAM/SG/public-key resources.

## Inputs and launch, only after approval

Required inputs: current operator public IPv4 `/32`, existing SSH **public** key, existing VPC ID and existing public subnet ID in the same VPC. Do not substitute a broad CIDR. Read-only account checks confirmed an active internet-gateway route, a public candidate subnet in `us-east-1a`, c7i.2xlarge offered in that zone, and a 32-vCPU standard On-Demand quota. The Canonical AMI parameter resolved successfully. Capacity at launch remains subject to availability. Nova Micro invocation succeeded using the local application's temporary key; the instance role successfully invoked Nova Micro during the 18 October test.

CloudFormation's initial change-set validation rejected `Throughput` under an EC2 instance's EBS block mapping. The template now omits that unsupported property and uses the gp3 baseline throughput. The corrected `reviewed-test-v2` change set passed and lists exactly the five proposed resources. An unexecuted change set does not create its proposed EC2/IAM resources.

Upload the reviewed JSON to CloudShell using its upload UI. After approval, use one fixed stack name to avoid duplicate hosts. Paste the explicit parameter values in CloudShell; these are public configuration, not private credentials:

```bash
read -r -p 'Current operator public IPv4/32: ' SSH_CIDR
read -r -p 'OpenSSH public key: ' SSH_PUBLIC_KEY
aws cloudformation validate-template --region us-east-1 --template-body file://temporary-live-test.json
aws cloudformation deploy --region us-east-1 \
  --stack-name trip-rescue-live-test \
  --template-file temporary-live-test.json \
  --parameter-overrides \
    VpcId=YOUR_VPC_ID \
    PublicSubnetId=YOUR_PUBLIC_SUBNET_ID \
    SshSourceCidr="$SSH_CIDR" SshPublicKey="$SSH_PUBLIC_KEY" \
  --capabilities CAPABILITY_IAM --no-fail-on-empty-changeset
aws cloudformation describe-stacks --region us-east-1 --stack-name trip-rescue-live-test --query 'Stacks[0].Outputs'
```

Deploy is repeatable for an existing unchanged stack, but do not update/replace a running host or launch a second stack without reviewing the change and cost. If the first launch rolls back or has already expired, delete its stack before preparing a fresh attempt. The template deliberately imports a key rather than creating one; no private key is returned by AWS. The deployer needs CloudFormation and the EC2/IAM/PassRole permissions to create these specific resources; those privileges are not attached to the host.

## Upload and bootstrap

Use the EC2 instance's console system log to verify its SSH host-key fingerprint before accepting the first SSH connection. Keep SSH's normal host-key checking enabled. Substitute the public IP from stack outputs and the local private-key path. The private key stays local.

Prepare and send only backend source, the reusable recipe and the reviewed setup helper from the project root:

```powershell
tar --exclude=__pycache__ --exclude=.pytest_cache -czf infra/trip-rescue-source.tar.gz backend patterns infra/temporary-live-test-setup.sh
scp -i .local/trip-rescue-test infra/trip-rescue-source.tar.gz ubuntu@PUBLIC_IP:trip-rescue-source.tar.gz
ssh -i .local/trip-rescue-test ubuntu@PUBLIC_IP
```

On the host:

```bash
sudo systemctl list-timers trip-rescue-expiry.timer --no-pager
sudo systemctl status trip-rescue-expiry.timer --no-pager
mkdir -p ~/trip-rescue
tar -xzf ~/trip-rescue-source.tar.gz -C ~/trip-rescue
cd ~/trip-rescue
bash infra/temporary-live-test-setup.sh
sudo journalctl -u trip-rescue-decider -u trip-rescue-api --no-pager -n 80
curl --fail http://127.0.0.1:8099/health
curl --fail http://127.0.0.1:8100/health
```

Do not continue installing if the expiry timer is missing or inactive. The setup helper is repeatable, uses separate Python 3.12 virtual environments for the API and Decider, and installs CPU-only torch 2.7.1 before the pinned official Decider source revision `930e6d5de16309be32579f5631a7369a3322140c`. It starts a single model process and one API worker with no automatic restart loop. Model download/loading can take minutes; a running service or configuration health response is not proof of an actual live call.

The [official CPU instructions](https://github.com/strands-labs/strands-decider/blob/930e6d5de16309be32579f5631a7369a3322140c/docs/inference.md) support the CPU-only torch wheel and `--device cpu`. The Qwen 2B base download is about 4.5 GB, with fp32 runtime weights and extra activation memory; 16 GiB is a practical initial sizing choice, not a measured guarantee for this host. CPU latency and memory use must be observed. Use short scenario messages, one request at a time, and no vision. If loading runs out of memory or inference exceeds the 60-second provider timeout, stop and inspect rather than silently switching model, threshold or mode. The setup pins code; the named model repository can change, so retain its reported checkpoint/model metadata and installed package versions with test evidence.

## Connect the existing local UI

In one local terminal, keep a tunnel open (local 18100 avoids conflict with the old local API):

```powershell
ssh -i .local/trip-rescue-test -o ExitOnForwardFailure=yes -N -L 127.0.0.1:18100:127.0.0.1:8100 ubuntu@PUBLIC_IP
```

In another local terminal in the project root:

```powershell
$env:AGENT_API_URL = 'http://127.0.0.1:18100'
npm run dev:web
```

Run the UI's live mode only after both remote health endpoints respond. Start with one rail scenario, then inspect decision provenance, actual numeric confidence, tool execution or abstention, and Bedrock explanation provenance. Low confidence is a valid abstention; do not lower the gate merely to produce a demo result. Export the run. Successful live inference requires observed Decider and Bedrock responses; all transport/stay/advisory inventory remains fictional. No booking is performed. Check the expiry timer and remaining session time before further scenarios.

## Cleanup and verification

Download required run evidence before expiry because the root disk will be destroyed. To finish early, run `sudo systemctl poweroff` on the host, or terminate its exact instance ID in EC2. From CloudShell, delete the single stack and wait:

```bash
aws cloudformation delete-stack --region us-east-1 --stack-name trip-rescue-live-test
aws cloudformation wait stack-delete-complete --region us-east-1 --stack-name trip-rescue-live-test
```

Confirm the recorded instance ID is `terminated`, the attached root volume no longer exists, the autoassigned IPv4 is released, and the stack deletion succeeded. This also removes the imported public key, SG, profile and role. Do not delete unrelated VPC, subnet, keys or volumes. Review Billing later for actual cost and credit application. Local archives and SSH keys can be retained locally until evidence is safe; no cloud service has a cleanup role.

The AMI parameter follows [Canonical's official CloudFormation guidance](https://documentation.ubuntu.com/aws/aws-how-to/instances/build-cloudformation-templates/). Termination behavior and public-key import semantics are documented in [EC2 instance properties](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-ec2-instance.html) and [EC2 KeyPair properties](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-ec2-keypair.html).
