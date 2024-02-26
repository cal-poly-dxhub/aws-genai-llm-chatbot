import genai_core.clients

from langchain.llms import Bedrock
from langchain.prompts.prompt import PromptTemplate

from ..base import ModelAdapter
from ..registry import registry

#/model-interfaces/langchain/readme.md
class EcisoPDFAdapter(ModelAdapter):
    def __init__(self, model_id, *args, **kwargs):
        self.model_id = model_id

        super().__init__(*args, **kwargs)

    def get_llm(self, model_kwargs={}):
        bedrock = genai_core.clients.get_bedrock_client()

        params = {}
        if "temperature" in model_kwargs:
            #override
            #params["temperature"] = model_kwargs["temperature"]
            params["temperature"] =  .5
        if "topP" in model_kwargs:
            #params["top_p"] = model_kwargs["topP"]
            params["top_p"] = 0
        if "maxTokens" in model_kwargs:
            #override
            #params["max_tokens_to_sample"] = model_kwargs["maxTokens"]
            params["max_tokens_to_sample"] =  8000

        # probably can just update to streaming = false as we don't want UI to control this aspect.
        return Bedrock(
            client=bedrock,
            model_id=self.model_id,
            model_kwargs=params,
            streaming=model_kwargs.get("streaming", False),
            callbacks=[self.callback_handler],
        )

        return PromptTemplate(
            template=template, input_variables=["context", "question"]
        )

    def get_prompt(self):
        template = """

{input}

{chat_history}

Based on the above conversation detailing the evaluation of the cybersecurity posture of an institution using the NIST (National Institute of Standards and Technology) Cybersecurity Framework, generate a comprehensive report. The conversation provides information on various aspects of the institution's cybersecurity practices. The report should be formatted using Markdown and should include:

Introduction: A brief overview of the cybersecurity evaluation and the relevance of the NIST framework to the institution.
Evaluation based on NIST Framework:
Identify:
Asset Management: Evaluation of how the institution identifies and manages its cyber-related assets.
Business Environment: Assessment of the institution's understanding of its business context and cybersecurity role.
Governance: Analysis of the institution's policies and procedures in relation to cybersecurity.
Risk Assessment: How the institution assesses cybersecurity risks.
Risk Management Strategy: Review of how the institution manages cybersecurity risks.
Identify Grade: [Based on conversation, grade from A to F]
Protect:
Access Control: Evaluation of controls that limit access to critical information and systems.
Training and Awareness: Analysis of the institution's cybersecurity training programs.
Data Security: Review of how data is protected both in transit and at rest.
Maintenance: Evaluation of system and software maintenance practices.
Protective Technology: Assessment of technological solutions employed for cybersecurity.
Protect Grade: [Based on conversation, grade from A to F]
Detect:
Anomalies and Events: How the institution detects unusual and potentially harmful activities.
Monitoring: Assessment of continuous monitoring capabilities.
Detection Processes: Analysis of processes that assist in the detection of cybersecurity events.
Detect Grade: [Based on conversation, grade from A to F]
Respond:
Response Planning: Evaluation of plans in place for cybersecurity incidents.
Mitigation: How the institution works to minimize the impact of cybersecurity incidents.
Improvements: Assessment of processes to improve response capabilities after an event.
Respond Grade: [Based on conversation, grade from A to F]
Recover:
Recovery Planning: Evaluation of the institution's recovery plans post-cybersecurity incident.
Improvements: Analysis of post-event recovery improvements and lessons learned.
Communication: How the institution communicates recovery processes internally and externally.
Recover Grade: [Based on conversation, grade from A to F]
Grading Criteria:
A: Excellent practices, meets or exceeds all best standards.
B: Above average, meets most standards but has minor areas of improvement.
C: Average, meets baseline standards but has significant areas for improvement.
D: Below average, fails to meet many standards and requires considerable improvement.
F: Poor, does not meet minimum standards and requires immediate action.
Overall Grade: [Based on conversation, grade from A to F]
Suggestions/Recommendations: A list of actionable insights based on the weaknesses identified during the evaluation.
Generate the report.

Assistant:"""


        input_variables = ["input", "chat_history"]
        prompt_template_args = {
            "chat_history": "{chat_history}",
            "input_variables": input_variables,
            "template": template,
        }
        prompt_template = PromptTemplate(**prompt_template_args)


        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("~~~E CISO PDF ADAPTER TEMPLATE   ~~~~~~~~~")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(prompt_template)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return prompt_template


# Register the adapter
registry.register(r"^ecisopdf.anthropic.claude*", EcisoPDFAdapter)
