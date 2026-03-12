# n8n Workflow – News Aggregation Automation

## Overview
This workflow implements the automation layer for the News Aggregation project using **n8n**.  
It orchestrates the flow of data between news sources, AI processing, and user personalization.

## Workflow Purpose
The goal of this workflow is to automate the process of generating a personalized news newsletter.

The workflow simulates the integration between:
- News aggregation
- AI summarization
- User preference filtering
- Newsletter generation

## Workflow Steps

1. **Schedule Trigger**
   - Automatically starts the workflow at a scheduled time.

2. **Mock News Data**
   - Simulates news articles received from the backend aggregation service.

3. **Newsletter Generation (Function Node)**
   - Processes the news data and generates a formatted newsletter.

4. **User Preference**
   - Represents user interests stored in the system.

5. **Preference Matching (IF Node)**
   - Checks whether the news category matches the user’s preferred category.

6. **Final Output**
   - If the preference matches, the newsletter is prepared for delivery.

## Technologies Used
- n8n (Workflow Automation)
- JavaScript (Function Node logic)

## Role in the Project
This workflow acts as the **orchestration layer** of the system, connecting different components such as:
- News aggregation backend
- AI processing service
- User preference filtering
- Newsletter delivery pipeline

## File
`news-workflow.json` – Exported n8n workflow file.
