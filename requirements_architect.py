#!/usr/bin/env python3
"""
Requirements Architect — AI-Native BA Tool
Transforms raw stakeholder transcripts OR regulatory documents into
structured technical specs with user stories, edge cases, and a developer critique.

Part of the Wealthsimple AI Builder application.

Usage:
    python execution/requirements_architect.py <input_file> [--output output.md]
    python execution/requirements_architect.py --regulation <regulation_file>
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")


# ──────────────────────────────────────────────
# Provider Discovery & Smart Fallback
# ──────────────────────────────────────────────

def get_available_providers():
    """Discover all available AI providers from .env keys.
    Returns list of (provider_name, api_key) tuples.
    Checks Anthropic first (best quality), then OpenAI, then Gemini.
    Skips placeholder keys like 'your_key_here'.
    """
    providers = []

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if api_key and not api_key.startswith("your_"):
        providers.append(("anthropic", api_key))

    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key and not api_key.startswith("your_"):
        providers.append(("openai", api_key))

    api_key = os.getenv("GOOGLE_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
    if api_key and not api_key.startswith("your_"):
        providers.append(("gemini", api_key))

    return providers


# ──────────────────────────────────────────────
# System Prompts (The "Directive" Layer)
# ──────────────────────────────────────────────

TRANSCRIPT_DIRECTIVE = """You are the AI-Native Requirement Architect, a system that replaces the 3-week requirements gathering bottleneck with a 3-minute structured spec.

You are built by a Senior BA with 5+ years of Agile delivery experience who understands that the gap between stakeholder intent and shipped code is where projects die.

Given a raw stakeholder transcript (meeting notes, Slack threads, or rambling voice memos), produce a COMPLETE technical specification with the following sections:

## 1. EXECUTIVE SUMMARY
One paragraph: what is being built and why. No jargon.

## 2. USER STORIES
Standard format: "As a [role], I want [capability], so that [business value]."
Include at minimum 3 user stories. Each must have:
- Acceptance criteria in GIVEN-WHEN-THEN format
- Priority tag: [P0-Critical] [P1-High] [P2-Medium] [P3-Low]

## 3. TECHNICAL CONSTRAINTS
Identify constraints specific to fintech/regulated environments:
- Security requirements (PII handling, encryption, auth)
- Regulatory requirements (CRA, OSFI, provincial regulations)
- Performance requirements (latency, throughput, availability SLA)
- Data requirements (storage, retention, audit trails)

## 4. EDGE CASES & FAILURE MODES
At minimum 5 edge cases. For each:
- Scenario description
- Expected system behavior
- Risk level: [Critical/High/Medium/Low]

## 5. DEVELOPER CRITIQUE
Act as a Senior Staff Engineer reviewing these requirements. Be blunt:
- Where are the requirements ambiguous?
- What's technically expensive that the stakeholder probably doesn't realize?
- What's missing that will cause a production incident?
- Suggest at least one simplification that delivers 80% of the value at 20% of the cost.

## 6. GHERKIN TEST SCENARIOS
Translate the top 3 user stories into executable Gherkin (BDD) test scenarios.

## 7. HUMAN DECISION GATE
Explicitly state ONE critical decision that MUST remain with a human product manager or compliance officer. Explain WHY this decision cannot be automated — what would go wrong if AI made it autonomously.

Be specific, opinionated, and practical. This spec should be usable by a development team tomorrow morning."""

REGULATION_DIRECTIVE = """You are the AI-Native Compliance Architect, a system that transforms dense regulatory documents into actionable engineering specs.

In fintech, the gap between "what the regulation says" and "what the code enforces" is where billion-dollar fines happen. Your job is to close that gap.

Given a regulatory document (or excerpt), produce:

## 1. PLAIN ENGLISH SUMMARY
What does this regulation actually require? No legalese. Write it so a junior developer understands.

## 2. LOGIC CONSTRAINTS
Extract every conditional rule as structured logic:
- IF [condition] THEN [requirement] ELSE [alternative]
- Include thresholds, limits, dates, and exceptions

## 3. USER STORIES (Compliance)
"As a [regulated entity], I must [requirement], so that [regulatory outcome]."
Include acceptance criteria in GIVEN-WHEN-THEN format.

## 4. PYTHON UNIT TESTS
Write actual executable Python unit tests (using pytest) that enforce the key regulatory rules. These should be copy-paste runnable.

