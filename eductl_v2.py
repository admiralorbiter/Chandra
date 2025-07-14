#!/usr/bin/env python3
"""
Chandra Education Control Tool v2 (eductl)
Command-line interface for managing lessons and leveraging Python tools
"""

import os
import sys
import argparse
import json
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.scripts.manager import LessonManager

def create_lesson(args):
    """Create a new lesson"""
    app = create_app()
    
    with app.app_context():
        manager = LessonManager()
        
        lesson_id = args.name
        template = args.template
        
        print(f"Creating lesson '{lesson_id}' with template '{template}'...")
        
        success = manager.create_lesson(lesson_id, template)
        
        if success:
            print(f"✅ Lesson '{lesson_id}' created successfully!")
            print(f"📁 Location: {manager.lessons_dir}/{lesson_id}.py")
            
            # Show lesson info
            metadata = manager.lesson_metadata.get(lesson_id)
            if metadata:
                print(f"📝 Name: {metadata.name}")
                print(f"📋 Description: {metadata.description}")
                print(f"🏷️  Tags: {', '.join(metadata.tags)}")
                print(f"📊 Difficulty: {metadata.difficulty}")
                print(f"⏱️  Duration: {metadata.duration} minutes")
        else:
            print(f"❌ Failed to create lesson '{lesson_id}'")
            sys.exit(1)

def list_lessons(args):
    """List all available lessons"""
    app = create_app()
    
    with app.app_context():
        manager = LessonManager()
        lessons = manager.get_lesson_list()
        
        if not lessons:
            print("No lessons found.")
            return
        
        print(f"Found {len(lessons)} lesson(s):")
        print()
        
        for lesson in lessons:
            print(f"📝 {lesson['name']} ({lesson['id']})")
            print(f"   Description: {lesson['description']}")
            print(f"   Author: {lesson['author']}")
            print(f"   Version: {lesson['version']}")
            print(f"   Created: {lesson['created']}")
            print(f"   Tags: {', '.join(lesson['tags'])}")
            print(f"   Difficulty: {lesson['difficulty']}")
            print(f"   Duration: {lesson['duration']} minutes")
            
            if lesson['requirements']:
                print(f"   Requirements: {', '.join(lesson['requirements'])}")
            
            print()

def run_lesson(args):
    """Run a lesson"""
    app = create_app()
    
    with app.app_context():
        manager = LessonManager()
        
        lesson_id = args.name
        
        print(f"Starting lesson '{lesson_id}'...")
        
        # Load the lesson if not already loaded
        if lesson_id not in manager.lesson_metadata:
            success = manager.load_lesson_from_file(lesson_id)
            if not success:
                print(f"❌ Failed to load lesson '{lesson_id}'")
                sys.exit(1)
        
        # Start the lesson
        success = manager.start_lesson(lesson_id)
        
        if success:
            print(f"✅ Lesson '{lesson_id}' started successfully!")
            print("Press Ctrl+C to stop the lesson...")
            
            try:
                # Keep the lesson running
                while True:
                    time.sleep(1)
                    manager.tick()
                    
                    # Show state updates
                    state = manager.get_lesson_state(lesson_id)
                    if state and state.get('state', {}).get('lesson_progress'):
                        progress = state['state']['lesson_progress']
                        print(f"\r📊 Progress: {progress:.1f}%", end='', flush=True)
                        
            except KeyboardInterrupt:
                print("\n🛑 Stopping lesson...")
                manager.stop_lesson(lesson_id)
                print("✅ Lesson stopped.")
        else:
            print(f"❌ Failed to start lesson '{lesson_id}'")
            sys.exit(1)

