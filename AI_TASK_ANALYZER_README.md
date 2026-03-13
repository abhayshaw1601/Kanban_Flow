# 🤖 AI Task Analyzer

An intelligent assistant that transforms vague task descriptions into structured technical breakdowns with sub-tasks, acceptance criteria, and potential blockers.

## Features

- **Smart Analysis**: Automatically detects task domain (frontend, backend, testing, etc.)
- **Complexity Assessment**: Estimates task complexity (low, medium, high)
- **Structured Output**: Generates 3-5 technical sub-tasks, acceptance criteria, and potential blockers
- **Multiple Interfaces**: CLI, Web UI, and programmatic API

## Quick Start

### 1. CLI Version
```bash
python ai_task_analyzer.py
```

### 2. Web Interface
```bash
pip install -r requirements_analyzer.txt
python web_task_analyzer.py
```
Then open http://localhost:5000 in your browser.

### 3. Demo Examples
```bash
python demo.py
```

## Usage Examples

### Input: "make the login better"
**Output:**
```
📊 Estimated Complexity: MEDIUM

📋 TECHNICAL SUB-TASKS:
  1. Design component structure and props interface
  2. Implement responsive UI components  
  3. Add state management and event handlers
  4. Integrate with backend APIs
  5. Add error handling and loading states

✅ ACCEPTANCE CRITERIA:
  1. All functionality works as specified in requirements
  2. Code passes all existing tests and new tests are added
  3. Implementation follows project coding standards
  4. UI is responsive across different screen sizes
  5. Components are accessible (WCAG compliant)

⚠️ POTENTIAL BLOCKERS:
  1. Unclear or changing requirements
  2. Dependencies on external services or APIs
  3. Browser compatibility issues
  4. Third-party library conflicts
  5. Performance issues with large datasets
```

## How It Works

The AI Task Analyzer uses pattern matching and domain detection to:

1. **Analyze the prompt** for keywords and context
2. **Detect the domain** (frontend, backend, testing, security, etc.)
3. **Estimate complexity** based on action words and scope
4. **Generate structured outputs** using domain-specific templates
5. **Identify potential issues** based on complexity and domain

## Domain Detection

The system recognizes these domains:
- **Frontend**: UI, components, React, Vue, CSS, HTML
- **Backend**: API, server, database, endpoints, services
- **DevOps**: Deploy, Docker, CI/CD, infrastructure
- **Testing**: Unit tests, integration, E2E, coverage
- **Security**: Auth, permissions, encryption, vulnerabilities

## Complexity Levels

- **Low**: Fix, update, change, modify, adjust
- **Medium**: Add, create, implement, build, develop  
- **High**: Integrate, migrate, refactor, redesign, architect

## API Usage

```python
from ai_task_analyzer import AITaskAnalyzer

analyzer = AITaskAnalyzer()
analysis = analyzer.analyze_prompt("implement user authentication")

print(f"Complexity: {analysis.estimated_complexity}")
print(f"Sub-tasks: {analysis.technical_subtasks}")
print(f"Criteria: {analysis.acceptance_criteria}")
print(f"Blockers: {analysis.potential_blockers}")
```

## Customization

You can extend the analyzer by:
- Adding new domain patterns in `domain_patterns`
- Modifying complexity keywords in `complexity_keywords`
- Customizing task templates in `_generate_subtasks()`
- Adding domain-specific criteria and blockers

## Requirements

- Python 3.7+
- Flask (for web interface)

## License

MIT License - feel free to use and modify as needed!