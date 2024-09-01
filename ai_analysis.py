import google.generativeai as genai
import json
from json_repair import repair_json
import pandas as pd
import asyncio
import streamlit as st
from utils import clean_response

# --- Load API Key from Secrets ---
api_key = st.secrets["api_keys"]["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

def generate_prompt(text):
    return f"""
    ## Marketing Brief Analysis Request

    Please analyze the following marketing brief and provide a structured response suitable for Python processing, with scores as numbers out of 100. 
    Extract specific details and insights where possible.

    **Marketing Brief Text:**

    ```
    {text}
    ```

    **Response Format:**

    ```json
    {{
      "overall_score": {{score}},
      "breakdown": {{
        "focus_clarity": {{
          "score": {{score}},
          "feedback": "{{feedback}}",
          "extracted_objectives": ["list of extracted objectives from the text"], 
          "keywords": ["list of relevant keywords"]
        }},
        "strategic_alignment": {{
          "score": {{score}},
          "feedback": "{{feedback}}",
          "alignment_issues": ["list of potential misalignments with business goals (if any)"]
        }},
        "target_audience": {{
          "score": {{score}},
          "feedback": "{{feedback}}",
          "extracted_demographics": ["age", "location", "interests", "other relevant demographics"],
          "target_audience_examples": ["specific examples of the target audience mentioned in the text"]
        }},
        "competitive_landscape": {{
          "score": {{score}},
          "feedback": "{{feedback}}",
          "competitors_mentioned": ["list of competitor brands mentioned"],
          "competitive_advantages": ["list of mentioned or implied competitive advantages"]
        }},
        "channel_strategy": {{
          "score": {{score}},
          "feedback": "{{feedback}}",
          "recommended_channels": ["list of potentially effective channels based on the brief"],
          "channel_justifications": ["reasons for recommending each channel"]
        }},
        "measurement_kpis": {{
          "score": {{score}},
          "feedback": "{{feedback}}",
          "extracted_kpis": ["list of KPIs mentioned in the brief"],
          "kpi_suggestions": ["suggestions for additional relevant KPIs"]
        }}
      }},
      "gap_analysis": [
            "List of missing elements (if any)",
            "Another missing element"
        ]
    }}
    """

async def analyze_text_async(text):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, analyze_text, text)
    return result

def analyze_text(text):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = generate_prompt(text)

    try:
        response = model.generate_content(prompt)
        response_text = response.text

        # --- Clean up the response ---
        response_text = clean_response(response_text)

        # --- Repair potentially malformed JSON ---
        try:
            response_text = repair_json(response_text)
        except Exception as e:
            print(f"Warning: json_repair could not fix the JSON: {e}")

        # Directly try to parse as JSON
        response_data = json.loads(response_text)

        # Extract data for DataFrame (corrected structure)
        data = {}

        for category, details in response_data['breakdown'].items():
            category_title = category.replace('_', ' ').title()
            
            # Store all details for the category in a dictionary
            data[category_title] = {
                'Score': int(details['score']),
                'Feedback': details['feedback'],
                'Extracted Objectives': details.get('extracted_objectives', []),
                'Keywords': details.get('keywords', []),
                'Alignment Issues': details.get('alignment_issues', []),
                'Extracted Demographics': details.get('extracted_demographics', []),
                'Target Audience Examples': details.get('target_audience_examples', []),
                'Competitors Mentioned': details.get('competitors_mentioned', []),
                'Competitive Advantages': details.get('competitive_advantages', []),
                'Recommended Channels': details.get('recommended_channels', []),
                'Channel Justifications': details.get('channel_justifications', []),
                'Extracted KPIs': details.get('extracted_kpis', []),
                'KPI Suggestions': details.get('kpi_suggestions', []),
                'Target Locations': details.get('target_locations', [])  # Add target locations extraction
            } 

        df_results = pd.DataFrame.from_dict(data, orient='index')
        overall_score = int(response_data['overall_score'])

        # Extract gap analysis results
        gap_analysis_results = response_data.get('gap_analysis', [])

        # Extract competitors mentioned
        competitors_mentioned = data['Competitive Landscape']['Competitors Mentioned']

        return df_results, overall_score, gap_analysis_results, competitors_mentioned 
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw response: {response.text}")
        return None, None, None, []

def rewrite_brief(original_text, df_results):
    """Generates an improved marketing brief using Google Gemini."""

    # Construct a prompt incorporating feedback from the analysis
    prompt = f"""
    ## Marketing Brief Rewriter

    Here's an original marketing brief:
    ```
    {original_text}
    ```

    Based on an analysis, here are some areas for improvement:
    """
    suggestions = {}
    from_to_quotes = {}

    for category, details in df_results.iterrows():
        prompt += f"**{category.title()}:** {details['Feedback']}\n"
        
        # Generate suggestions based on missing elements
        if category == 'Competitive Landscape' and not details['Competitors Mentioned']:
            competitors = ["Competitor A", "Competitor B", "Competitor C"]
            suggestions[category] = f"Consider adding relevant competitors such as {', '.join(competitors)} to better understand the competitive landscape."
            from_to_quotes[category] = {
                "from": "No competitors mentioned.",
                "to": f"Added relevant competitors such as {', '.join(competitors)}."
            }
            prompt += f"Add relevant competitors such as {', '.join(competitors)}.\n"
        elif category == 'Target Audience' and not details['Extracted Demographics']:
            demographics = ["age 25-34", "gender: female", "location: New York", "interests: fitness, wellness"]
            suggestions[category] = f"Specify target demographics such as {', '.join(demographics)} to tailor your strategy effectively."
            from_to_quotes[category] = {
                "from": "No target demographics specified.",
                "to": f"Included target demographics such as {', '.join(demographics)}."
            }
            prompt += f"Include target demographics such as {', '.join(demographics)}.\n"
        elif category == 'Channel Strategy' and not details['Recommended Channels']:
            channels = ["social media", "email marketing", "paid advertising"]
            suggestions[category] = f"Include recommended channels such as {', '.join(channels)} to reach your audience more effectively."
            from_to_quotes[category] = {
                "from": "No recommended channels mentioned.",
                "to": f"Recommended channels such as {', '.join(channels)}."
            }
            prompt += f"Recommend channels such as {', '.join(channels)}.\n"
        elif category == 'Measurement Kpis' and not details['Extracted KPIs']:
            kpis = ["conversion rate", "click-through rate", "customer acquisition cost"]
            suggestions[category] = f"Define specific KPIs such as {', '.join(kpis)} to measure the success of your campaign."
            from_to_quotes[category] = {
                "from": "No KPIs defined.",
                "to": f"Included KPIs such as {', '.join(kpis)}."
            }
            prompt += f"Include KPIs such as {', '.join(kpis)}.\n"
        else:
            # For other categories or if already specified, include general improvements
            from_to_quotes[category] = {
                "from": details['Feedback'],
                "to": f"Enhanced {category.lower()} based on feedback."
            }

    prompt += """
    Please rewrite the brief, addressing the feedback provided and making it as strong as possible. 
    Maintain the original core message and objectives. Use crisp and clear language, and ensure the brief is detailed, actionable, and relevant.
    """

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")  # Or your preferred Gemini model
    response = model.generate_content(prompt)
    
    # Debugging output
    print("Generated Prompt:", prompt)
    print("Suggestions:", suggestions)
    print("From-To Quotes:", from_to_quotes)

    return response.text, suggestions, from_to_quotes