import asyncio
import uuid

from google.adk.runners import InMemoryRunner
from google.genai import types

from global_kyc_agent.agent import root_agent


async def main():
    """Runs the Companies House agent."""
    print("Companies House Agent")
    print("--------------------")
    print("Enter your query below. Type 'exit' to quit.")

    APP_NAME = "companies_house_agent"
    USER_ID = "user_1"
    SESSION_ID = str(uuid.uuid4())

    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)

    await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    while True:
        try:
            query = await asyncio.to_thread(input, "> ")
            if query.lower() == "exit":
                break

            user_message = types.Content(
                role="user", parts=[types.Part.from_text(text=query)]
            )

            # async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=user_message):
            #     if event.is_final_response() and event.content:
            #         response = "".join(part.text for part in event.content.parts)
            #         print(f"Agent: {response}")
            async for event in runner.run_async(
                user_id=USER_ID, session_id=SESSION_ID, new_message=user_message
            ):
                if (
                    event.actions
                    and event.actions.state_delta
                    and event.actions.state_delta.get("final_message")
                ):
                    print(f"<<< Agent Response: {event.content}")
                    # You can uncomment the line below to see *all* events during execution
                    # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

                    # Key Concept: is_final_response() marks the concluding message for the turn.
                    if event.is_final_response():
                        break
            # print(f"<<< Agent Response: {final_response_text}")
        except (KeyboardInterrupt, EOFError):
            break


async def main_noinput():
    """Runs the Companies House agent."""
    print("Companies House Agent")
    print("--------------------")
    print("Enter your query below. Type 'exit' to quit.")

    APP_NAME = "companies_house_agent"
    USER_ID = "user_1"
    SESSION_ID = str(uuid.uuid4())

    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)

    await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    try:
        user_message = types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text="Create a report on London Stock Exchange Group"
                )
            ],
        )

        # async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=user_message):
        #     if event.is_final_response() and event.content:
        #         response = "".join(part.text for part in event.content.parts)
        #         print(f"Agent: {response}")
        final_response_text = None
        async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=user_message
        ):
            print(
                f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}"
            )

            if event.is_final_response() and event.content:
                if event.content.parts:
                    final_response_text = event.content.parts[0].text
                break
            elif (
                event.is_final_response()
                and event.actions
                and event.actions.escalate
            ):
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                break

        print(f"<<< Agent Response: {final_response_text}")
    except (KeyboardInterrupt, EOFError):
        pass


if __name__ == "__main__":
    asyncio.run(main_noinput())
