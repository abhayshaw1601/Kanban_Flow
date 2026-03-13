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
        Analyze a vague prompt and generate structured technical tasks
        
        Args:
            prompt: The user's vague task description
            
        Returns:
            TaskAnalysis object with structured breakdown
        """
        prompt_lower = prompt.lower()
        
        # Detect domain and complexity
        domain = self._detect_domain(prompt_lower)
        complexity = self._estimate_complexity(prompt_lower)
        
        # Generate components
        subtasks = self._generate_subtasks(prompt, domain, complexity)
        criteria = self._generate_acceptance_criteria(prompt, domain)
        blockers = self._generate_potential_blockers(prompt, domain, complexity)
        
        return TaskAnalysis(
            technical_subtasks=subtasks,
            acceptance_criteria=criteria,
            potential_blockers=blockers,
            estimated_complexity=complexity
        )

    def _detect_domain(self, prompt: str) -> str:
        """Detect the primary domain of the task"""
        domain_scores = {}
        
        for domain, keywords in self.domain_patterns.items():
            score = sum(1 for keyword in keywords if keyword in prompt)
            domain_scores[domain] = score
        
        return max(domain_scores, key=domain_scores.get) if max(domain_scores.values()) > 0 else 'general'

    def _estimate_complexity(self, prompt: str) -> str:
        """Estimate task complexity based on keywords"""
        for complexity, keywords in self.complexity_keywords.items():
            if any(keyword in prompt for keyword in keywords):
                return complexity
        return 'medium'  # default

    def _generate_subtasks(self, prompt: str, domain: str, complexity: str) -> List[str]:
        """Generate technical sub-tasks based on prompt analysis"""
        base_tasks = []
        
        # Domain-specific task templates
        if domain == 'frontend':
            base_tasks = [
                "Design component structure and props interface",
                "Implement responsive UI components",
                "Add state management and event handlers",
                "Integrate with backend APIs",
                "Add error handling and loading states"
            ]
        elif domain == 'backend':
            base_tasks = [
                "Design API endpoints and data models",
                "Implement database schema changes",
                "Create service layer business logic",
                "Add authentication and authorization",
                "Implement error handling and validation"
            ]
        elif domain == 'testing':
            base_tasks = [
                "Set up test environment and fixtures",
                "Write unit tests for core functionality",
                "Implement integration tests",
                "Add end-to-end test scenarios",
                "Configure test coverage reporting"
            ]
        else:
            # General tasks
            base_tasks = [
                "Analyze requirements and define scope",
                "Design system architecture and components",
                "Implement core functionality",
                "Add error handling and edge cases",
                "Create documentation and tests"
            ]
        
        # Adjust based on complexity
        if complexity == 'low':
            return base_tasks[:3]
        elif complexity == 'high':
            base_tasks.append("Performance optimization and monitoring")
            base_tasks.append("Security review and compliance check")
        
        return base_tasks

    def _generate_acceptance_criteria(self, prompt: str, domain: str) -> List[str]:
        """Generate acceptance criteria based on the prompt"""
        criteria = [
            "All functionality works as specified in requirements",
            "Code passes all existing tests and new tests are added",
            "Implementation follows project coding standards"
        ]
        
        # Domain-specific criteria
        if domain == 'frontend':
            criteria.extend([
                "UI is responsive across different screen sizes",
                "Components are accessible (WCAG compliant)"
            ])
        elif domain == 'backend':
            criteria.extend([
                "API endpoints return correct status codes and data",
                "Database operations are properly transactional"
            ])
        elif domain == 'security':
            criteria.extend([
                "Security vulnerabilities are addressed",
                "Authentication and authorization work correctly"
            ])
        
        return criteria

    def _generate_potential_blockers(self, prompt: str, domain: str, complexity: str) -> List[str]:
        """Generate potential blockers and edge cases"""
        blockers = [
            "Unclear or changing requirements",
            "Dependencies on external services or APIs"
        ]
        
        # Domain-specific blockers
        if domain == 'frontend':
            blockers.extend([
                "Browser compatibility issues",
                "Third-party library conflicts",
                "Performance issues with large datasets"
            ])
        elif domain == 'backend':
            blockers.extend([
                "Database migration conflicts",
                "API rate limiting or timeout issues",
                "Concurrent access and race conditions"
            ])
        elif domain == 'devops':
            blockers.extend([
                "Environment configuration differences",
                "Network connectivity and firewall issues",
                "Resource constraints (CPU, memory, storage)"
            ])
        
        # Complexity-based blockers
        if complexity == 'high':
            blockers.extend([
                "Integration complexity with existing systems",
                "Scalability and performance requirements",
                "Team coordination and knowledge transfer"
            ])
        
        return blockers

    def format_output(self, analysis: TaskAnalysis) -> str:
        """Format the analysis results for display"""
        output = []
        output.append("=== TASK ANALYSIS ===\n")
        
        output.append(f"📊 Estimated Complexity: {analysis.estimated_complexity.upper()}\n")
        
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


def main():
    """Interactive CLI for the AI Task Analyzer"""
    analyzer = AITaskAnalyzer()
    
    print("🤖 AI Task Analyzer")
    print("Enter vague prompts and get structured technical breakdowns!")
    print("Type 'quit' to exit.\n")
    
    while True:
        try:
            prompt = input("Enter your task description: ").strip()
            
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            if not prompt:
                print("Please enter a task description.\n")
                continue
            
            print("\nAnalyzing prompt...\n")
            analysis = analyzer.analyze_prompt(prompt)
            print(analyzer.format_output(analysis))
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()