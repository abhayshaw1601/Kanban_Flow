#!/usr/bin/env python3
"""
Web-based AI Task Analyzer using Flask and Gemini AI
"""

from flask import Flask, render_template, request, jsonify
from ai_task_analyzer_gemini import AITaskAnalyzer
import json
import os

app = Flask(__name__)
analyzer = AITaskAnalyzer()

@app.route('/')
def index():
    return render_template('index_gemini.html')

@app.route('/analyze', methods=['POST'])
def analyze_task():
    """API endpoint to analyze task prompts using Gemini AI"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        context = data.get('context', '').strip()
        
        if not prompt:
            return jsonify({'error': 'Please provide a task description'}), 400
        
        # Use contextual analysis if context is provided
        if context:
            analysis = analyzer.analyze_with_context(prompt, context)
        else:
            analysis = analyzer.analyze_prompt(prompt)
        
        return jsonify({
            'success': True,
            'analysis': {
                'technical_subtasks': analysis.technical_subtasks,
                'acceptance_criteria': analysis.acceptance_criteria,
                'potential_blockers': analysis.potential_blockers,
                'estimated_complexity': analysis.estimated_complexity,
                'domain': analysis.domain,
                'confidence_score': analysis.confidence_score
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test if Gemini API is accessible
        test_analysis = analyzer.analyze_prompt("test")
        return jsonify({
            'status': 'healthy',
            'gemini_api': 'connected',
            'confidence': test_analysis.confidence_score
        })
    except Exception as e:
        return jsonify({
            'status': 'degraded',
            'gemini_api': 'error',
            'error': str(e)
        }), 503

if __name__ == '__main__':
    # Check if API key is available
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Warning: GEMINI_API_KEY not found in environment variables")
        print("Please add your Gemini API key to the .env file")
    
    app.run(debug=True, port=5000)