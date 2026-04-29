import os
import zipfile
import tempfile
import time
from typing import List, Optional, Dict, Any

from langchain_core.tools import Tool
from e2b_code_interpreter import Sandbox


class CodeInterpreterTool:
    """
    A tool for executing Python code in a secure E2B sandbox,
    supporting file mounting and automatic result extraction.
    """

    def __init__(
        self,
        mount_paths: List[str],
        api_key: Optional[str] = None,
        packages: Optional[List[str]] = None,
    ):
        # Set API key if provided or ensure it exists in environment
        if api_key:
            os.environ["E2B_API_KEY"] = api_key

        if not os.getenv("E2B_API_KEY"):
            raise ValueError(
                "E2B_API_KEY must be set in environment or passed to constructor."
            )

        self.sandbox = Sandbox.create(timeout=400)
        self._install_dependencies(packages)
        self._mount_files(mount_paths)

    def _install_dependencies(self, packages: Optional[List[str]] = None):
        """
        Installs required Python libraries inside the sandbox
        by running subprocess from within sandbox Python runtime.
        Combines default + custom packages safely.
        """

        default_packages = [
            "networkx",
            "wordcloud",
            "textwrap",
            "statsmodels",
            "squarify",
            "plotly",
            "seaborn",
        ]

        combined_packages = list(set(default_packages + (packages or [])))

        install_code = f"""
import subprocess
import sys

packages = {combined_packages}

subprocess.run(
    [sys.executable, "-m", "pip", "install", "--no-cache-dir"] + packages,
)
"""
        self.sandbox.run_code(install_code)

    def _mount_files(self, mount_paths: List[str]):
        """Uploads local files to the sandbox environment."""
        for path in mount_paths:
            if not os.path.exists(path):
                print(f"Warning: Path {path} does not exist. Skipping.")
                continue

            file_name = os.path.basename(path)

            # Use binary read for universal file support
            with open(path, "rb") as file:
                self.sandbox.files.write(f"/home/user/mounted/{file_name}", file)

    def run_code(self, code: str) -> Dict[str, Any]:
        """Executes Python code and returns the execution results."""
        print(f"\n--- Executing Python ---\n{code}\n------------------------")

        execution = self.sandbox.run_code(code)

        return {
            "stdout": execution.logs.stdout,
            "stderr": execution.logs.stderr,
            "results": execution.results,
            "error": execution.error,
        }

    def tool(self) -> Tool:
        """Returns a LangChain Tool object for agent integration."""
        return Tool(
            name="python",
            description="Execute Python code in a sandboxed environment. Use this for data analysis or processing.",
            func=self.run_code,
        )

    def zip_and_close(self, output_dir: str = "./sandbox_output"):
        """
        Zips files created in the sandbox home directory, downloads,
        extracts them locally, and kills the sandbox session.
        """

        zipping_code = """
import os
import zipfile

HOME_DIR = "/home/user"
ZIP_PATH = os.path.join(HOME_DIR, "outputs.zip")

files_to_zip = [
    os.path.join(HOME_DIR, f) for f in os.listdir(HOME_DIR)
    if os.path.isfile(os.path.join(HOME_DIR, f))
    and not f.startswith(".")
    and f != "outputs.zip"
]

with zipfile.ZipFile(ZIP_PATH, "w") as zipf:
    for file_path in files_to_zip:
        zipf.write(file_path, os.path.basename(file_path))
"""

        try:
            # Run the zip script in the sandbox
            self.sandbox.run_code(zipping_code)

            # Read the zip back to the local machine
            zip_bytes = self.sandbox.files.read(
                "/home/user/outputs.zip", format="bytes"
            )

            os.makedirs(output_dir, exist_ok=True)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
                tmp_file.write(zip_bytes)
                tmp_path = tmp_file.name

            with zipfile.ZipFile(tmp_path, "r") as z:
                z.extractall(output_dir)

            os.remove(tmp_path)

            print(f"Successfully extracted sandbox outputs to: {output_dir}")

        except Exception as e:
            print(f"Error during cleanup and extraction: {e}")

        finally:
            # Wait 5 seconds before closing sandbox
            time.sleep(5)

            self.sandbox.kill()
            print("Sandbox session closed.")