def validate_lesson(args):
    """Validate a lesson"""
    app = create_app()
    
    with app.app_context():
        manager = LessonManager()
        
        lesson_id = args.name
        
        print(f"Validating lesson '{lesson_id}'...")
        
        # Get lesson content
        content = manager.get_lesson_content(lesson_id)
        if not content:
            print(f"❌ Lesson '{lesson_id}' not found")
            sys.exit(1)
        
        # Basic syntax validation
        try:
            compile(content, f'<lesson_{lesson_id}>', 'exec')
            print("✅ Lesson syntax is valid!")
        except SyntaxError as e:
            print(f"❌ Syntax error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Compilation error: {e}")
            sys.exit(1)
        
        # Check for required hooks
        required_hooks = ['@on_start', '@on_gesture']
        missing_hooks = []
        
        for hook in required_hooks:
            if hook not in content:
                missing_hooks.append(hook)
        
        if missing_hooks:
            print(f"⚠️  Missing recommended hooks: {', '.join(missing_hooks)}")
        else:
            print("✅ All recommended hooks are present")
        
        # Check for Python tool usage
        python_tools = ['import numpy', 'import pandas', 'import matplotlib', 
                       'import scipy', 'import sklearn', 'import seaborn']
        used_tools = []
        
        for tool in python_tools:
            if tool in content:
                used_tools.append(tool.split()[1])
        
        if used_tools:
            print(f"🔧 Using Python tools: {', '.join(used_tools)}")
        else:
            print("ℹ️  No advanced Python tools detected")

def export_lessons(args):
    """Export lessons to a zip file"""
    import zipfile
    from datetime import datetime
    
    app = create_app()
    
    with app.app_context():
        manager = LessonManager()
        
        # Create zip file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"chandra_lessons_{timestamp}.zip"
        
        print(f"Exporting lessons to '{zip_filename}'...")
        
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            # Add all lesson files
            for lesson_id, lesson_file in manager.lesson_files.items():
                zipf.write(lesson_file, f"lessons/{lesson_file.name}")
                
                # Add metadata file if it exists
                metadata_file = manager.lessons_dir / f"{lesson_id}.json"
                if metadata_file.exists():
                    zipf.write(metadata_file, f"lessons/{metadata_file.name}")
        
        print(f"✅ Lessons exported to '{zip_filename}'")

def show_lesson_info(args):
    """Show detailed information about a lesson"""
    app = create_app()
    
    with app.app_context():
        manager = LessonManager()
        
        lesson_id = args.name
        
        print(f"Lesson Information: {lesson_id}")
        print("=" * 50)
        
        # Get lesson metadata
        metadata = manager.lesson_metadata.get(lesson_id)
        if not metadata:
            print(f"❌ Lesson '{lesson_id}' not found")
            sys.exit(1)
        
        print(f"Name: {metadata.name}")
        print(f"Description: {metadata.description}")
        print(f"Author: {metadata.author}")
        print(f"Version: {metadata.version}")
        print(f"Created: {metadata.created}")
        print(f"Tags: {', '.join(metadata.tags)}")
        print(f"Difficulty: {metadata.difficulty}")
        print(f"Duration: {metadata.duration} minutes")
        
        if metadata.requirements:
            print(f"Requirements: {', '.join(metadata.requirements)}")
        
        if metadata.dependencies:
            print(f"Dependencies: {', '.join(metadata.dependencies)}")
        
        # Get lesson content
        content = manager.get_lesson_content(lesson_id)
        if content:
            lines = content.split('\n')
            print(f"\nContent ({len(lines)} lines):")
            print("-" * 30)
            for i, line in enumerate(lines[:20], 1):
                print(f"{i:3d}: {line}")
            
            if len(lines) > 20:
                print(f"... and {len(lines) - 20} more lines")
        
        # Get lesson state if running
        state = manager.get_lesson_state(lesson_id)
        if state:
            print(f"\nCurrent State:")
            print("-" * 30)
            for key, value in state.get('state', {}).items():
                print(f"{key}: {value}")

