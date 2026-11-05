import os
from typing import Any

def generate_seo(topic: str, keywords: list[str] | None = None) -> dict[str, Any]:
    """Generate English YouTube metadata; uses OpenAI when configured, else a safe template."""
    keywords = [k.strip() for k in (keywords or []) if k.strip()]
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            response = client.chat.completions.create(
                model=model,
                temperature=0.7,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": (
                        "Create accurate, family-friendly YouTube metadata in English. "
                        "Do not use misleading claims, keyword stuffing, or imply the video "
                        "is educational or suitable for all ages unless the topic supports it. "
                        "Return JSON with title, description, and tags (array of strings)."
                    )},
                    {"role": "user", "content": (
                        f"Video topic: {topic}\nSuggested keywords: {', '.join(keywords)}"
                    )},
                ],
            )
            import json
            data = json.loads(response.choices[0].message.content or "{}")
            return {
                "title": str(data.get("title") or topic)[:100],
                "description": str(data.get("description") or topic)[:5000],
                "tags": [str(t)[:30] for t in data.get("tags", [])[:15]],
            }
        except Exception:
            # Fall back to deterministic metadata if the AI service is unavailable.
            pass

    title = topic.strip()[:90]
    description = (
        f"{topic.strip()}\n\n"
        "Thanks for watching! Please enjoy this story or video with your family.\n"
        "#KidsContent #FamilyFriendly"
    )
    tags = list(dict.fromkeys((keywords + ["kids content", "family friendly", "children's video"])))[:15]
    return {"title": title, "description": description[:5000], "tags": tags}
