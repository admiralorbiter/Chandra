#!/usr/bin/env python3
"""
Chandra Education Control Tool (eductl)
Command-line interface for managing scripts and lessons
"""

import os
import sys
import argparse
import json
import time
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.scripts.manager import ScriptManager

def create_script(args):
    """Create a new script"""
    app = create_app()
    
    with app.app_context():
        manager = ScriptManager()
        
        script_id = args.name
        template = args.template
        
        print(f"Creating script '{script_id}' with template '{template}'...")
        
        success = manager.create_script(script_id, template)
        
        if success:
            print(f"✅ Script '{script_id}' created successfully!")
            print(f"📁 Location: {manager.scripts_dir}/{script_id}.py")
        else:
            print(f"❌ Failed to create script '{script_id}'")
            sys.exit(1)

def list_scripts(args):
    """List all available scripts"""
    app = create_app()
    
    with app.app_context():
        manager = ScriptManager()
        scripts = manager.get_script_list()
        
        if not scripts:
            print("No scripts found.")
            return
        
        print(f"Found {len(scripts)} script(s):")
        print()
        
        for script in scripts:
            print(f"📝 {script['name']} ({script['id']})")
            print(f"   Description: {script['description']}")
            print(f"   Author: {script['author']}")
            print(f"   Version: {script['version']}")
            print(f"   Created: {script['created']}")
            
            if script['hooks']:
                hooks = [hook for hook, enabled in script['hooks'].items() if enabled]
                if hooks:
                    print(f"   Hooks: {', '.join(hooks)}")
            
            print()

def run_script(args):
    """Run a script"""
    app = create_app()
    
    with app.app_context():
        manager = ScriptManager()
        
        script_id = args.name
        
        print(f"Starting script '{script_id}'...")
        
        # Load the script if not already loaded
        if script_id not in manager.script_metadata:
            success = manager.load_script_from_file(script_id)
            if not success:
                print(f"❌ Failed to load script '{script_id}'")
                sys.exit(1)
        
        # Start the script
        success = manager.start_script(script_id)
        
        if success:
            print(f"✅ Script '{script_id}' started successfully!")
            print("Press Ctrl+C to stop the script...")
            
            try:
                # Keep the script running
                while True:
                    time.sleep(1)
                    manager.tick()
            except KeyboardInterrupt:
                print("\n🛑 Stopping script...")
                manager.stop_script(script_id)
                print("✅ Script stopped.")
        else:
            print(f"❌ Failed to start script '{script_id}'")
            sys.exit(1)

def validate_script(args):
    """Validate a script"""
    app = create_app()
    
    with app.app_context():
        manager = ScriptManager()
        
        script_id = args.name
        
        print(f"Validating script '{script_id}'...")
        
        # Get script content
        content = manager.get_script_content(script_id)
        if not content:
            print(f"❌ Script '{script_id}' not found")
            sys.exit(1)
        
        # Validate the script
        import requests
        
        try:
            response = requests.post(
                'http://localhost:5000/scripts/validate',
                json={'content': content},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data['valid']:
                    print("✅ Script is valid!")
                else:
                    print("❌ Script has errors:")
                    for error in data['errors']:
                        print(f"   - {error}")
                
                if data['warnings']:
                    print("⚠️  Warnings:")
                    for warning in data['warnings']:
                        print(f"   - {warning}")
            else:
                print(f"❌ Failed to validate script: {response.status_code}")
                sys.exit(1)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to server: {e}")
            print("Make sure the Flask app is running on localhost:5000")
            sys.exit(1)

def export_scripts(args):
    """Export scripts to a zip file"""
    import zipfile
    from datetime import datetime
    
    app = create_app()
    
    with app.app_context():
        manager = ScriptManager()
        
        # Create zip file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"chandra_scripts_{timestamp}.zip"
        
        print(f"Exporting scripts to '{zip_filename}'...")
        
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            # Add all script files
            for script_id, script_file in manager.script_files.items():
                zipf.write(script_file, f"scripts/{script_file.name}")
                
                # Add metadata file if it exists
                metadata_file = manager.scripts_dir / f"{script_id}.json"
                if metadata_file.exists():
                    zipf.write(metadata_file, f"scripts/{metadata_file.name}")
        
        print(f"✅ Scripts exported to '{zip_filename}'")

def show_script_info(args):
    """Show detailed information about a script"""
    app = create_app()
    
    with app.app_context():
        manager = ScriptManager()
        
        script_id = args.name
        
        print(f"Script Information: {script_id}")
        print("=" * 50)
        
        # Get script metadata
        metadata = manager.script_metadata.get(script_id)
        if not metadata:
            print(f"❌ Script '{script_id}' not found")
            sys.exit(1)
        
        print(f"Name: {metadata.name}")
        print(f"Description: {metadata.description}")
        print(f"Author: {metadata.author}")
        print(f"Version: {metadata.version}")
        print(f"Created: {metadata.created}")
        
        if metadata.hooks:
            enabled_hooks = [hook for hook, enabled in metadata.hooks.items() if enabled]
            if enabled_hooks:
                print(f"Hooks: {', '.join(enabled_hooks)}")
        
        if metadata.requirements:
            print(f"Requirements: {', '.join(metadata.requirements)}")
        
        # Get script content
        content = manager.get_script_content(script_id)
        if content:
            lines = content.split('\n')
            print(f"\nContent ({len(lines)} lines):")
            print("-" * 30)
            for i, line in enumerate(lines[:20], 1):
                print(f"{i:3d}: {line}")
            
            if len(lines) > 20:
                print(f"... and {len(lines) - 20} more lines")
        
        # Get script state if running
        state = manager.get_script_state(script_id)
        if state:
            print(f"\nCurrent State:")
            print("-" * 30)
            for key, value in state.items():
                print(f"{key}: {value}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Chandra Education Control Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  eductl new-script my_lesson --template counting_fingers
  eductl list-scripts
  eductl run my_lesson
  eductl validate my_lesson
  eductl info my_lesson
  eductl export --zip
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # New script command
    new_parser = subparsers.add_parser('new-script', help='Create a new script')
    new_parser.add_argument('name', help='Script name/ID')
    new_parser.add_argument('--template', default='basic', 
                          choices=['basic', 'counting_fingers', 'letter_tracing'],
                          help='Script template to use')
    new_parser.set_defaults(func=create_script)
    
    # List scripts command
    list_parser = subparsers.add_parser('list-scripts', help='List all scripts')
    list_parser.set_defaults(func=list_scripts)
    
    # Run script command
    run_parser = subparsers.add_parser('run', help='Run a script')
    run_parser.add_argument('name', help='Script name/ID')
    run_parser.set_defaults(func=run_script)
    
    # Validate script command
    validate_parser = subparsers.add_parser('validate', help='Validate a script')
    validate_parser.add_argument('name', help='Script name/ID')
    validate_parser.set_defaults(func=validate_script)
    
    # Show script info command
    info_parser = subparsers.add_parser('info', help='Show script information')
    info_parser.add_argument('name', help='Script name/ID')
    info_parser.set_defaults(func=show_script_info)
    
    # Export scripts command
    export_parser = subparsers.add_parser('export', help='Export scripts')
    export_parser.add_argument('--zip', action='store_true', help='Export as zip file')
    export_parser.set_defaults(func=export_scripts)
    
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