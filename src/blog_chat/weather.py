import asyncio
import re
from typing import Any

from cachetools import TTLCache

weather_cache: TTLCache[str, str] = TTLCache(maxsize=1000, ttl=3600)


async def fetch_weather_by_ip(ip_address: str) -> str | None:
    if not ip_address or ip_address in ("127.0.0.1", "::1", "localhost"):
        return None

    if ip_address in weather_cache:
        return weather_cache[ip_address]

    try:
        city = await get_city_from_ip(ip_address)
        if not city:
            return None

        weather = await get_weather(city)
        if weather:
            weather_cache[ip_address] = weather
        return weather
    except Exception:
        return None


async def get_city_from_ip(ip_address: str) -> str | None:
    if ip_address.startswith("192.168.") or ip_address.startswith("10.") or ip_address.startswith("172."):
        return None

    try:
        async with asyncio.timeout(5):
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://ipapi.co/{ip_address}/json/")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("city")
    except Exception:
        return None
    return None


async def get_weather(city: str) -> str | None:
    try:
        async with asyncio.timeout(10):
            import httpx
            async with httpx.AsyncClient() as client:
                url = f"https://wttr.in/{city}?format=j1"
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    current = data.get("current_condition", [{}])[0]
                    temp = current.get("temp_C", "")
                    desc = current.get("weatherDesc", [{}])[0].get("value", "")
                    icon = get_weather_icon(desc)
                    return f"{icon} {temp}°C, {desc}"
    except Exception:
        return None
    return None


def get_weather_icon(description: str) -> str:
    desc_lower = description.lower()
    if "sun" in desc_lower or "clear" in desc_lower:
        return "☀️"
    elif "cloud" in desc_lower:
        return "☁️"
    elif "rain" in desc_lower:
        return "🌧️"
    elif "snow" in desc_lower:
        return "❄️"
    elif "thunder" in desc_lower:
        return "⛈️"
    elif "fog" in desc_lower or "mist" in desc_lower:
        return "🌫️"
    elif "overcast" in desc_lower:
        return "☁️"
    else:
        return "🌡️"
