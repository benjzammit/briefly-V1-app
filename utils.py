def clean_response(response_text):
    """Cleans up the response text before JSON parsing."""
    # 1. Remove leading/trailing whitespace:
    response_text = response_text.strip()

    # 2. Remove backticks (if present):
    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "")

    # 3. Remove potential BOM (Byte Order Mark) characters:
    response_text = response_text.encode("utf-8", "ignore").decode("utf-8")

    return response_text

def parse_and_improve(df, overall_score):
    improvement_areas = {}

    for category, row in df.iterrows():
        improvement_areas[category] = {
            "Suggestions": [],
            "Examples": []
        }

        if category == 'Focus & Clarity':
            if row['Extracted Objectives']:
                improvement_areas[category]["Suggestions"].append(
                    f"Consider refining the following objectives to ensure they are clear, measurable, and ambitious: {', '.join(row['Extracted Objectives'])}"
                )
            else:
                improvement_areas[category]["Suggestions"].append(
                    "Clearly define specific, measurable, achievable, relevant, and time-bound (SMART) objectives for the campaign."
                )

            if row['Keywords']:
                improvement_areas[category]["Suggestions"].append(
                    f"Ensure these keywords are strategically and consistently incorporated throughout the marketing materials to enhance visibility, searchability, and reach: {', '.join(row['Keywords'])}"
                )

        elif category == 'Strategic Alignment':
            if row['Alignment Issues']:
                improvement_areas[category]["Suggestions"].append(
                    f"Carefully review and address the following potential misalignments with overall business goals to ensure the campaign effectively contributes to key strategic priorities: {', '.join(row['Alignment Issues'])}"
                )
            else:
                improvement_areas[category]["Suggestions"].append(
                    "Clearly articulate how the campaign directly aligns with and supports the company's overall marketing and business objectives. Provide specific examples to demonstrate the connection."
                )

        elif category == 'Target Audience':
            if row['Extracted Demographics'] or row['Target Audience Examples']:
                if row['Extracted Demographics']:
                    demographics_str = ', '.join(row['Extracted Demographics'])
                    improvement_areas[category]["Suggestions"].append(
                        f"Refine targeting by providing more specific information about the desired audience. Consider these extracted demographics: {demographics_str}"
                    )
                if row['Target Audience Examples']:
                    examples_str = ', '.join(row['Target Audience Examples'])
                    improvement_areas[category]["Suggestions"].append(
                        f"While '{examples_str}' provides a starting point, explore and define the target audience more comprehensively. Include demographics, psychographics, behaviors, and needs."
                    )
            else:
                improvement_areas[category]["Suggestions"].append(
                    "Define a specific target audience by considering demographics, psychographics, behaviors, and needs. Avoid overly broad descriptions."
                )

        elif category == 'Competitive Landscape':
            if row['Competitors Mentioned']:
                improvement_areas[category]["Suggestions"].append(
                    f"Conduct a thorough analysis of these competitors to identify opportunities for differentiation and develop effective competitive strategies: {', '.join(row['Competitors Mentioned'])}"
                )
            else:
                improvement_areas[category]["Suggestions"].append(
                    "Research and identify key competitors. Analyze their strengths, weaknesses, target audience, and marketing strategies. Use this information to differentiate your offering and highlight its unique value proposition."
                )

            if row['Competitive Advantages']:
                improvement_areas[category]["Suggestions"].append(
                    f"Clearly and compellingly highlight these competitive advantages in your messaging and positioning to stand out in the market: {', '.join(row['Competitive Advantages'])}"
                )
            else:
                improvement_areas[category]["Suggestions"].append(
                        "Identify and clearly articulate your competitive advantages. What makes your product/service stand out from the competition? Highlight these advantages in your messaging."
                    )

        elif category == 'Channel Strategy':
            if row['Recommended Channels']:
                improvement_areas[category]["Suggestions"].append(
                    f"Evaluate the suitability of these channels for your target audience and campaign objectives: {', '.join(row['Recommended Channels'])}"
                )
            else:
                improvement_areas[category]["Suggestions"].append(
                    "Develop a comprehensive channel strategy that outlines the specific channels to be used (e.g., social media, email, paid advertising, content marketing). Justify the selection of each channel based on its relevance to the target audience and campaign goals."
                )

            # Instead of just listing justifications, integrate them into the channel suggestions
            if row['Channel Justifications']:
                for i, justification in enumerate(row['Channel Justifications']):
                    if i < len(row['Recommended Channels']):
                        channel = row['Recommended Channels'][i]
                        improvement_areas[category]["Suggestions"].append(f" - **{channel}:** {justification}")

        elif category == 'Measurement & KPIs':
            if row['Extracted KPIs']:
                improvement_areas[category]["Suggestions"].append(
                    f"Establish a system for consistently tracking and measuring these KPIs to evaluate campaign performance and make data-driven adjustments: {', '.join(row['Extracted KPIs'])}"
                )
            else:
                improvement_areas[category]["Suggestions"].append(
                    "Define specific and measurable KPIs to track the success of your campaign. Consider metrics related to your objectives, such as website traffic, lead generation, sales conversions, brand awareness, or customer satisfaction."
                )

            if row['KPI Suggestions']:
                improvement_areas[category]["Suggestions"].extend(
                    [f"- Consider tracking {suggestion} to gain additional insights into campaign effectiveness." for suggestion in row['KPI Suggestions']]
                )

    return improvement_areas