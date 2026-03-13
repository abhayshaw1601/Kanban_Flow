#!/usr/bin/env python3
"""
Demo script showing the Gemini-powered AI Task Analyzer in action
"""

from ai_task_analyzer_gemini import AITaskAnalyzer
import time

def run_demo():
    """Run demonstration with sample prompts using Gemini AI"""
    analyzer = AITaskAnalyzer()
    
    sample_prompts = [
        {
            "prompt": "make the login better",
            "context": "React + FastAPI web application"
        },
        {
            "prompt": "fix the dashboard performance issues", 
            "context": "Next.js frontend with large datasets"
        },
        {
            "prompt": "add user management to the system",
            "context": "Multi-tenant SaaS platform"
        },
        {
            "prompt": "implement real-time notifications",
            "context": "Mobile app with React Native"
        },
        {
            "prompt": "migrate database to PostgreSQL",
            "context": "Legacy MySQL system with 1M+ records"
        }
    ]
    
    print("🤖 AI Task Analyzer Demo (Powered by Gemini)")
    print("=" * 60)
    print("🧠 Using Google Gemini AI for intelligent task analysis")
    print("=" * 60)
    
    for i, sample in enumerate(sample_prompts, 1):
        print(f"\n📝 Sample {i}: '{sample['prompt']}'")
        print(f"🎯 Context: {sample['context']}")
        print("-" * 50)
        
        print("🧠 Analyzing with Gemini AI...")
        start_time = time.time()
        
        try:
            analysis = analyzer.analyze_with_context(sample['prompt'], sample['context'])
            end_time = time.time()
            
            print(f"⚡ Analysis completed in {end_time - start_time:.1f}s")
            print()
            print(analyzer.format_output(analysis))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Using fallback analysis...")
            analysis = analyzer._fallback_analysis(sample['prompt'])
            print(analyzer.format_output(analysis))
        
        if i < len(sample_prompts):
            input(f"\nPress Enter to continue to example {i+1}...")

def interactive_demo():
    """Interactive demo mode"""
    analyzer = AITaskAnalyzer()
    
    print("\n🎮 Interactive Demo Mode")
    print("Enter your own prompts to see Gemini AI in action!")
    print("Type 'quit' to exit, 'examples' to see sample prompts.\n")
    
    context = ""
    
    while True:
        try:
            user_input = input("Your task: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input.lower() == 'examples':
                print("\n💡 Example prompts:")
                examples = [
                    "optimize the search functionality",
                    "add dark mode support", 
                    "implement file upload feature",
                    "fix mobile responsiveness",
                    "add analytics dashboard"
                ]
                for ex in examples:
                    print(f"  • {ex}")
                print()
                continue
            
            if user_input.lower().startswith('context:'):
                context = user_input[8:].strip()
                print(f"✅ Context set: {context}\n")
                continue
            
            if not user_input:
                continue
            
            print("\n🧠 Gemini AI is analyzing...")
            start_time = time.time()
            
            if context:
                analysis = analyzer.analyze_with_context(user_input, context)
            else:
                analysis = analyzer.analyze_prompt(user_input)
            
            end_time = time.time()
            print(f"⚡ Completed in {end_time - start_time:.1f}s\n")
            print(analyzer.format_output(analysis))
            print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")

def benchmark_demo():
    """Benchmark different types of prompts"""
    analyzer = AITaskAnalyzer()
    
    print("\n📊 Benchmark Demo - Testing Different Prompt Types")
    print("=" * 60)
    
    test_cases = [
        ("Vague", "make it better"),
        ("Specific", "implement OAuth2 authentication with JWT tokens"),
        ("Technical", "refactor monolithic architecture to microservices"),
        ("UI/UX", "improve user onboarding experience"),
        ("Performance", "reduce page load time by 50%"),
        ("Security", "fix SQL injection vulnerabilities")
    ]
    
    results = []
    
    for category, prompt in test_cases:
        print(f"\n🧪 Testing {category}: '{prompt}'")
        
        try:
            start_time = time.time()
            analysis = analyzer.analyze_prompt(prompt)
            end_time = time.time()
            
            results.append({
                'category': category,
                'prompt': prompt,
                'confidence': analysis.confidence_score,
                'complexity': analysis.estimated_complexity,
                'domain': analysis.domain,
                'time': end_time - start_time
            })
            
            print(f"  ✅ Confidence: {analysis.confidence_score:.1%}")
            print(f"  📊 Complexity: {analysis.estimated_complexity}")
            print(f"  🎯 Domain: {analysis.domain}")
            print(f"  ⚡ Time: {end_time - start_time:.1f}s")
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    # Summary
    print(f"\n📈 Benchmark Summary:")
    print(f"Average confidence: {sum(r['confidence'] for r in results) / len(results):.1%}")
    print(f"Average response time: {sum(r['time'] for r in results) / len(results):.1f}s")
    print(f"Domains detected: {set(r['domain'] for r in results)}")

if __name__ == "__main__":
    print("🚀 Choose demo mode:")
    print("1. Guided examples")
    print("2. Interactive mode") 
    print("3. Benchmark test")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        run_demo()
    elif choice == "2":
        interactive_demo()
    elif choice == "3":
        benchmark_demo()
    else:
        print("Running guided examples...")
        run_demo()
    
    print("\n👋 Demo completed!")