#!/usr/bin/env python3
"""
Demo script showing the AI Task Analyzer in action
"""

from ai_task_analyzer import AITaskAnalyzer

def run_demo():
    """Run demonstration with sample prompts"""
    analyzer = AITaskAnalyzer()
    
    sample_prompts = [
        "make the login better",
        "fix the dashboard performance issues", 
        "add user management to the system",
        "implement real-time notifications",
        "migrate database to PostgreSQL"
    ]
    
    print("🤖 AI Task Analyzer Demo")
    print("=" * 50)
    
    for i, prompt in enumerate(sample_prompts, 1):
        print(f"\n📝 Sample Prompt {i}: '{prompt}'")
        print("-" * 40)
        
        analysis = analyzer.analyze_prompt(prompt)
        print(analyzer.format_output(analysis))
        
        if i < len(sample_prompts):
            input("\nPress Enter to continue to next example...")

if __name__ == "__main__":
    run_demo()