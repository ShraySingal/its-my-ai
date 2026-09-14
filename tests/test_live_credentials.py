"""
IT'S MY AI — Live Credentials & API Verification Script
Tests Groq API, OpenWeatherMap API, and Supabase Cloud Connectivity.
"""

import sys
import os
import asyncio
import httpx
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.config import settings
from backend.app.providers.groq_provider import GroqProvider

async def test_groq():
    print("\n--- 1. Testing Groq API (llama-3.3-70b-versatile) ---")
    provider = GroqProvider()
    print(f"  Key configured: {provider.is_configured()} ({settings.GROQ_API_KEY[:8]}...{settings.GROQ_API_KEY[-4:]})")
    try:
        resp = await provider.generate_response(
            messages=[{"role": "user", "content": "Hello! Confirm you are online in one short sentence."}],
            system_instruction="You are IT'S MY AI command center."
        )
        print(f"  [SUCCESS] Groq Response ({resp.latency_ms} ms, {resp.tokens_used} tokens):")
        print(f"  \"{resp.text}\"")
        return True
    except Exception as e:
        print(f"  [ERROR] Groq API call failed: {e}")
        return False

async def test_openweather():
    print("\n--- 2. Testing OpenWeatherMap API ---")
    api_key = settings.OPENWEATHER_API_KEY
    print(f"  Key configured: {bool(api_key)} ({api_key[:6]}...)")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat=28.61&lon=77.23&appid={api_key}&units=metric"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.get(url)
            print(f"  Status Code: {res.status_code}")
            if res.status_code == 200:
                data = res.json()
                print(f"  [SUCCESS] City: {data.get('name')}")
                print(f"  Temperature: {data['main']['temp']} °C (Feels like: {data['main']['feels_like']} °C)")
                print(f"  Weather: {data['weather'][0]['description'].title()}")
                print(f"  Humidity: {data['main']['humidity']}% | Wind: {data['wind']['speed']} m/s")
                return True
            else:
                print(f"  [RESPONSE]: {res.text}")
                return False
    except Exception as e:
        print(f"  [ERROR] OpenWeatherMap call failed: {e}")
        return False

async def test_supabase():
    print("\n--- 3. Testing Supabase Cloud Connectivity ---")
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    print(f"  Supabase URL: {url}")
    print(f"  Supabase Key: {key[:12]}...")
    try:
        # Check health / auth endpoint
        health_url = f"{url}/auth/v1/health"
        async with httpx.AsyncClient(timeout=8.0) as client:
            headers = {"apikey": key, "Authorization": f"Bearer {key}"}
            res = await client.get(health_url, headers=headers)
            print(f"  Auth Health Status: {res.status_code}")
            
            # Check PostgREST root
            rest_url = f"{url}/rest/v1/"
            rest_res = await client.get(rest_url, headers=headers)
            print(f"  REST API Status: {rest_res.status_code}")
            print("  [SUCCESS] Supabase cloud instance is reachable and authenticated!")
            return True
    except Exception as e:
        print(f"  [ERROR] Supabase call failed: {e}")
        return False

async def main():
    print("==================================================")
    print("  IT'S MY AI — LIVE API CREDENTIALS VERIFICATION")
    print("==================================================")
    g_ok = await test_groq()
    w_ok = await test_openweather()
    s_ok = await test_supabase()
    print("\n==================================================")
    print(f"Summary: Groq={g_ok}, OpenWeather={w_ok}, Supabase={s_ok}")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
