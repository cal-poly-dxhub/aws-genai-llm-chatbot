# E-Ciso Refactor
Original proof of concept refactored into broader framework.

Follows same deployment steps as [Original Framework](https://aws-samples.github.io/aws-genai-llm-chatbot/guide/deploy.html)

```
(eciso) $ npm run config

> aws-genai-llm-chatbot@3.1.3 config
> node ./cli/magic.js config

✔ Prefix to differentiate this deployment · eciso
✔ Do you want to deploy a private website? I.e only accessible in VPC (y/N) · false
✔ Do you have access to Bedrock and want to enable it (Y/n) · true
✔ Region where Bedrock is available · us-east-1
✔ Cross account role arn to invoke Bedrock - leave empty if Bedrock is in same account · 
✔ Do you want to enable additional custom plugins?  (Y/n) · true
✔ Do you want to enable the eCISO plugin? (Y/n) · true
✔ Do you want to enable the focus mode for eCISO plugin? (Y/n) · true
✔ Do you want to use any Sagemaker Models (y/N) · false
✔ Do you want to enable RAG (y/N) · false
```

Config has been updated to support eCISO "Plugin". eCISO plugin true adds the module under a menu drop down of Custom Plugins; focus mode rolls away everything else from the core framework and makes eCISO related items only piece showing to user.

## High level changes to note/areas of interest

| File | Comment |
|--------- | ------------ |
| magic-config.ts | Updated prompt options |
| lib/chatbot-api/chatbot-s3-buckets/index.ts | additional s3 bucket to support PDF |
| lib/chatbot-api/functions/api-handler/routes/sessions.py | appsync additional routes |
| lib/model-interfaces/langchain/functions/request-handler/adapters/* | Custom adapter enhancements for eCISO |
| lib/user-interface/* | UI related tweaks | 

General thoughts:
* POC level implementation, so will need further development for production systems
* Needs increased error handling
* PDF Generation should be ASYNC not SYNC
* Likely would want to limit available adapters (not just via ui)
* Retro testing of baseline functionality outside of the following options was not performed
```
✔ Prefix to differentiate this deployment · eciso
✔ Do you want to deploy a private website? I.e only accessible in VPC (y/N) · false
✔ Do you have access to Bedrock and want to enable it (Y/n) · true
✔ Region where Bedrock is available · us-east-1
✔ Cross account role arn to invoke Bedrock - leave empty if Bedrock is in same account · 
✔ Do you want to use any Sagemaker Models (y/N) · false
✔ Do you want to enable RAG (y/N) · false
```
(IE private website etc.)


# Deploying a Multi-Model and Multi-RAG Powered Chatbot Using AWS CDK on AWS

[![Release Notes](https://img.shields.io/github/v/release/aws-samples/aws-genai-llm-chatbot)](https://github.com/aws-samples/aws-genai-llm-chatbot/releases)
[![GitHub star chart](https://img.shields.io/github/stars/aws-samples/aws-genai-llm-chatbot?style=social)](https://star-history.com/#aws-samples/aws-genai-llm-chatbot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Deploy with GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://aws-samples.github.io/aws-genai-llm-chatbot/guide/deploy.html#deploy-with-github-codespaces)

[![Full Documentation](https://img.shields.io/badge/Full%20Documentation-blue?style=for-the-badge&logo=Vite&logoColor=white)](https://aws-samples.github.io/aws-genai-llm-chatbot/)

![sample](docs/about/assets/chabot-sample.gif "AWS GenAI Chatbot")

This solution provides ready-to-use code so you can start **experimenting with a variety of Large Language Models and Multimodal Language Models, settings and prompts** in your own AWS account.

Supported model providers:

- [Amazon Bedrock](https://aws.amazon.com/bedrock/)
- [Amazon SageMaker](https://aws.amazon.com/sagemaker/) self-hosted models from Foundation, Jumpstart and HuggingFace.
- Third-party providers via API such as Anthropic, Cohere, AI21 Labs, OpenAI, etc. [See available langchain integrations](https://python.langchain.com/docs/integrations/llms/) for a comprehensive list.

# Additional Resources

| Resource |Description|
|:-------------|:-------------|
| [AWS Generative AI CDK Constructs](https://github.com/awslabs/generative-ai-cdk-constructs/) | Open-source library extension of the [AWS Cloud Development Kit (AWS CDK)](https://docs.aws.amazon.com/cdk/v2/guide/home.html)  aimed to help developers build generative AI solutions using pattern-based definitions for their architecture. |
| [Project Lakechain](https://github.com/awslabs/project-lakechain) | A powerful cloud-native, AI-powered, document (docs, images, audios, videos) processing framework built on top of the AWS CDK. |

# Roadmap

Roadmap is available through the [GitHub Project](https://github.com/orgs/aws-samples/projects/69)

# Authors

- [Bigad Soleiman](https://www.linkedin.com/in/bigadsoleiman/)
- [Sergey Pugachev](https://www.linkedin.com/in/spugachev/)

# Contributors
[![contributors](https://contrib.rocks/image?repo=aws-samples/aws-genai-llm-chatbot&max=2000)](https://github.com/aws-samples/aws-genai-llm-chatbot/graphs/contributors)

# License

This library is licensed under the MIT-0 License. See the LICENSE file.

- [Changelog](CHANGELOG.md) of the project.
- [License](LICENSE) of the project.
- [Code of Conduct](CODE_OF_CONDUCT.md) of the project.
- [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

# Legal Disclaimer

You should consider doing your own independent assessment before using the content in this sample for production purposes. This may include (amongst other things) testing, securing, and optimizing the content provided in this sample, based on your specific quality control practices and standards.
