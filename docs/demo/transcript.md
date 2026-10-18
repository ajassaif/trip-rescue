# Trip Rescue demo transcript

Silent, captioned walkthrough of saved actual AWS responses, recorded 18 October 2026. Travel inventory is fictional. Response panels are rendered directly from the original JSON evidence, not new inference. The introductory UI screenshot is from an earlier offline demo.

## One useful next move.

A cancelled train, a missed flight, or heavy rain can leave a traveler unsure what to do next. Trip Rescue gives that next decision to a small model.

This is an edited walkthrough of saved responses from real AWS runs on October eighteenth. All travel inventory is fictional. No new inference happens in this video.

## Decider chooses. Bedrock explains.

The agent and Strands Decider ran on an eight CPU, sixteen gigabyte EC2 instance. Amazon Bedrock Nova Micro supplied the explanations through a model restricted instance role.

Decider chooses one typed tool. A validator and confidence gate run before execution. Deterministic code filters the tool evidence, then Bedrock explains that evidence.

## Find another way to Kochi.

The traveler is in Varkala, with three thousand rupees and a nine p.m. arrival deadline. Decider chose find transport, with confidence zero point nine eight zero nine.

The tool returned three fictional options after route, fare and schedule filtering. Nova Micro explained those options. This two point three second figure is the recorded Decider HTTP time, not an animation timer.

## Tonight comes before tomorrow.

Now the traveler missed the last flight and needs somewhere tonight. Decider selected find stay, with confidence zero point nine eight four seven.

The agent returned two fictional stays in Kochi. Those rooms do not promise arrival in Bengaluru. The chosen tool changes the evidence Bedrock receives.

## Check the disruption first.

For heavy rain on the Munnar to Kochi route, Decider chose check disruptions, with confidence zero point nine eight zero four.

The agent returned two fictional reports. It does not establish real road safety, availability, or an arrival guarantee.

## Uncertainty changes the action.

Here the traveler says their plans changed but their immediate need is unclear. The model proposed find transport, with confidence zero point five nine zero five.

That is below the experimental zero point eight threshold. The application selected clarify and asked a question. No recovery tool or Bedrock call ran.

## Inspect it. Adapt it. Evaluate it.

The public repository includes the typed question, tool choices, validator, original requests and responses, and model environment. The recorded results page lets you inspect each saved run.

Four examples are not an accuracy or performance benchmark. Reuse the pattern, evaluate the threshold on your own tasks, and keep uncertainty visible. Trip Rescue: a useful next decision, grounded in evidence.
