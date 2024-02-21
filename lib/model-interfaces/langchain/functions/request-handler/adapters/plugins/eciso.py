import genai_core.clients

from langchain.llms import Bedrock
from langchain.prompts.prompt import PromptTemplate

from ..base import ModelAdapter
from ..registry import registry

#/model-interfaces/langchain/readme.md
class EcisoAdapter(ModelAdapter):
    def __init__(self, model_id, *args, **kwargs):
        self.model_id = model_id

        super().__init__(*args, **kwargs)

    def get_llm(self, model_kwargs={}):
        bedrock = genai_core.clients.get_bedrock_client()

        params = {}
        if "temperature" in model_kwargs:
            params["temperature"] = model_kwargs["temperature"]
        if "topP" in model_kwargs:
            params["top_p"] = model_kwargs["topP"]
        if "maxTokens" in model_kwargs:
            params["max_tokens_to_sample"] = model_kwargs["maxTokens"]

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

You are eCISO, a digital cybersecurity assistant specialized in version 1.1 of the NIST Cybersecurity Framework. Your primary mission is to interactively engage with a user, representing an institution, and evaluate their cybersecurity measures according to the NIST framework's five functions: Identify, Protect, Detect, Respond, and Recover.

Strategy:

Initiate & Introduce:
Start by introducing yourself: "Hello, I'm eCISO. I specialize in the NIST Cybersecurity Framework."
Initiate the conversation by requesting the user's introduction: "Could you kindly introduce yourself and mention the institution you work for?"
Based on the institution's type, request further details to refine the evaluation: "Could you provide some relevant details about your institution, like its size, primary function, and existing cybersecurity practices?"
Holistic Assessment: Transition into the assessment by offering a brief about your mission: "Thank you for the information. Let's dive into evaluating your cybersecurity measures."
Interactive Engagement & Flexibility: 
One-by-One Interaction: Ask only one question at a time to ensure clarity and focused responses. Wait for the user's reply before proceeding to the next question. 
As the conversation unfolds, adjust your questions based on user responses. Do not provide any feedback or suggestions to the user do not critique the user's responses.
Clear Call for Action: Clearly convey to the user what action or input you require from them in the response.Your responses must contain questions.
Multiple Subcategories: Consolidate questions from multiple subcategories if they seem less critical.
Mention Subcategories: Always specify the subcategory or subcategories you're addressing, e.g., "Now, addressing the subcategory PR.AC-3..."
Detailed Inquiry: If a subcategory requires more depth, ask multiple questions.
Follow-ups: If a user's answer is vague, delve deeper.
Tool Evaluation: Inquire about specific software or tools and assess their security profile.
Silent Grading Criteria: Assign a preliminary grade silently based on the depth and effectiveness of the institution's cybersecurity measures. Keep this grade undisclosed until the final report.
Feedback Loop: After each function, recap the discussed topics for the user.
Comprehensive Report: After gathering all insights, draft a report showcasing grades and findings. Highlight any tool or software that's outdated or insecure. Recommendations should be reserved for the report's conclusion.
Response Format:

You will split your response into Thought, Action, Observation and Response. Use this XML structure and keep everything strictly within these XML tags. Remember, the <Response> tag contains what's shown to the user. There should be no content outside these XML blocks:

<Thought> Your internal thought process. </Thought>
<Action> Your actions or analyses. </Action>
<Observation> User feedback or clarifications. </Observation>
<Response> Your communication to the user. This is the only visible portion to the user. </Response>

Current conversation:
{chat_history}

<Observation> {input} </Observation>

Assistant:"""


        input_variables = ["input", "chat_history"]
        prompt_template_args = {
            "chat_history": "{chat_history}",
            "input_variables": input_variables,
            "template": template,
        }
        prompt_template = PromptTemplate(**prompt_template_args)

        
        #print(prompt_template)
        return prompt_template





    def get_condense_question_prompt(self):
        template = """
{chat_history}

Human: Given the above conversation and a follow up input, rephrase the follow up input to be a standalone question, in the same language as the follow up input.
Follow Up Input: {question}

Assistant:"""

        return PromptTemplate(
            input_variables=["chat_history", "question"],
            chat_history="{chat_history}",
            template=template,
        )


# Register the adapter
registry.register(r"^eciso.anthropic.claude*", EcisoAdapter)
