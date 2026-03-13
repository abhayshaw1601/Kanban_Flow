#!/usr/bin/env python3
"""
Web-based AI Task Analyzer using Flask
"""

from flask import Flask, render_template, request, jsonify
from ai_task_analyzer import AITaskAnalyzer
import json

app = Flask(__name__)
analyzer = AITaskAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_task():
    """API endpoint to analyze task prompts"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'error': 'Please provide a task description'}), 400
        
        analysis = analyzer.analyze_prompt(prompt)
        
        return jsonify({
            'success': True,
            'analysis': {
                'technical_subtasks': analysis.technical_subtasks,
                'acceptance_criteria': analysis.acceptance_criteria,
                'potential_blockers': analysis.potential_blockers,
                'estimated_complexity': analysis.estimated_complexity
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)