#!/usr/bin/env python3
"""Test KaggleBot with real competition - full pipeline."""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.orchestrator import orchestrator_agent


async def test_santander():
    session_service = InMemorySessionService()
    runner = Runner(
        agent=orchestrator_agent,
        app_name='test',
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name='test',
        user_id='test_user',
    )

    print("=" * 60)
    print("TEST: Santander Customer Transaction Prediction")
    print("=" * 60)

    # Send the request
    content = types.Content(
        role='user',
        parts=[types.Part(text='Analyze the competition at https://www.kaggle.com/competitions/santander-customer-transaction-prediction. Run the full pipeline: scrape, profile data, generate strategies, and generate code.')]
    )

    all_responses = []
    async for event in runner.run_async(
        user_id='test_user',
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    author = event.author or 'unknown'
                    print(f"\n{'='*40}")
                    print(f"AGENT: {author}")
                    print(f"{'='*40}")
                    # Print first 500 chars
                    print(part.text[:500])
                    if len(part.text) > 500:
                        print(f"... ({len(part.text)} chars)")
                    all_responses.append(author)

    print(f"\n{'='*60}")
    print(f"Pipeline agents that responded: {all_responses}")
    print(f"Total responses: {len(all_responses)}")
    print(f"{'='*60}")


async def test_home_credit():
    session_service = InMemorySessionService()
    runner = Runner(
        agent=orchestrator_agent,
        app_name='test2',
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name='test2',
        user_id='test_user',
    )

    print("\n" + "=" * 60)
    print("TEST 2: Home Credit Default Risk")
    print("=" * 60)

    content = types.Content(
        role='user',
        parts=[types.Part(text='Analyze https://www.kaggle.com/competitions/home-credit-default-risk. Run the full pipeline.')]
    )

    all_responses = []
    async for event in runner.run_async(
        user_id='test_user',
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    author = event.author or 'unknown'
                    print(f"\n--- [{author}] ---")
                    print(part.text[:500])
                    if len(part.text) > 500:
                        print(f"... ({len(part.text)} chars)")
                    all_responses.append(author)

    print(f"\nAgents: {all_responses}")


if __name__ == "__main__":
    asyncio.run(test_santander())
    asyncio.run(test_home_credit())
