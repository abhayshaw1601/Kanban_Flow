"""
AI Task Analyzer Service
Integrates with Google Gemini AI for intelligent task analysis
"""

import os
import json
import google.generativeai as genai
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.core.config import settings


class TaskAnalysis(BaseModel):
    """Structure for task analysis results"""
    technical_subtasks: List[str]
    acceptance_criteria: List[str]
    potential_blockers: List[str]
    estimated_complexity: str
    domain: str
    confidence_score: float


class AnalyzeTaskRequest(BaseModel):
    """Request model for task analysis"""
    prompt: str
    context: Optional[str] = None


class AITaskAnalyzer:
    """AI Assistant for analyzing vague prompts using Gemini AI"""
    
    def __init__(self):
        # Configure Gemini AI
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        self.system_prompt = """
You are an expert technical project manager and software architect. Your job is to analyze vague task descriptions and break them down into structured, actionable technical tasks.

For any given prompt, you must provide a JSON response with the following structure:
{
    "technical_subtasks": [3-5 specific technical sub-tasks],
    "acceptance_criteria": [3-5 clear acceptance criteria],
    "potential_blockers": [3-5 potential blockers or edge cases],
    "estimated_complexity": "low|medium|high",
    "domain": "frontend|backend|fullstack|devops|testing|security|mobile|data",
    "confidence_score": 0.0-1.0
}

Guidelines:
- Technical subtasks should be specific, actionable, and ordered logically
- Acceptance criteria should be measurable and testable
- Potential blockers should include technical challenges, dependencies, and edge cases
- Complexity should reflect scope, technical difficulty, and time investment
- Domain should be the primary technical area
- Confidence score should reflect how well you understand the requirements

Be practical and consider real-world development challenges.
"""

    async def analyze_prompt(self, request: AnalyzeTaskRequest) -> TaskAnalysis:
        """
        Analyze a vague prompt using Gemini AI and generate structured technical tasks
        
        Args:
            request: The analysis request with prompt and optional context
            
        Returns:
            TaskAnalysis object with structured breakdown
        """
        try:
            # Construct the full prompt
            full_prompt = f"{self.system_prompt}\n\n"
            if request.context:
                full_prompt += f"Context: {request.context}\n\n"
            full_prompt += f"Task to analyze: '{request.prompt}'\n\nProvide your analysis as valid JSON:"
            
            # Generate response using Gemini
            response = self.model.generate_content(full_prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Try to find JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            analysis_data = json.loads(json_text)
            
            # Validate and create TaskAnalysis object
            return TaskAnalysis(
                technical_subtasks=analysis_data.get('technical_subtasks', []),
                acceptance_criteria=analysis_data.get('acceptance_criteria', []),
                potential_blockers=analysis_data.get('potential_blockers', []),
                estimated_complexity=analysis_data.get('estimated_complexity', 'medium'),
                domain=analysis_data.get('domain', 'general'),
                confidence_score=analysis_data.get('confidence_score', 0.5)
            )
            
        except Exception as e:
            # Fallback to basic analysis if AI fails
            print(f"AI analysis failed: {e}. Using fallback analysis.")
            return self._fallback_analysis(request.prompt)

    def _fallback_analysis(self, prompt: str) -> TaskAnalysis:
        """Fallback analysis when AI fails"""
        return TaskAnalysis(
            technical_subtasks=[
                "Analyze requirements and define scope",
                "Design system architecture and components",
                "Implement core functionality",
                "Add error handling and validation",
                "Create tests and documentation"
            ],
            acceptance_criteria=[
                "All functionality works as specified",
                "Code passes quality checks",
                "Implementation follows best practices",
                "Tests provide adequate coverage"
            ],
            potential_blockers=[
                "Unclear or changing requirements",
                "Technical dependencies",
                "Integration challenges",
                "Performance constraints"
            ],
            estimated_complexity="medium",
            domain="general",
            confidence_score=0.3
        )

    def format_analysis_as_markdown(self, analysis: TaskAnalysis, original_title: str) -> str:
        """Format analysis results into markdown for task description"""
        markdown = f"""# {original_title}

## 🎯 AI Analysis Summary
- **Domain**: {analysis.domain.upper()}
- **Complexity**: {analysis.estimated_complexity.upper()}
- **Confidence**: {analysis.confidence_score:.1%}

## 📋 Technical Sub-Tasks
{chr(10).join(f"{i+1}. {task}" for i, task in enumerate(analysis.technical_subtasks))}

## ✅ Acceptance Criteria
{chr(10).join(f"{i+1}. {criteria}" for i, criteria in enumerate(analysis.acceptance_criteria))}

## ⚠️ Potential Blockers
{chr(10).join(f"{i+1}. {blocker}" for i, blocker in enumerate(analysis.potential_blockers))}

---
*Generated by AI Task Analyzer*"""

        return markdown

    async def check_health(self) -> bool:
        """Check if the AI service is healthy"""
        try:
            test_request = AnalyzeTaskRequest(prompt="test connection")
            await self.analyze_prompt(test_request)
            return True
        except Exception:
            return False


# Global instance
ai_analyzer = AITaskAnalyzer()