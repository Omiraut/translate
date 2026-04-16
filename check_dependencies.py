#!/usr/bin/env python
"""
Setup validation script
Checks if all dependencies are properly installed
"""

import sys
import importlib

def check_dependency(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✓ {package_name}")
        return True
    except ImportError:
        print(f"✗ {package_name} - NOT INSTALLED")
        return False


def main():
    """Check all required dependencies"""
    print("\n🔍 Checking Translation API Dependencies...\n")
    
    dependencies = [
        ("FastAPI", "fastapi"),
        ("Uvicorn", "uvicorn"),
        ("Pydantic", "pydantic"),
        ("deep-translator", "deep_translator"),
        ("googletrans", "googletrans"),
        ("python-dotenv", "dotenv"),
        ("httpx", "httpx"),
    ]
    
    optional_dependencies = [
        ("pytest", "pytest"),
        ("black", "black"),
        ("flake8", "flake8"),
    ]
    
    failed = 0
    
    print("📦 Required Dependencies:")
    for package_name, import_name in dependencies:
        if not check_dependency(package_name, import_name):
            failed += 1
    
    print("\n📦 Optional Dependencies (for development):")
    for package_name, import_name in optional_dependencies:
        check_dependency(package_name, import_name)
    
    print("\n" + "=" * 50)
    
    if failed == 0:
        print("✅ All required dependencies are installed!")
        print("\n🚀 Ready to start the API:")
        print("   python main.py")
        return 0
    else:
        print(f"❌ {failed} dependency/dependencies missing!")
        print("\n📦 Install with:")
        print("   pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
