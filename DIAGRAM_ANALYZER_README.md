# AI Diagram Analyzer Feature

## Overview

The AI Diagram Analyzer is a powerful new feature that allows administrators to upload architecture or flow diagrams and have them automatically converted into structured JSON format using Google's Gemini AI. This feature helps transform visual diagrams into actionable project data.

## Features

### 🎨 Diagram Analysis
- **Upload Support**: PNG, JPEG, GIF, WebP images (max 10MB)
- **AI Processing**: Uses Gemini-3-Flash-Preview for intelligent analysis
- **Structured Output**: Converts diagrams to comprehensive JSON format

### 📊 Analysis Components
The AI extracts and structures the following information:

1. **Components/Services**: All boxes, services, modules, or components
2. **Connections/Flow**: Arrows, lines, or connections between components
3. **Data Flow**: Direction and type of data/information flow
4. **Layers/Tiers**: Different architectural layers (presentation, business, data)
5. **Technologies**: Specific technologies, databases, or frameworks
6. **External Systems**: Third-party services or external dependencies
7. **User Interactions**: User touchpoints or interfaces

### 🚀 Project Planning
- **Suggested Tasks**: AI-generated development tasks with priorities
- **Development Phases**: Organized project phases with task groupings
- **Effort Estimation**: Time estimates for each task
- **Dependencies**: Task dependency mapping

## JSON Output Structure

```json
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
```

## Usage Instructions

### For Administrators

1. **Access the Feature**
   - Login as an administrator
   - Navigate to **Admin Tools** > **Diagram Analyzer**

2. **Upload Diagram**
   - Click "Select File" to choose your diagram
   - Supported formats: PNG, JPEG, GIF, WebP
   - Maximum file size: 10MB
   - Preview will be shown after selection

3. **Analyze Diagram**
   - Click "Analyze with AI" button
   - Wait for Gemini AI to process the image
   - Results will be displayed in structured format

4. **Review Results**
   - Browse components, connections, and suggested tasks
   - View development phases and project breakdown
   - Check for any analysis errors

5. **Download Results**
   - Click "Download JSON" to save the analysis
   - Use the JSON for project planning and documentation

### API Usage

**Endpoint**: `POST /ai/analyze-diagram`

**Authentication**: Admin role required

**Request**: Multipart form data with image file

**Response**:
```json
{
  "success": true,
  "message": "Diagram analyzed successfully",
  "filename": "architecture.png",
  "content_type": "image/png",
  "analysis": {
    // ... structured analysis result
  }
}
```

## Technical Implementation

### Backend Components

1. **AI Router** (`backend/app/routers/ai.py`)
   - New endpoint: `/ai/analyze-diagram`
   - File upload handling with validation
   - Admin-only access control

2. **AI Analyzer Service** (`backend/app/services/ai_analyzer.py`)
   - `analyze_diagram()` method
   - Gemini AI integration with vision capabilities
   - Comprehensive prompt engineering for diagram analysis

3. **File Validation**
   - Image type validation
   - File size limits (10MB max)
   - Base64 encoding for AI processing

### Frontend Components

1. **Diagram Analyzer Component** (`frontend/components/admin/diagram-analyzer.tsx`)
   - File upload interface with drag-and-drop
   - Image preview functionality
   - Results display with structured layout
   - JSON download capability

2. **Admin Tools Integration** (`frontend/app/dashboard/audit/page.tsx`)
   - Tabbed interface for audit and diagram analysis
   - Admin-only access control
   - Responsive design

3. **UI Components**
   - Custom Tabs component using Radix UI
   - File upload with validation
   - Structured result display

## Configuration

### Environment Variables

The feature uses the existing Gemini AI configuration:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Dependencies

**Backend**:
- `google-generativeai`: Gemini AI SDK
- `fastapi`: File upload handling
- `python-multipart`: Multipart form support

**Frontend**:
- `@radix-ui/react-tabs`: Tab interface
- `axios`: API communication
- `lucide-react`: Icons

## Error Handling

### Common Errors

1. **File Type Error**
   - Message: "Only image files are supported"
   - Solution: Upload PNG, JPEG, GIF, or WebP files

2. **File Size Error**
   - Message: "File size must be less than 10MB"
   - Solution: Compress or resize the image

3. **Access Denied**
   - Message: "Only administrators can analyze diagrams"
   - Solution: Login with admin account

4. **AI Service Error**
   - Message: "AI analysis failed"
   - Causes: API quota exceeded, network issues, invalid image
   - Solution: Check API limits, retry later

5. **JSON Parsing Error**
   - The system handles cases where AI returns non-JSON responses
   - Raw response is included for debugging

## Testing

### Demo Script

Run the demo to see sample output:

```bash
cd backend
python demo_diagram_analyzer.py
```

### Test Script

Test the actual AI integration:

```bash
cd backend
python test_diagram_analyzer.py
```

Note: Requires valid Gemini API key and available quota.

## Use Cases

### 1. Architecture Documentation
- Convert hand-drawn architecture diagrams to structured documentation
- Generate component inventories and dependency maps
- Create project roadmaps from architectural designs

### 2. Project Planning
- Extract development tasks from system diagrams
- Organize work into logical phases
- Estimate effort and identify dependencies

### 3. System Analysis
- Analyze existing system diagrams for modernization
- Identify integration points and data flows
- Document external dependencies

### 4. Team Communication
- Convert visual designs to actionable specifications
- Share structured project breakdowns with development teams
- Create consistent documentation from various diagram sources

## Limitations

1. **AI Accuracy**: Results depend on diagram clarity and AI interpretation
2. **Image Quality**: Blurry or low-resolution images may produce poor results
3. **Complex Diagrams**: Very complex diagrams might be partially analyzed
4. **API Limits**: Subject to Gemini API rate limits and quotas
5. **Language**: Works best with English text in diagrams

## Future Enhancements

1. **Batch Processing**: Analyze multiple diagrams at once
2. **Template Generation**: Create Kanban boards from analysis results
3. **Integration**: Direct import of tasks into project boards
4. **Collaboration**: Share analysis results with team members
5. **Version Control**: Track changes in diagram analysis over time

## Support

For issues or questions:
1. Check the error messages in the UI
2. Review the console logs for detailed errors
3. Verify Gemini API key and quota
4. Ensure proper admin permissions
5. Test with simpler diagrams first

## Security Considerations

1. **Admin Only**: Feature restricted to administrators
2. **File Validation**: Strict image type and size validation
3. **Temporary Storage**: Images processed in memory, not stored permanently
4. **API Security**: Gemini API key secured in environment variables
5. **Input Sanitization**: All user inputs validated and sanitized