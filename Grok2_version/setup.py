import subprocess
import sys
import pkg_resources

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        raise RuntimeError("Python 3.8 or higher is required")

def install_requirements():
    """Install packages from requirements.txt"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def verify_installations():
    """Verify that all required packages are installed"""
    with open("requirements.txt") as f:
        requirements = [line.strip().split('==')[0] for line in f 
                       if line.strip() and not line.startswith('#')]
    
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    
    print("\nVerifying installations:")
    all_installed = True
    for package in requirements:
        if package.lower() in installed_packages:
            print(f"✓ {package} successfully installed")
        else:
            print(f"✗ {package} installation failed")
            all_installed = False
    
    return all_installed

def main():
    try:
        check_python_version()
        install_requirements()
        if verify_installations():
            print("\nEnvironment setup completed successfully!")
        else:
            print("\nSome packages failed to install. Please check the error messages above.")
    except Exception as e:
        print(f"Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 