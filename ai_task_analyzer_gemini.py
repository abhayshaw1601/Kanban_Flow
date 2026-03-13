#!/usr/bin/env python3
"""
AI Task Analyzer - Converts vague prompts into structured technical tasks using Gemini AI
"""

import os
import json
import google.generativeai as genai
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class TaskAnalysis:
    """Structure for task analysis results"""
    technical_subtasks: List[str]
    acceptance_criteria: List[str]
    potential_blockers: List[str]
    estimated_complexity: str
    domain: str
    confidence_score: float


class AITaskAnalyzer:
    """AI Assistant for analyzing vague prompts using Gemini AI"""
    
    def __init__(self):
        # Configure Gemini AI
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
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

    def analyze_prompt(self, prompt: str) -> TaskAnalysis:
        """
        Analyze a vague prompt using Gemini AI and generate structured technical tasks
        
        Args:
            prompt: The user's vague task description
            
        Returns:
            TaskAnalysis object with structured breakdown
        """
        try:
            # Construct the full prompt
            full_prompt = f"{self.system_prompt}\n\nTask to analyze: '{prompt}'\n\nProvide your analysis as valid JSON:"
            
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
            return self._fallback_analysis(prompt)

    def _fallback_analysis(self, prompt: str) -> TaskAnalysis:
        """Fallback analysis when AI fails"""
        return TaskAnalysis(
            technical_subtasks=[
                "Analyze requirements and define scope",
                "Design system architecture",
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

    def format_output(self, analysis: TaskAnalysis) -> str:
        """Format the analysis results for display"""
        output = []
        output.append("=== AI TASK ANALYSIS ===\n")
        
        output.append(f"🎯 Domain: {analysis.domain.upper()}")
        output.append(f"📊 Complexity: {analysis.estimated_complexity.upper()}")
        output.append(f"🎲 Confidence: {analysis.confidence_score:.1%}\n")
        
        output.append("📋 TECHNICAL SUB-TASKS:")
        for i, task in enumerate(analysis.technical_subtasks, 1):
            output.append(f"  {i}. {task}")
        output.append("")
        
        output.append("✅ ACCEPTANCE CRITERIA:")
        for i, criteria in enumerate(analysis.acceptance_criteria, 1):
            output.append(f"  {i}. {criteria}")
        output.append("")
        
        output.append("⚠️  POTENTIAL BLOCKERS:")
        for i, blocker in enumerate(analysis.potential_blockers, 1):
            output.append(f"  {i}. {blocker}")
        
        return "\n".join(output)

    def analyze_with_context(self, prompt: str, context: str = "") -> TaskAnalysis:
        """
        Analyze prompt with additional context about the project
        
        Args:
            prompt: The task description
            context: Additional context (tech stack, project type, etc.)
            
        Returns:
            TaskAnalysis with context-aware recommendations
        """
        contextual_prompt = f"""
{self.system_prompt}

Additional Context: {context}

Task to analyze: '{prompt}'

Consider the provided context when generating your analysis. Provide your analysis as valid JSON:
"""
        
        try:
            response = self.model.generate_content(contextual_prompt)
            response_text = response.text.strip()
            
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            analysis_data = json.loads(json_text)
            
            return TaskAnalysis(
                technical_subtasks=analysis_data.get('technical_subtasks', []),
                acceptance_criteria=analysis_data.get('acceptance_criteria', []),
                potential_blockers=analysis_data.get('potential_blockers', []),
                estimated_complexity=analysis_data.get('estimated_complexity', 'medium'),
                domain=analysis_data.get('domain', 'general'),
                confidence_score=analysis_data.get('confidence_score', 0.5)
            )
            
        except Exception as e:
            print(f"Contextual analysis failed: {e}. Using basic analysis.")
            return self.analyze_prompt(prompt)


def main():
    """Interactive CLI for the AI Task Analyzer"""
    analyzer = AITaskAnalyzer()
    
    print("🤖 AI Task Analyzer (Powered by Gemini)")
    print("Enter vague prompts and get AI-generated technical breakdowns!")
    print("Type 'quit' to exit, 'context' to add project context.\n")
    
    context = ""
    
    while True:
        try:
            user_input = input("Enter your task description: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            if user_input.lower() == 'context':
                context = input("Enter project context (tech stack, project type, etc.): ").strip()
                print(f"Context set: {context}\n")
                continue
            
            if not user_input:
                print("Please enter a task description.\n")
                continue
            
            print("\n🧠 Analyzing with Gemini AI...\n")
            
            if context:
                analysis = analyzer.analyze_with_context(user_input, context)
            else:
                analysis = analyzer.analyze_prompt(user_input)
            
            print(analyzer.format_output(analysis))
            print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()