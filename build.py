#!/usr/bin/env python3
"""Build script for creating Snake Game binaries.

Provides a CLI interface to configure and build executables for Windows and Linux.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.resolve()
SPEC_FILE = PROJECT_ROOT / "snake_game.spec"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"


def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    result = subprocess.run(
        cmd,
        cwd=cwd or PROJECT_ROOT,
        shell=isinstance(cmd, str),
    )
    return result.returncode == 0


def check_dependencies():
    """Check if required build tools are installed."""
    print("Checking dependencies...")
    
    missing = []
    
    try:
        import pyinstaller
    except ImportError:
        missing.append("pyinstaller")
    
    if missing:
        print(f"Missing: {', '.join(missing)}")
        print("Install with: pip install pyinstaller")
        return False
    
    print("Dependencies OK")
    return True


def clean_build_dirs():
    """Clean previous build outputs."""
    print("Cleaning build directories...")
    
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
            print(f"  Removed {d}")
    
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
        print(f"  Removed {SPEC_FILE}")
    
    print("Clean complete")


def create_spec(
    onedir: bool = False,
    console: bool = False,
    icon: str = None,
    name: str = "snake_game",
    version: str = "1.0.0",
):
    """Generate PyInstaller spec file content."""
    
    a = Analysis(
        ["run_game.py"],
        pathex=[str(PROJECT_ROOT)],
        binaries=[],
        datas=[],
        hiddenimports=[
            "pygame",
            "numpy",
        ],
        hookspath=[],
        hooksconfig={},
        runtime_hooks=[],
        excludes=[],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=None,
        noarchive=False,
    )
    
    exe = EXE(
        a,
        [],
        exclude_binaries=True,
        name=name,
        version=version,
        console=console,
        icon=icon,
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        a.zip_dependencies,
        a.binaries,
        exclude_binaries=True,
        name=name if onedir else None,
    )
    
    returngrm = '''
app = BUNDLE(
    coll,
    name='Snake Game.exe' if sys.platform == 'win32' else 'Snake Game.app',
    icon=%s,
    version='%s',
)
''' % (f"'{icon}'" if icon else "None", version)
    
    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_game.py'],
    pathex=['{PROJECT_ROOT}'],
    binaries=[],
    datas=[],
    hiddenimports=['pygame', 'numpy'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    exclude_binaries=True,
    name='{name}',
    console={console},
    icon={f"'{icon}'" if icon else "None"},
    version='{version}',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    a.zip_dependencies,
    exclude_binaries=True,
    name='{name}' if {onedir} else None,
)

app = BUNDLE(
    coll,
    name='Snake Game.exe' if sys.platform == 'win32' else 'Snake Game.app',
    icon={f"'{icon}'" if icon else "None"},
    version='{version}',
)
'''
    
    with open(SPEC_FILE, "w") as f:
        f.write(spec_content)
    
    print(f"Created spec file: {SPEC_FILE}")


def build_binary(
    onedir: bool = False,
    clean: bool = True,
):
    """Run PyInstaller to build the binary."""
    
    if clean:
        clean_build_dirs()
    
    print(f"Building {'onedir' if onedir else 'onefile'} binary...")
    
    cmd = ["pyinstaller", str(SPEC_FILE)]
    if onedir:
        cmd.append("--onedir")
    else:
        cmd.append("--onefile")
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    if result.returncode != 0:
        print("Build FAILED")
        return False
    
    print("Build complete!")
    return True


def list_outputs():
    """List built binaries."""
    print("\n=== Built Binaries ===")
    
    if not DIST_DIR.exists():
        print("No dist directory found")
        return
    
    for item in DIST_DIR.iterdir():
        print(f"\n{item.name}/")
        for sub in item.iterdir():
            if sub.is_file() and sub.stat().st_mode & 0o111:
                size = sub.stat().st_size
                size_str = f"{size // 1024} KB" if size < 1024*1024 else f"{size / 1024 / 1024:.1f} MB"
                print(f"  {sub.name} ({size_str})")


def get_default_name() -> str:
    """Get default binary name based on platform."""
    return "snake_game"


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Build Snake Game binaries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                    # Interactive mode
  python build.py --windows         # Build Windows onefile
  python build.py --linux --onedir  # Build Linux onedir
  python build.py --clean           # Clean build dirs
  python build.py --list            # List built binaries
        """,
    )
    
    parser.add_argument(
        "--windows", "-w",
        action="store_true",
        help="Build for Windows",
    )
    parser.add_argument(
        "--linux", "-l",
        action="store_true",
        help="Build for Linux",
    )
    parser.add_argument(
        "--onedir", "-d",
        action="store_true",
        help="Create directory bundle (default: onefile)",
    )
    parser.add_argument(
        "--console", "-c",
        action="store_true",
        help="Show console window (default: no console)",
    )
    parser.add_argument(
        "--name", "-n",
        default=None,
        help="Binary name (default: snake_game)",
    )
    parser.add_argument(
        "--icon", "-i",
        default=None,
        help="Icon file (.ico for Windows, .icns for macOS)",
    )
    parser.add_argument(
        "--version", "-v",
        default="1.0.0",
        help="Version string",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build directories before building",
    )
    parser.add_argument(
        "--list", "-ls",
        action="store_true",
        help="List built binaries",
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_outputs()
        return
    
    if not check_dependencies():
        sys.exit(1)
    
    if args.windows or args.linux:
        binary_name = args.name or get_default_name()
        
        if args.windows:
            binary_name += ".exe"
        
        create_spec(
            onedir=args.onedir,
            console=args.console,
            icon=args.icon,
            name=binary_name,
            version=args.version,
        )
        
        build_binary(onedir=args.onedir, clean=args.clean)
        list_outputs()
        return
    
    print("=" * 50)
    print("  Snake Game Build Tool")
    print("=" * 50)
    print()
    
    options = {
        "windows": "Build Windows binary",
        "linux": "Build Linux binary",
        "onedir": "Directory bundle (vs onefile)",
        "console": "Show console window",
        "clean": "Clean before build",
    }
    
    selected = {k: v for k, v in options.items()}
    
    def print_menu():
        print("\n=== Build Options ===")
        for i, (k, v) in enumerate(options.items(), 1):
            marker = "[*]" if k in selected else "[ ]"
            print(f"  {i}. {marker} {v}")
        print()
        print("  B. Build")
        print("  Q. Quit")
        print()
    
    while True:
        print_menu()
        choice = input("Select option: ").strip().lower()
        
        if choice == "q":
            print("Goodbye!")
            return
        
        if choice == "b":
            break
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                key = list(options.keys())[idx]
                if key in selected:
                    selected.pop(key)
                else:
                    selected[key] = True
    
    binary_name = input(f"Binary name [{get_default_name()}]: ").strip()
    if not binary_name:
        binary_name = get_default_name()
    
    version = input("Version [1.0.0]: ").strip() or "1.0.0"
    
    icon_path = input("Icon file (optional): ").strip()
    
    create_spec(
        onedir="onedir" in selected,
        console="console" in selected,
        icon=icon_path or None,
        name=binary_name,
        version=version,
    )
    
    build_binary(onedir="onedir" in selected, clean="clean" in selected)
    list_outputs()


if __name__ == "__main__":
    main()