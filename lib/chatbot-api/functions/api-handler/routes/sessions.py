import genai_core.sessions
import genai_core.types
import genai_core.auth
import genai_core.utils.json
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.appsync import Router
import json

tracer = Tracer()
router = Router()
logger = Logger()


@router.resolver(field_name="listSessions")
@tracer.capture_method
def get_sessions():
    user_id = genai_core.auth.get_user_id(router)
    if user_id is None:
        raise genai_core.types.CommonError("User not found")

    sessions = genai_core.sessions.list_sessions_by_user_id(user_id)

    return [
        {
            "id": session.get("SessionId"),
            "title": session.get("History", [{}])[0]
            .get("data", {})
            .get("content", "<no title>"),
            "startTime": f'{session.get("StartTime")}Z',
        }
        for session in sessions
    ]



def extract_response(text):
    # edge case won't hit as this is an established session
    '''
    if(text.find( "You are eCISO, a digital cybersecurity assistant specialized in version 1.1 of the NIST Cybersecurity Framework. Your primary mission is to interactively engage with a user, representing an institution, and evaluate their cybersecurity measures according to the NIST framework's five functions: Identify, Protect, Detect, Respond, and Recover.") > -1 ):
        first_occurrence=text.find("<Response>")
        edge_override=text[first_occurrence+len("<Response>"):]
        text=edge_override
    '''

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


@router.resolver(field_name="getEcisoSession")
@tracer.capture_method
def get_session_eciso(id: str):
    user_id = genai_core.auth.get_user_id(router)
    if user_id is None:
        raise genai_core.types.CommonError("User not found")

    session = genai_core.sessions.get_session(id, user_id)
    if not session:
        return None

    return {
        "id": session.get("SessionId"),
        "title": session.get("History", [{}])[0]
        .get("data", {})
        .get("content", "<no title>"),
        "startTime": f'{session.get("StartTime")}Z',
        "history": [
            {
                "type": item.get("type"),
                "content": extract_response(item.get("data", {}).get("content")),
                "metadata": json.dumps(
                    item.get("data", {}).get("additional_kwargs"),
                    cls=genai_core.utils.json.CustomEncoder,
                ),
            }
            for item in session.get("History")
        ],
    }


@router.resolver(field_name="getSession")
@tracer.capture_method
def get_session(id: str):
    user_id = genai_core.auth.get_user_id(router)
    if user_id is None:
        raise genai_core.types.CommonError("User not found")

    session = genai_core.sessions.get_session(id, user_id)
    if not session:
        return None

    return {
        "id": session.get("SessionId"),
        "title": session.get("History", [{}])[0]
        .get("data", {})
        .get("content", "<no title>"),
        "startTime": f'{session.get("StartTime")}Z',
        "history": [
            {
                "type": item.get("type"),
                "content": item.get("data", {}).get("content"),
                "metadata": json.dumps(
                    item.get("data", {}).get("additional_kwargs"),
                    cls=genai_core.utils.json.CustomEncoder,
                ),
            }
            for item in session.get("History")
        ],
    }


@router.resolver(field_name="deleteUserSessions")
@tracer.capture_method
def delete_user_sessions():
    user_id = genai_core.auth.get_user_id(router)
    if user_id is None:
        raise genai_core.types.CommonError("User not found")

    result = genai_core.sessions.delete_user_sessions(user_id)

    return result


@router.resolver(field_name="deleteSession")
@tracer.capture_method
def delete_session(id: str):
    user_id = genai_core.auth.get_user_id(router)
    if user_id is None:
        raise genai_core.types.CommonError("User not found")

    result = genai_core.sessions.delete_session(id, user_id)

    return result
