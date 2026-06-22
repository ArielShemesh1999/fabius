import asyncio
import base64
import json
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.genai.types import (
    Blob,
    Content,
    Part,
)
from starlette.websockets import WebSocketDisconnect

from example_agent.agent import root_agent

load_dotenv()


async def start_agent_session(user_id: str):
    """Starts an agent session"""

    # Create a Runner
    runner = InMemoryRunner(app_name=os.getenv("APP_NAME"), agent=root_agent)

    # Create a Session
    session = await runner.session_service.create_session(
        app_name=os.getenv("APP_NAME"),
        user_id=user_id,
    )

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Setup RunConfig
    run_config = RunConfig(
        streaming_mode="bidi",
        session_resumption=types.SessionResumptionConfig(transparent=True),
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(
                start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_LOW,
                end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
                prefix_padding_ms=0,
                silence_duration_ms=0,
            )
        ),
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=os.getenv("AGENT_VOICE")
                )
            ),
            language_code=os.getenv("AGENT_LANGUAGE"),
        ),
        output_audio_transcription={},
        input_audio_transcription={},
    )

    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue


async def agent_to_client_messaging(websocket: WebSocket, live_events):
    """Agent to client communication: Sends structured event data."""
    async for event in live_events:
        try:
            message_to_send = {
                "author": event.author or "agent",
                "is_partial": event.partial or False,
                "turn_complete": event.turn_complete or False,
                "interrupted": event.interrupted or False,
                "parts": [],
                "input_transcription": None,
                "output_transcription": None,
            }

            if not event.content:
                if (
                    message_to_send["turn_complete"]
                    or message_to_send["interrupted"]
                ):
                    await websocket.send_text(json.dumps(message_to_send))
                continue

            transcription_text = "".join(
                part.text for part in event.content.parts if part.text
            )

            if hasattr(event.content, "role") and event.content.role == "user":
                if transcription_text:
                    message_to_send["input_transcription"] = {
                        "text": transcription_text,
                        "is_final": not event.partial,
                    }

            elif (
                hasattr(event.content, "role") and event.content.role == "model"
            ):
                if transcription_text:
                    message_to_send["output_transcription"] = {
                        "text": transcription_text,
                        "is_final": not event.partial,
                    }
                    message_to_send["parts"].append(
                        {"type": "text", "data": transcription_text}
                    )

                for part in event.content.parts:
                    if (
                        part.inline_data
                        and part.inline_data.mime_type.startswith("audio/pcm")
                    ):
                        audio_data = part.inline_data.data
                        encoded_audio = base64.b64encode(audio_data).decode(
                            "ascii"
                        )
                        message_to_send["parts"].append(
                            {"type": "audio/pcm", "data": encoded_audio}
                        )

                    elif part.function_call:
                        message_to_send["parts"].append(
                            {
                                "type": "function_call",
                                "data": {
                                    "name": part.function_call.name,
                                    "args": part.function_call.args or {},
                                },
                            }
                        )

                    elif part.function_response:
                        message_to_send["parts"].append(
                            {
                                "type": "function_response",
                                "data": {
                                    "name": part.function_response.name,
                                    "response": part.function_response.response
                                    or {},
                                },
                            }
                        )

            if (
                message_to_send["parts"]
                or message_to_send["turn_complete"]
                or message_to_send["interrupted"]
                or message_to_send["input_transcription"]
                or message_to_send["output_transcription"]
            ):
                await websocket.send_text(json.dumps(message_to_send))

        except Exception as e:
            logging.error(f"Error in agent_to_client_messaging: {e}")


async def client_to_agent_messaging(
    websocket: WebSocket, live_request_queue: LiveRequestQueue
):
    """Client to agent communication"""
    while True:
        try:
            message_json = await websocket.receive_text()
            message = json.loads(message_json)
            mime_type = message["mime_type"]

            if mime_type == "text/plain":
                data = message["data"]
                content = Content(
                    role="user", parts=[Part.from_text(text=data)]
                )
                live_request_queue.send_content(content=content)

            elif mime_type == "audio/pcm":
                data = message["data"]
                decoded_data = base64.b64decode(data)
                live_request_queue.send_realtime(
                    Blob(data=decoded_data, mime_type=mime_type)
                )

            elif mime_type == "image/jpeg":
                data = message["data"]
                decoded_data = base64.b64decode(data)
                live_request_queue.send_realtime(
                    Blob(data=decoded_data, mime_type=mime_type)
                )

            else:
                logging.warning(f"Mime type not supported: {mime_type}")

        except WebSocketDisconnect:
            logging.info("Client disconnected (WebSocketDisconnect).")
            break

        except Exception as e:
            logging.error(
                f"An error occurred in client_to_agent_messaging: {e}"
            )


app = FastAPI()


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """Client websocket endpoint"""

    # Wait for client connection
    await websocket.accept()

    # Start agent session
    user_id_str = str(user_id)
    live_events, live_request_queue = await start_agent_session(user_id_str)

    # Start tasks
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )

    # Wait until the websocket is disconnected or an error occurs
    tasks = [agent_to_client_task, client_to_agent_task]
    await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    # Close LiveRequestQueue
    live_request_queue.close()
    print(f"Client #{user_id} disconnected")
