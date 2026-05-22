#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any

import tkinter as tk
from tkinter import messagebox, scrolledtext


ALIASES = {
    "id_token": {
        "id_token",
        "idToken",
        "id-token",
        "id token",
    },
    "access_token": {
        "access_token",
        "accessToken",
        "access-token",
        "access token",
        "token",
    },
    "refresh_token": {
        "refresh_token",
        "refreshToken",
        "refresh-token",
        "refresh token",
    },
    "account_id": {
        "account_id",
        "accountId",
        "account-id",
        "account id",
        "sub",
        "user_id",
        "userId",
    },
    "last_refresh": {
        "last_refresh",
        "lastRefresh",
        "last-refresh",
        "last refresh",
        "updated_at",
        "updatedAt",
        "expires_at",
        "expiresAt",
    },
}


def normalize_key(key: str) -> str:
    return key.replace("-", "_").replace(" ", "_").lower()


def walk_json(value: Any):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key), item
            yield from walk_json(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_json(item)


def find_value(data: Any, output_key: str) -> str:
    aliases = {normalize_key(alias) for alias in ALIASES[output_key]}

    for key, value in walk_json(data):
        if normalize_key(key) in aliases and value is not None:
            if isinstance(value, (dict, list)):
                continue
            return str(value)

    return ""


def convert(data: Any) -> dict[str, Any]:
    return {
        "auth_mode": "chatgpt",
        "OPENAI_API_KEY": None,
        "tokens": {
            "id_token": find_value(data, "id_token"),
            "access_token": find_value(data, "access_token"),
            "refresh_token": find_value(data, "refresh_token"),
            "account_id": find_value(data, "account_id"),
        },
        "last_refresh": find_value(data, "last_refresh"),
    }


def read_input(path: str | None) -> Any:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    return json.load(sys.stdin)


def write_output(path: str | None, data: dict[str, Any]) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


def converted_text(source_text: str) -> str:
    source = json.loads(source_text)
    return json.dumps(convert(source), ensure_ascii=False, indent=2)


def run_ui() -> int:
    root = tk.Tk()
    root.title("JSON 转换工具")
    root.geometry("1000x650")
    root.minsize(780, 480)

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(1, weight=1)

    tk.Label(root, text="粘贴原始 JSON").grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))
    tk.Label(root, text="转换结果").grid(row=0, column=1, sticky="w", padx=12, pady=(12, 6))

    input_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, undo=True)
    input_box.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(0, 12))

    output_frame = tk.Frame(root)
    output_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=(0, 12))
    output_frame.columnconfigure(0, weight=1)
    output_frame.rowconfigure(1, weight=1)

    copy_button = tk.Button(output_frame, text="复制", width=8)
    copy_button.grid(row=0, column=0, sticky="e", pady=(0, 6))

    output_box = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, state="disabled")
    output_box.grid(row=1, column=0, sticky="nsew")

    status_var = tk.StringVar(value="粘贴 JSON 后点击转换。")
    status_label = tk.Label(root, textvariable=status_var, anchor="w")
    status_label.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))

    def set_output(text: str) -> None:
        output_box.configure(state="normal")
        output_box.delete("1.0", tk.END)
        output_box.insert("1.0", text)
        output_box.configure(state="disabled")

    def convert_clicked() -> None:
        source_text = input_box.get("1.0", tk.END).strip()
        if not source_text:
            messagebox.showwarning("缺少输入", "请先粘贴要转换的 JSON。")
            return

        try:
            set_output(converted_text(source_text))
        except json.JSONDecodeError as exc:
            messagebox.showerror("JSON 格式错误", str(exc))
            status_var.set("转换失败：JSON 格式错误。")
            return

        status_var.set("转换完成。")

    def copy_clicked() -> None:
        text = output_box.get("1.0", tk.END).strip()
        if not text:
            status_var.set("没有可复制的转换结果。")
            return

        root.clipboard_clear()
        root.clipboard_append(text)
        status_var.set("已复制到剪贴板。")

    convert_button = tk.Button(root, text="转换", command=convert_clicked, height=2)
    convert_button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
    copy_button.configure(command=copy_clicked)

    root.mainloop()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert arbitrary JSON into the fixed ChatGPT auth JSON format."
    )
    parser.add_argument("input", nargs="?", help="Input JSON file. Reads stdin if omitted.")
    parser.add_argument("-o", "--output", help="Output JSON file. Prints stdout if omitted.")
    parser.add_argument("--ui", action="store_true", help="Open a paste-and-convert UI.")
    args = parser.parse_args()

    stdin = getattr(sys, "stdin", None)
    if args.ui or (not args.input and (stdin is None or stdin.isatty())):
        return run_ui()

    try:
        source = read_input(args.input)
        write_output(args.output, convert(source))
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"File error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
