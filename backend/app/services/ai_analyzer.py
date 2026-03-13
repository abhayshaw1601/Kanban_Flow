"""
AI Task Analyzer Service
Integrates with Google Gemini AI for intelligent task analysis
"""

import os
import json
import google.generativeai as genai
from typing import Dict, List, Optional, Any
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

    async def analyze_diagram(self, image_base64: str, content_type: str) -> Dict[str, Any]:
        """
        Analyze architecture/flow diagram and convert to structured JSON format
        
        Args:
            image_base64: Base64 encoded image data
            content_type: MIME type of the image
            
        Returns:
            Structured JSON representation of the diagram
        """
        try:
            # Prepare the image for Gemini
            image_data = {
                "mime_type": content_type,
                "data": image_base64
            }
            
            # Create a comprehensive prompt for diagram analysis
            prompt = """
            Analyze this architecture or flow diagram and convert it into a structured JSON format.
            
            Please identify and extract:
            1. **Components/Services**: All boxes, services, modules, or components shown
            2. **Connections/Flow**: Arrows, lines, or connections between components
            3. **Data Flow**: Direction and type of data/information flow
            4. **Layers/Tiers**: Different architectural layers (presentation, business, data, etc.)
            5. **Technologies**: Any specific technologies, databases, or frameworks mentioned
            6. **External Systems**: Third-party services or external dependencies
            7. **User Interactions**: User touchpoints or interfaces
            
            Return a JSON structure with the following format:
            {
                "diagram_type": "architecture|flow|sequence|network|other",
                "title": "Inferred diagram title",
                "description": "Brief description of what the diagram represents",
                "components": [
                    {
                        "id": "unique_identifier",
                        "name": "Component Name",
                        "type": "service|database|ui|api|external|user|other",
                        "description": "What this component does",
                        "technology": "Technology stack if mentioned",
                        "layer": "presentation|business|data|infrastructure|other"
                    }
                ],
                "connections": [
                    {
                        "from": "source_component_id",
                        "to": "target_component_id",
                        "type": "api_call|data_flow|user_interaction|dependency|other",
                        "description": "What this connection represents",
                        "direction": "bidirectional|unidirectional",
                        "protocol": "HTTP|TCP|UDP|other|unknown"
                    }
                ],
                "data_flows": [
                    {
                        "name": "Data flow name",
                        "path": ["component1", "component2", "component3"],
                        "data_type": "user_data|system_data|configuration|other",
                        "description": "What data flows through this path"
                    }
                ],
                "layers": [
                    {
                        "name": "Layer name",
                        "components": ["component_ids_in_this_layer"],
                        "description": "Purpose of this layer"
                    }
                ],
                "external_dependencies": [
                    {
                        "name": "External service name",
                        "type": "api|database|service|cdn|other",
                        "description": "What this external dependency provides"
                    }
                ],
                "project_breakdown": {
                    "suggested_tasks": [
                        {
                            "title": "Task title",
                            "description": "Detailed task description",
                            "component": "related_component_id",
                            "priority": "high|medium|low",
                            "estimated_effort": "hours|days|weeks",
                            "dependencies": ["other_task_titles"]
                        }
                    ],
                    "development_phases": [
                        {
                            "phase": "Phase name",
                            "tasks": ["task_titles_in_this_phase"],
                            "description": "What gets accomplished in this phase"
                        }
                    ]
                }
            }
            
            Be thorough and extract as much meaningful information as possible from the diagram.
            If certain information is not visible or unclear, use "unknown" or "not_specified".
            Focus on creating actionable project tasks that could be derived from this architecture.
            """
            
            # Make the API call to Gemini
            response = self.model.generate_content([prompt, image_data])
            
            if not response or not response.text:
                raise Exception("No response from Gemini API")
            
            # Clean and parse the JSON response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            import json
            try:
                analysis_result = json.loads(response_text)
            except json.JSONDecodeError as e:
                # If JSON parsing fails, return a structured error with the raw response
                print(f"JSON parsing failed: {e}")
                print(f"Raw response: {response_text}")
                analysis_result = {
                    "error": "Failed to parse AI response as JSON",
                    "raw_response": response_text,
                    "parsing_error": str(e)
                }
            
            return analysis_result
            
        except Exception as e:
            print(f"Error in diagram analysis: {e}")
            raise Exception(f"Diagram analysis failed: {str(e)}")

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