def install_dependencies(args):
    """Install Python dependencies for lessons"""
    app = create_app()
    
    with app.app_context():
        manager = LessonManager()
        
        print("Installing Python dependencies for lessons...")
        
        # Collect all requirements from lessons
        all_requirements = set()
        for lesson_id, metadata in manager.lesson_metadata.items():
            all_requirements.update(metadata.requirements)
        
        if not all_requirements:
            print("ℹ️  No additional dependencies required")
            return
        
        print(f"Found requirements: {', '.join(all_requirements)}")
        
        # Install dependencies
        for requirement in all_requirements:
            print(f"Installing {requirement}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', requirement])
                print(f"✅ {requirement} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {requirement}: {e}")
                sys.exit(1)

def analyze_lesson(args):
    """Analyze a lesson for Python tool usage and complexity"""
    app = create_app()
    
    with app.app_context():
        manager = LessonManager()
        
        lesson_id = args.name
        
        print(f"Analyzing lesson '{lesson_id}'...")
        
        # Get lesson content
        content = manager.get_lesson_content(lesson_id)
        if not content:
            print(f"❌ Lesson '{lesson_id}' not found")
            sys.exit(1)
        
        # Analyze imports
        imports = []
        for line in content.split('\n'):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                imports.append(line.strip())
        
        print(f"\n📦 Imports ({len(imports)}):")
        for imp in imports:
            print(f"   {imp}")
        
        # Analyze hooks
        hooks = []
        hook_patterns = ['@on_start', '@on_gesture', '@on_tick', '@on_complete']
        for pattern in hook_patterns:
            if pattern in content:
                hooks.append(pattern)
        
        print(f"\n🎣 Hooks ({len(hooks)}):")
        for hook in hooks:
            print(f"   {hook}")
        
        # Analyze Python tools usage
        tools = {
            'numpy': 'Numerical computing',
            'pandas': 'Data manipulation',
            'matplotlib': 'Data visualization',
            'scipy': 'Scientific computing',
            'sklearn': 'Machine learning',
            'seaborn': 'Statistical visualization',
            'requests': 'HTTP requests',
            'json': 'JSON handling',
            'time': 'Time utilities',
            'datetime': 'Date/time handling',
            'math': 'Mathematical functions',
            'random': 'Random number generation',
            'collections': 'Data structures',
            'itertools': 'Iteration tools',
            'functools': 'Function tools'
        }
        
        used_tools = []
        for tool, description in tools.items():
            if f'import {tool}' in content or f'from {tool}' in content:
                used_tools.append((tool, description))
        
        print(f"\n🔧 Python Tools ({len(used_tools)}):")
        for tool, description in used_tools:
            print(f"   {tool}: {description}")
        
        # Complexity analysis
        lines = len(content.split('\n'))
        functions = content.count('def ')
        variables = content.count(' = ')
        
        print(f"\n📊 Complexity Analysis:")
        print(f"   Lines of code: {lines}")
        print(f"   Functions: {functions}")
        print(f"   Variable assignments: {variables}")
        
        if lines < 50:
            complexity = "Simple"
        elif lines < 100:
            complexity = "Moderate"
        else:
            complexity = "Complex"
        
        print(f"   Overall complexity: {complexity}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Chandra Education Control Tool v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  eductl new-lesson my_lesson --template counting_fingers
  eductl new-lesson data_analysis --template data_analysis
  eductl list-lessons
  eductl run my_lesson
  eductl validate my_lesson
  eductl info my_lesson
  eductl analyze my_lesson
  eductl install-deps
  eductl export --zip
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create lesson command
    create_parser = subparsers.add_parser('new-lesson', help='Create a new lesson')
    create_parser.add_argument('name', help='Lesson name')
    create_parser.add_argument('--template', default='basic', 
                             choices=['basic', 'counting_fingers', 'data_analysis'],
                             help='Lesson template to use')
    create_parser.set_defaults(func=create_lesson)
    
    # List lessons command
    list_parser = subparsers.add_parser('list-lessons', help='List all lessons')
    list_parser.set_defaults(func=list_lessons)
    
    # Run lesson command
    run_parser = subparsers.add_parser('run', help='Run a lesson')
    run_parser.add_argument('name', help='Lesson name')
    run_parser.set_defaults(func=run_lesson)
    
    # Validate lesson command
    validate_parser = subparsers.add_parser('validate', help='Validate a lesson')
    validate_parser.add_argument('name', help='Lesson name')
    validate_parser.set_defaults(func=validate_lesson)
    
    # Export lessons command
    export_parser = subparsers.add_parser('export', help='Export lessons')
    export_parser.add_argument('--zip', action='store_true', help='Export as zip file')
    export_parser.set_defaults(func=export_lessons)
    
    # Show lesson info command
    info_parser = subparsers.add_parser('info', help='Show lesson information')
    info_parser.add_argument('name', help='Lesson name')
    info_parser.set_defaults(func=show_lesson_info)
    
    # Install dependencies command
    deps_parser = subparsers.add_parser('install-deps', help='Install lesson dependencies')
    deps_parser.set_defaults(func=install_dependencies)
    
    # Analyze lesson command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a lesson')
    analyze_parser.add_argument('name', help='Lesson name')
    analyze_parser.set_defaults(func=analyze_lesson)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 