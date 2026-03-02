import subprocess
import tempfile
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk


class DonStudioEngine(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Don Studio Engine")
        self.geometry("1200x760")
        self.minsize(920, 600)
        self.configure(bg="#151824")

        self._setup_style()
        self._build_layout()
        self._seed_templates()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Dark.TFrame", background="#151824")
        style.configure("Panel.TFrame", background="#1f2433")
        style.configure("Dark.TLabel", background="#151824", foreground="#dbe3ff", font=("Segoe UI", 10))
        style.configure(
            "Title.TLabel",
            background="#151824",
            foreground="#f3f6ff",
            font=("Segoe UI Semibold", 14),
        )
        style.configure(
            "Action.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 8),
            foreground="#ffffff",
            background="#4f7cff",
            borderwidth=0,
        )
        style.map(
            "Action.TButton",
            background=[("active", "#698fff"), ("pressed", "#426ee8")],
        )

        style.configure("Dark.TNotebook", background="#151824", borderwidth=0)
        style.configure(
            "Dark.TNotebook.Tab",
            background="#1f2433",
            foreground="#cfd8f8",
            padding=(16, 8),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Dark.TNotebook.Tab",
            background=[("selected", "#2c3550")],
            foreground=[("selected", "#ffffff")],
        )

    def _build_layout(self) -> None:
        wrapper = ttk.Frame(self, style="Dark.TFrame", padding=16)
        wrapper.pack(fill="both", expand=True)

        header = ttk.Frame(wrapper, style="Dark.TFrame")
        header.pack(fill="x", pady=(0, 12))

        ttk.Label(header, text="Don Studio Engine", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Учебная среда для Python и C++ в одном окне",
            style="Dark.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        action_row = ttk.Frame(wrapper, style="Dark.TFrame")
        action_row.pack(fill="x", pady=(0, 12))

        self.run_button = ttk.Button(
            action_row,
            text="▶ Запустить текущий код",
            style="Action.TButton",
            command=self._run_selected,
        )
        self.run_button.pack(side="left")

        ttk.Label(
            action_row,
            text="Сначала выбери вкладку Python или C++",
            style="Dark.TLabel",
        ).pack(side="left", padx=12)

        self.notebook = ttk.Notebook(wrapper, style="Dark.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        self.python_editor = self._create_editor_tab("Python")
        self.cpp_editor = self._create_editor_tab("C++")

        console_panel = ttk.Frame(wrapper, style="Panel.TFrame", padding=12)
        console_panel.pack(fill="both", expand=False, pady=(12, 0))

        ttk.Label(console_panel, text="Консоль / Логи", style="Dark.TLabel").pack(anchor="w")
        self.console = tk.Text(
            console_panel,
            height=13,
            bg="#0f1320",
            fg="#cde2ff",
            insertbackground="#ffffff",
            relief="flat",
            padx=10,
            pady=10,
            font=("Consolas", 11),
            wrap="word",
        )
        self.console.pack(fill="both", expand=True, pady=(8, 0))

    def _create_editor_tab(self, title: str) -> tk.Text:
        tab = ttk.Frame(self.notebook, style="Panel.TFrame", padding=12)
        self.notebook.add(tab, text=title)

        editor = tk.Text(
            tab,
            bg="#0f1320",
            fg="#f3f6ff",
            insertbackground="#ffffff",
            relief="flat",
            padx=14,
            pady=14,
            font=("Consolas", 12),
            undo=True,
        )
        editor.pack(fill="both", expand=True)
        return editor

    def _seed_templates(self) -> None:
        python_template = """# Python demo\nname = input(\"Как тебя зовут? \")\nprint(f\"Привет, {name}! Добро пожаловать в Don Studio Engine.\")\n"""
        cpp_template = """// C++ demo\n#include <iostream>\n\nint main() {\n    std::cout << \"Hello from Don Studio Engine!\" << std::endl;\n    return 0;\n}\n"""

        self.python_editor.insert("1.0", python_template)
        self.cpp_editor.insert("1.0", cpp_template)

    def _run_selected(self) -> None:
        self.run_button.config(state="disabled")
        active = self.notebook.tab(self.notebook.select(), "text")

        if active == "Python":
            code = self.python_editor.get("1.0", "end-1c")
            threading.Thread(target=self._run_python, args=(code,), daemon=True).start()
        else:
            code = self.cpp_editor.get("1.0", "end-1c")
            threading.Thread(target=self._run_cpp, args=(code,), daemon=True).start()

    def _log(self, text: str) -> None:
        self.console.insert("end", text + "\n")
        self.console.see("end")

    def _run_python(self, code: str) -> None:
        self.after(0, self._log, "\n[Python] Запуск...")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                path = Path(temp_dir) / "script.py"
                path.write_text(code, encoding="utf-8")

                result = subprocess.run(
                    ["python3", str(path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                output = (result.stdout or "") + (result.stderr or "")
                self.after(0, self._log, output.strip() or "[Python] Выполнение завершено без вывода.")
        except subprocess.TimeoutExpired:
            self.after(0, self._log, "[Python] Ошибка: время выполнения > 30 секунд.")
        finally:
            self.after(0, lambda: self.run_button.config(state="normal"))

    def _run_cpp(self, code: str) -> None:
        self.after(0, self._log, "\n[C++] Сборка и запуск...")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                source = Path(temp_dir) / "main.cpp"
                binary = Path(temp_dir) / "program"
                source.write_text(code, encoding="utf-8")

                compile_result = subprocess.run(
                    ["g++", str(source), "-std=c++17", "-O2", "-o", str(binary)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if compile_result.returncode != 0:
                    self.after(0, self._log, compile_result.stderr.strip() or "[C++] Ошибка компиляции.")
                    return

                run_result = subprocess.run(
                    [str(binary)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                output = (run_result.stdout or "") + (run_result.stderr or "")
                self.after(0, self._log, output.strip() or "[C++] Выполнение завершено без вывода.")
        except FileNotFoundError:
            self.after(0, self._log, "[C++] g++ не найден. Установи компилятор и попробуй снова.")
        except subprocess.TimeoutExpired:
            self.after(0, self._log, "[C++] Ошибка: время компиляции/выполнения > 30 секунд.")
        finally:
            self.after(0, lambda: self.run_button.config(state="normal"))


if __name__ == "__main__":
    app = DonStudioEngine()
    app.mainloop()
