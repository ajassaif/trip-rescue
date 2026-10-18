# Private AWS demo deployment

Status as of 19 October 2026: the [temporary CPU deployment](temporary-aws-test.md) successfully ran Decider and the agent on AWS on 18 October, paired with Bedrock through an instance role. See [original evidence](evidence/aws/). The timer shut the host down; final stack cleanup verification is pending. The full-stack SSM deployment below is an alternative that has not been executed.

## Deployment shape

Use one Linux EC2 instance for the web app, Python API and Decider model server. Keep all three bound to `127.0.0.1`. Use an IAM instance role for Bedrock and AWS Systems Manager for private browser access. This avoids exposing the experimental model server or the unauthenticated recovery API publicly.

1. Create an instance with enough RAM and disk for the selected model and runtime. For CUDA, use a supported NVIDIA Linux image and the upstream Decider setup. CPU is suitable for experimentation if its observed latency fits the demo; there is no promised response time.
2. Attach a role with Systems Manager managed-instance permissions and narrowly scoped `bedrock:InvokeModel` access for your chosen model or inference profile. Cross-region inference profiles may require the underlying model resources too. Use the permissions required by the actual model/profile, not a wildcard administrative policy.
3. Allow the instance outbound access needed for package installation, model downloads, Bedrock and SSM. No inbound application ports are required for the tunnel workflow. Confirm the instance appears as an online Systems Manager managed node.
4. Install Node.js 24, Python 3.12 with venv, Git and the model's documented runtime prerequisites. Transfer the reviewed project source, excluding `.env`, `.venv`, `node_modules`, `.git`, `.local`, caches and any credentials. Recreate dependencies on Linux from the committed lockfiles.

## Build the app

Run from the repository root:

```bash
npm ci
npm run build
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.lock
python3 -m venv .decider-venv
.decider-venv/bin/python -m pip install strands-decider
```

Keep the inference environment separate. Record its package version with `.decider-venv/bin/python -m pip show strands-decider` and record the model revision used for the demo.

In terminal 1, start the CPU model server (or the official CUDA variant on appropriate hardware):

```bash
.decider-venv/bin/strands-decider serve StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --device cpu --port 8099
```

In terminal 2, export actual configuration and start the API. Replace the model value with one verified for your region and account:

```bash
export STRANDS_DECIDER_URL=http://127.0.0.1:8099
export AWS_REGION=ap-south-1
export AWS_USE_INSTANCE_ROLE=true
export BEDROCK_MODEL_ID=your-converse-compatible-model-or-profile-id
export PROVIDER_TIMEOUT_SECONDS=60
.venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8100
```

In terminal 3, start the production web server:

```bash
AGENT_API_URL=http://127.0.0.1:8100 npm start
```

These foreground processes are appropriate for a supervised recording. Use a process manager with the same working directory and environment if you need a persistent service. An idle instance still incurs charges; stop or terminate demo resources after use, accounting for retained storage.

## Open it privately

Install the AWS CLI and Session Manager plugin locally, and authenticate with an identity permitted to start a session on this instance. Use the actual instance ID. This PowerShell example passes parameters via a file to avoid quoting ambiguity:

```powershell
'{"portNumber":["3100"],"localPortNumber":["3101"]}' | Set-Content -Encoding ascii .\ssm-port-parameters.json
aws ssm start-session --target YOUR_INSTANCE_ID --document-name AWS-StartPortForwardingSession --parameters file://ssm-port-parameters.json
```

Then visit `http://127.0.0.1:3101`. Keep the tunnel open during the demo. Local 3101 avoids a clash with the development app on 3100. This makes the agent run on AWS while access remains private. The required demo video can be publicly shared after recording.

## Verify before recording

- `/health` on port 8099 identifies the loaded Decider checkpoint.
- `/health` on port 8100 reports configuration present.
- A live recovery returns `Strands Decider live HTTP` and `Amazon Bedrock Converse live` provenance.
- The trace identifies the actual model and measured decision HTTP round trip.
- The selected tool differs between transport and accommodation examples.
- Low confidence produces clarification without executing a tool; use a real observed example, not an invented confidence number.
- Export the successful run JSON and record the model revision, region and instance hardware alongside it.

All inventory remains fictional. Review generated explanations for unsupported claims. Do not claim latency savings without a measured baseline on comparable hardware and requests.

## Sources checked 16 October 2026

- [Official Decider inference guide](https://github.com/strands-labs/strands-decider/blob/main/docs/inference.md): serving and supported runtime options.
- [Amazon Bedrock Converse](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html): invocation and permission model.
- [Session Manager port forwarding](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html): managed-node prerequisites and tunnel command.

The repository now includes `infra/temporary-live-test.json` and its setup helper. Account-specific parameters, credentials and private keys remain in ignored local files. Creating the proposed IAM role and SSH access still requires action-time confirmation in the browser workflow.
