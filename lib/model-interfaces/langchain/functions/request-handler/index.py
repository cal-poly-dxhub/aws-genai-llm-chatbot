import os
import json
import uuid
from datetime import datetime
from adapters.registry import registry
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType
from aws_lambda_powertools.utilities.batch.exceptions import BatchProcessingError
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext

from genai_core.utils.websocket import send_to_client
from genai_core.types import ChatbotAction

from fpdf import FPDF
import markdown
import boto3
import hashlib


processor = BatchProcessor(event_type=EventType.SQS)
tracer = Tracer()
logger = Logger()

AWS_REGION = os.environ["AWS_REGION"]
API_KEYS_SECRETS_ARN = os.environ["API_KEYS_SECRETS_ARN"]

sequence_number = 0


def on_llm_new_token(
    user_id, session_id, self, token, run_id, *args, **kwargs
):
    global sequence_number
    sequence_number += 1
    run_id = str(run_id)

    send_to_client(
        {
            "type": "text",
            "action": ChatbotAction.LLM_NEW_TOKEN.value,
            "userId": user_id,
            "timestamp": str(int(round(datetime.now().timestamp()))),
            "data": {
                "sessionId": session_id,
                "token": {
                    "runId": run_id,
                    "sequenceNumber": sequence_number,
                    "value": token,
                },
            },
        }
    )


def handle_heartbeat(record):
    user_id = record["userId"]
    session_id = record["data"]["sessionId"]

    send_to_client(
        {
            "type": "text",
            "action": ChatbotAction.HEARTBEAT.value,
            "timestamp": str(int(round(datetime.now().timestamp()))),
            "userId": user_id,
            "data": {
                "sessionId": session_id,
            },
        }
    )



def extract_response(text):
    # edge case of first message

    if(text.find( "You are eCISO, a digital cybersecurity assistant specialized in version 1.1 of the NIST Cybersecurity Framework. Your primary mission is to interactively engage with a user, representing an institution, and evaluate their cybersecurity measures according to the NIST framework's five functions: Identify, Protect, Detect, Respond, and Recover.") > -1 ):
        first_occurrence=text.find("<Response>")
        edge_override=text[first_occurrence+len("<Response>"):]
        text=edge_override

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

class PDFGenerator(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'My eCISO Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page %s' % self.page_no(), 0, 0, 'C')


def handle_run(record):
    user_id = record["userId"]
    data = record["data"]
    provider = data["provider"]
    model_id = data["modelName"]
    mode = data["mode"]
    prompt = data["text"]
    workspace_id = data.get("workspaceId", None)
    session_id = data.get("sessionId")

    if not session_id:
        session_id = str(uuid.uuid4())

    adapter = registry.get_adapter(f"{provider}.{model_id}")

    adapter.on_llm_new_token = lambda *args, **kwargs: on_llm_new_token(
        user_id, session_id, *args, **kwargs
    )

    model = adapter(
        model_id=model_id,
        mode=mode,
        session_id=session_id,
        user_id=user_id,
        model_kwargs=data.get("modelKwargs", {}),
    )

    response = model.run(
        prompt=prompt,
        workspace_id=workspace_id,
    )

    
    # eCiso override to strip xml tags
    if( provider == 'eciso'):
        #logger.info("~~~~~~~~~~~~~~~~~~~~~~~~")
        #logger.info(response["content"])
        #logger.info("------------------------")
        override = extract_response(response["content"])
        #logger.info(override)
        #logger.info("~~~~~~~~~~~~~~~~~~~~~~~~")
        
        response["content"]=override
        #logger.info(response)
    
    # eciso override for pdf generation
    if( provider == 'ecisopdf'):
        s3_client = boto3.client('s3')
        bucket_name=os.environ["PLUGIN_ECISO_BUCKET_NAME"]
        
        sha256 = hashlib.sha256()
        sha256.update(response["content"].encode('utf-8'))
        unique_hash = sha256.hexdigest()
        
        #tmp file pdf path
        temp_file_path="/tmp/output.pdf"
        temp_file_name="output"+unique_hash+".pdf"
        # Create instance of FPDF class
        pdf = PDFGenerator()
        # Add a page
        pdf.add_page()
        # Set font
        #pdf.set_font("Arial", size=12)
        # Add content to the PDF
        # pdf.multi_cell(0, 10, response["content"])
        # markdown flag only support on fpdf2
        #pdf.multi_cell(0, 10, response["content"])
        # Save the PDF to a file
        html_output = markdown.markdown(response["content"])
        pdf.write_html(html_output)
        pdf.output(temp_file_path)

        # upload to s3
        s3_client.upload_file(temp_file_path, bucket_name, temp_file_name)
        # Clean up the temporary file
        os.remove(temp_file_path)
        # Generate a pre-signed URL for the uploaded file
        s3_presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': temp_file_name},
            ExpiresIn=3600  # Set the expiration time (in seconds)
        )
        #generate pdf and update last statement of response with presigned url
        response["content"] += "\n\nDownload report here: " + s3_presigned_url
    

    send_to_client(
        {
            "type": "text",
            "action": ChatbotAction.FINAL_RESPONSE.value,
            "timestamp": str(int(round(datetime.now().timestamp()))),
            "userId": user_id,
            "data": response,
        }
    )


@tracer.capture_method
def record_handler(record: SQSRecord):
    payload: str = record.body
    message: dict = json.loads(payload)
    detail: dict = json.loads(message["Message"])
    logger.info(detail)

    if detail["action"] == ChatbotAction.RUN.value:
        handle_run(detail)
    elif detail["action"] == ChatbotAction.HEARTBEAT.value:
        handle_heartbeat(detail)


def handle_failed_records(records):
    for triplet in records:
        status, error, record = triplet
        payload: str = record.body
        message: dict = json.loads(payload)
        detail: dict = json.loads(message["Message"])
        logger.info(detail)
        user_id = detail["userId"]
        data = detail.get("data", {})
        session_id = data.get("sessionId", "")

        send_to_client(
            {
                "type": "text",
                "action": "error",
                "direction": "OUT",
                "userId": user_id,
                "timestamp": str(int(round(datetime.now().timestamp()))),
                "data": {
                    "sessionId": session_id,
                    "content": str(error),
                    "type": "text",
                },
            }
        )


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def handler(event, context: LambdaContext):
    batch = event["Records"]

    api_keys = parameters.get_secret(API_KEYS_SECRETS_ARN, transform="json")
    for key in api_keys:
        os.environ[key] = api_keys[key]

    try:
        with processor(records=batch, handler=record_handler):
            processed_messages = processor.process()
    except BatchProcessingError as e:
        logger.error(e)

    logger.info(processed_messages)
    handle_failed_records(
        message for message in processed_messages if message[0] == "fail"
    )

    return processor.response()