## 5. RISK SUMMARY
For each major rule:
- What happens if we get this wrong? (fine amount, license risk, user harm)
- Risk level: [Critical/High/Medium/Low]
- Suggested audit frequency

## 6. EDGE CASES
At minimum 5 edge cases where the regulation is ambiguous or where real-world scenarios create conflicts.

## 7. HUMAN DECISION GATE
Explicitly state which compliance decisions MUST have human sign-off. In regulated fintech, this is non-negotiable. Explain what would break if AI made these decisions autonomously.

Be precise. Be opinionated. A compliance officer should be able to review this and say "yes, ship it." """


# ──────────────────────────────────────────────
# API Call + Smart Fallback
# ──────────────────────────────────────────────

def _call_provider(provider, api_key, system_prompt, user_input):
    """Call a single provider. Raises on failure."""
    if provider == "anthropic":
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_input}],
            temperature=0.2,
        )
        return response.content[0].text

    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content

    elif provider == "gemini":
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{system_prompt}\n\n---\n\nINPUT:\n{user_input}",
            config={"temperature": 0.2},
        )
        return response.text


def call_ai_with_fallback(providers, system_prompt, user_input):
    """Try each provider in order. If one fails (quota, auth, etc.), fall to next."""
    if not providers:
        print("❌ No API keys found in .env!")
        print("   Add at least one of: ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY")
        sys.exit(1)

    print(f"📡 {len(providers)} provider(s) available: {', '.join(p[0] for p in providers)}")

    for i, (provider, api_key) in enumerate(providers):
        try:
            label = f" ({i+1}/{len(providers)})" if len(providers) > 1 else ""
            print(f"🤖 Trying: {provider}{label}")
            result = _call_provider(provider, api_key, system_prompt, user_input)
            print(f"✅ Success via {provider}")
            return result
        except Exception as e:
            error_str = str(e).lower()
            is_quota = any(w in error_str for w in ["quota", "rate", "429", "limit", "exhausted", "exceeded"])
            is_auth = any(w in error_str for w in ["401", "403", "auth", "invalid", "permission", "unauthorized"])

            if is_quota:
                print(f"⚠️  {provider}: quota/rate limit hit — trying next...")
            elif is_auth:
                print(f"⚠️  {provider}: auth error — trying next...")
            else:
                print(f"⚠️  {provider}: {type(e).__name__}: {str(e)[:120]}")

            if i == len(providers) - 1:
                print(f"\n❌ All {len(providers)} providers failed.")
                print(f"   Last error: {e}")
                sys.exit(1)

    return None


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI-Native Requirement Architect — Transform transcripts and regulations into technical specs."
    )
    parser.add_argument("input_file", help="Path to transcript or regulation text file")
    parser.add_argument(
        "--regulation", "-r", action="store_true",
        help="Treat input as a regulatory document (generates compliance spec + unit tests)"
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output file path (default: <input>_spec.md)"
    )
    args = parser.parse_args()

    # Validate input
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ File not found: {input_path}")
        sys.exit(1)

    # Read input
    content = input_path.read_text()
    print(f"📄 Reading: {input_path.name} ({len(content):,} chars)")

    # Select directive
    directive = REGULATION_DIRECTIVE if args.regulation else TRANSCRIPT_DIRECTIVE
    mode = "regulation" if args.regulation else "transcript"
    print(f"📋 Mode: {mode}")
    print(f"🚀 Architecting requirements...\n")

    # Discover providers & call with fallback
    providers = get_available_providers()
    user_prompt = f"Here is the raw {'regulatory document' if args.regulation else 'stakeholder transcript'}:\n\n{content}"
    result = call_ai_with_fallback(providers, directive, user_prompt)

    # Write output
    if result:
        output_path = Path(args.output) if args.output else input_path.with_name(f"{input_path.stem}_spec.md")
        header = (
            f"# AI-Generated Technical Spec\n\n"
            f"> **Source:** {input_path.name}  \n"
            f"> **Mode:** {mode}  \n"
            f"> **Generated by:** Requirements Architect v1.0\n\n---\n\n"
        )
        output_path.write_text(header + result + "\n")
        print(f"\n📄 Spec saved: {output_path}")
        print(f"📊 Output: {len(result):,} chars")


if __name__ == "__main__":
    main()
