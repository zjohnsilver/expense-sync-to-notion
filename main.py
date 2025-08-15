import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--streamlit":
        streamlit_app_path = Path(__file__).parent / "src" / "streamlit_app" / "app.py"
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(streamlit_app_path)]
        )
    else:
        print("💰 Expense Sync to Notion")
        print("=" * 40)
        print("Usage options:")
        print(
            "  python main.py --streamlit  # Launch interactive Streamlit interface (recommended)"
        )
        print(
            "  python main.py --cli        # Run CLI version (direct sync without validation)"
        )
        print("")
        print("🚀 Launching Streamlit interface...")

        streamlit_app_path = Path(__file__).parent / "src" / "streamlit_app" / "app.py"
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(streamlit_app_path)]
        )


if __name__ == "__main__":
    main()
