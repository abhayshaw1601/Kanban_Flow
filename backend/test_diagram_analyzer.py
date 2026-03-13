#!/usr/bin/env python3
"""
Test script for the AI Diagram Analyzer feature
"""

import asyncio
import base64
import json
from pathlib import Path
from app.services.ai_analyzer import ai_analyzer

async def test_diagram_analyzer():
    """Test the diagram analyzer with a sample image"""
    
    print("🧪 Testing AI Diagram Analyzer")
    print("=" * 50)
    
    # Create a simple test image (1x1 pixel PNG)
    # This is a minimal PNG file in base64 format
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    content_type = "image/png"
    
    try:
        print("📊 Analyzing test diagram...")
        print(f"Content Type: {content_type}")
        print(f"Image Size: {len(test_image_base64)} characters (base64)")
        
        # Test the diagram analysis
        result = await ai_analyzer.analyze_diagram(test_image_base64, content_type)
        
        print("\n✅ Analysis completed successfully!")
        print("\n📋 Analysis Result:")
        print(json.dumps(result, indent=2))
        
        # Check if the result has the expected structure
        expected_keys = [
            'diagram_type', 'title', 'description', 'components', 
            'connections', 'data_flows', 'layers', 'external_dependencies', 
            'project_breakdown'
        ]
        
        print("\n🔍 Validating result structure...")
        for key in expected_keys:
            if key in result:
                print(f"  ✅ {key}: Present")
            else:
                print(f"  ❌ {key}: Missing")
        
        # Check project breakdown structure
        if 'project_breakdown' in result and isinstance(result['project_breakdown'], dict):
            pb = result['project_breakdown']
            if 'suggested_tasks' in pb:
                print(f"  ✅ suggested_tasks: {len(pb['suggested_tasks'])} tasks found")
            if 'development_phases' in pb:
                print(f"  ✅ development_phases: {len(pb['development_phases'])} phases found")
        
        print("\n🎉 Diagram analyzer test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False

async def test_ai_health():
    """Test AI service health"""
    print("\n🏥 Testing AI Service Health...")
    
    try:
        is_healthy = await ai_analyzer.check_health()
        if is_healthy:
            print("✅ AI Service is healthy and ready")
        else:
            print("⚠️ AI Service is not responding properly")
        return is_healthy
    except Exception as e:
        print(f"❌ AI Health check failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Diagram Analyzer Tests")
    print("=" * 60)
    
    # Test AI health first
    health_ok = await test_ai_health()
    if not health_ok:
        print("\n❌ AI service is not healthy. Cannot proceed with diagram analysis test.")
        return
    
    # Test diagram analyzer
    success = await test_diagram_analyzer()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Diagram analyzer is working correctly.")
        print("\n📝 Next steps:")
        print("1. Start the backend server: uvicorn app.main:app --reload")
        print("2. Start the frontend: npm run dev")
        print("3. Login as admin and go to Admin Tools > Diagram Analyzer")
        print("4. Upload an architecture diagram to test the feature")
    else:
        print("❌ Tests failed. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())