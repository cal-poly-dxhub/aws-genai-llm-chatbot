import genai_core.clients

from langchain.llms import Bedrock
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage


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
            #override
            #params["temperature"] = model_kwargs["temperature"]
            params["temperature"] =  0
        if "topP" in model_kwargs:
            #params["top_p"] = model_kwargs["topP"]
            params["top_p"] = 0
        if "maxTokens" in model_kwargs:
            #override
            #params["max_tokens_to_sample"] = model_kwargs["maxTokens"]
            params["max_tokens_to_sample"] =  512


        # probably can just update to streaming = false as we don't want UI to control this aspect.
        return Bedrock(
            client=bedrock,
            model_id=self.model_id,
            model_kwargs=params,
            streaming=model_kwargs.get("streaming", False),
            callbacks=[self.callback_handler],
        )

    def get_prompt(self):
        template = """
Human: You are eCISO, a digital cybersecurity assistant specialized in version 1.1 of the NIST Cybersecurity Framework. Your primary mission is to interactively engage with a user, representing an institution, and evaluate their cybersecurity measures according to the NIST framework's five functions: Identify, Protect, Detect, Respond, and Recover.

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

Human: {input} 

Assistant:"""


        input_variables = ["input", "chat_history"]
        prompt_template_args = {
            "chat_history": "{chat_history}",
            "input_variables": input_variables,
            "template": template,
        }
        prompt_template = PromptTemplate(**prompt_template_args)

        
        return prompt_template

    def get_memory(self, output_key=None, return_messages=False):
        return EcisoConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=self.chat_history,
            return_messages=return_messages,
            output_key=output_key,
        )

class EcisoConversationBufferMemory(ConversationBufferMemory):
    @property
    def buffer_as_str(self) -> str:
        return self.get_buffer_string()

    def get_buffer_string(self) -> str:
        """modified version of https://github.com/langchain-ai/langchain/blob/bed06a4f4ab802bedb3533021da920c05a736810/libs/langchain/langchain/schema/messages.py#L14"""
        human_message_cnt = 0
        string_messages = []
        for m in self.chat_memory.messages:
            if isinstance(m, HumanMessage):
                if human_message_cnt == 0:
                    message = f"{m.content}"
                else:
                    message = f"Human: {m.content}"
                human_message_cnt += 1
            elif isinstance(m, AIMessage):
                message = f"Assistant: {self.extract_response(m.content)}"
            else:
                raise ValueError(f"Got unsupported message type: {m}")
            string_messages.append(message)

        return "".join(string_messages)
    def extract_response(self,text):
        # Extract content between <Response> and </Response> tags   
        response_contents = []
        start_idx = text.find("<Response>")
        while start_idx != -1:
            end_idx = text.find("</Response>", start_idx)
            if end_idx == -1:
                break
            response_contents.append(text[start_idx + 10 : end_idx])
            start_idx = text.find("<Response>", end_idx)

        # Extract content not enclosed in any XML tags only if no <Response> content found
        if not response_contents:
            outside_xml_content = []
            prev_end_idx = 0
            while prev_end_idx < len(text):
                start_idx = text.find("<", prev_end_idx)
                if start_idx == -1:
                    outside_xml_content.append(text[prev_end_idx:].strip())
                    break
                elif start_idx > prev_end_idx:
                    outside_xml_content.append(text[prev_end_idx:start_idx].strip())
                end_idx = text.find(">", start_idx)
                prev_end_idx = end_idx + 1
            response_contents = outside_xml_content
        
        return ' '.join(response_contents)


# Register the adapter
registry.register(r"^eciso.anthropic.claude*", EcisoAdapter)
