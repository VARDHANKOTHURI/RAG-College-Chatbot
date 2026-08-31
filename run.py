import os
import sys
import uvicorn

def main():
    # Ensure current directory is in sys.path
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    print("=" * 70)
    print("      GREENWOOD INSTITUTE OF TECHNOLOGY — RAG CHATBOT SERVER      ")
    print("=" * 70)
    print("  [>] Web Application UI:  http://localhost:8000")
    print("  [>] Interactive API Docs: http://localhost:8000/docs")
    print("  [>] Health Endpoint:      http://localhost:8000/api/health")
    print("-" * 70)
    print("  Default Demo Credentials:")
    print("    * Student Account: student@college.edu | Password: Student@123")
    print("    * Admin Account:   admin@college.edu   | Password: Admin@123")
    print("=" * 70)
    print("  Press Ctrl+C to stop the server.\n")

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
