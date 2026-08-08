#!/usr/bin/env python3
"""BatchRename — 批量重命名工具 / Batch File Renamer"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os, re, datetime

TR = {
    "zh": {
        "title": "BatchRename · 批量重命名",
        "add_files": "📁 添加文件",
        "clear_list": "🧹 清空列表",
        "preview": "👁 预览",
        "apply": "✅ 应用重命名",
        "undo": "↩ 撤销",
        "seq": "序号",
        "date": "日期",
        "replace": "替换",
        "regex": "正则",
        "prefix": "前缀:",
        "suffix": "后缀:",
        "start_num": "起始序号:",
        "date_fmt": "日期格式",
        "old_str": "查找:",
        "new_str": "替换为:",
        "pattern": "正则:",
        "replacement": "替换:",
        "help_text": ("BatchRename 使用说明\n\n"
            "1. 点击「📁 添加文件」选择要重命名的文件\n"
            "2. 选择重命名模式（序号/日期/替换/正则）\n"
            "3. 填写参数后点「👁 预览」查看效果\n"
            "4. 确认无误后点「✅ 应用重命名」\n"
            "5. 误操作可用「↩ 撤销」恢复\n\n"
            "预览功能确保不会误改文件。"),
        "disclaimer": ("⚠️ 免责声明\n\n"
            "1. BatchRename 批量修改文件名，请务必先预览再应用！\n"
            "2. 误操作可能导致文件无法找回，建议操作前备份重要文件。\n"
            "3. 本软件按原样（AS-IS）提供，不提供任何明示或暗示的担保。\n"
            "4. 开发者不对因使用本软件造成的任何文件损失或数据丢失承担责任。\n"
            "5. 撤销功能仅限最近一次批量操作，多次操作后无法回溯。\n"
            "6. 使用者须遵守所在地法律法规。\n"
            "7. 不用本工具批量修改系统文件或程序目录。\n\n"
            "© 永远的兰兰"),
        "about": ("BatchRename v1.0\n\n批量重命名工具\n"
            "Python 3 + tkinter\n单文件 ~10MB\n\n"
            "GitHub: https://github.com/podcatcher962/BatchRename\n© 永远的兰兰"),
    },
    "en": {
        "title": "BatchRename · File Renamer",
        "add_files": "📁 Add Files",
        "clear_list": "🧹 Clear",
        "preview": "👁 Preview",
        "apply": "✅ Apply",
        "undo": "↩ Undo",
        "seq": "Sequence",
        "date": "Date",
        "replace": "Replace",
        "regex": "Regex",
        "prefix": "Prefix:",
        "suffix": "Suffix:",
        "start_num": "Start num:",
        "date_fmt": "Format",
        "old_str": "Find:",
        "new_str": "Replace:",
        "pattern": "Pattern:",
        "replacement": "Replace:",
        "help_text": ("BatchRename Help\n\n"
            "1. Click '📁 Add Files' to select files\n"
            "2. Choose rename mode\n"
            "3. Set params and click '👁 Preview'\n"
            "4. Click '✅ Apply' when ready\n"
            "5. Use '↩ Undo' to revert\n\n"
            "Always preview first!"),
        "disclaimer": ("⚠️ Disclaimer\n\n"
            "1. Always preview before applying!\n"
            "2. Misoperation may cause unrecoverable file loss. Backup first.\n"
            "3. Provided AS-IS without warranty of any kind.\n"
            "4. Developer not liable for any file loss or data damage.\n"
            "5. Undo only works for the last batch operation.\n"
            "6. Users must comply with local laws.\n"
            "7. Do NOT use on system files or program directories.\n\n"
            "© forever-chitanda"),
        "about": ("BatchRename v1.0\n\nBatch File Renamer\n"
            "Python 3 + tkinter\nSingle-file ~10MB\n\n"
            "GitHub: https://github.com/podcatcher962/BatchRename\n© forever-chitanda"),
    },
}

class BatchRename:
    def __init__(self):
        self.root = tk.Tk()
        self.lang = "zh"
        self.files = []  # list of full paths
        self.undo_stack = []  # [(old_path, new_path), ...]
        self.root.title("BatchRename")
        self.root.geometry("700x650")
        self.root.minsize(500, 500)
        self.root.configure(bg="#F5F5F5")
        self.accent = "#7C4DFF"
        self._build_menu()
        self._build_ui()
        self._toggle_lang()
        self.root.mainloop()

    def _t(self, k): return TR[self.lang].get(k, k)

    def _build_menu(self):
        mb = tk.Menu(self.root)
        hm = tk.Menu(mb, tearoff=0)
        hm.add_command(label=self._t("help_text")[:10], command=lambda: messagebox.showinfo("Help", self._t("help_text")))
        hm.add_command(label=self._t("disclaimer")[:10], command=lambda: messagebox.showinfo("Disclaimer", self._t("disclaimer")))
        hm.add_separator()
        hm.add_command(label=self._t("about")[:10], command=lambda: messagebox.showinfo("About", self._t("about")))
        mb.add_cascade(label="Help" if self.lang == "en" else "帮助", menu=hm)
        self.root.config(menu=mb)

    def _build_ui(self):
        # Title
        tb = tk.Frame(self.root, bg=self.accent, height=42)
        tb.pack(fill=tk.X, padx=8, pady=(8, 0))
        tb.pack_propagate(False)
        self.title_lbl = tk.Label(tb, text="", font=('Microsoft YaHei UI', 12, 'bold'), fg="white", bg=self.accent)
        self.title_lbl.pack(side=tk.LEFT, padx=(16, 4), pady=8)
        tk.Label(tb, text="永远的兰兰", font=('Microsoft YaHei UI', 8), fg="#D1C4E9", bg=self.accent).pack(side=tk.LEFT, pady=8)
        self.lang_btn = tk.Button(tb, text="中/EN", font=('Microsoft YaHei UI', 9, 'bold'), bg="#4A148C", fg="white",
                                   relief=tk.FLAT, cursor="hand2", command=self._toggle_lang, padx=10, pady=3)
        self.lang_btn.pack(side=tk.RIGHT, padx=12, pady=8)

        card = tk.Frame(self.root, bg="#FFF")
        card.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # File list
        lf = tk.Frame(card, bg="#FFF")
        lf.pack(fill=tk.X, padx=12, pady=(12, 4))
        tk.Label(lf, text="📂", font=('Microsoft YaHei UI', 11, 'bold'), bg="#FFF", fg=self.accent).pack(side=tk.LEFT)
        self.file_count = tk.Label(lf, text="", font=('Microsoft YaHei UI', 10), bg="#FFF", fg="#757575")
        self.file_count.pack(side=tk.LEFT, padx=4)
        self.add_btn = tk.Button(lf, text="", font=('Microsoft YaHei UI', 10, 'bold'),
            bg=self.accent, fg="white", relief=tk.FLAT, cursor="hand2", command=self._add_files, padx=14, pady=5)
        self.add_btn.pack(side=tk.RIGHT, padx=2)
        self.clear_btn = tk.Button(lf, text="", font=('Microsoft YaHei UI', 10, 'bold'),
            bg="#FF5252", fg="white", relief=tk.FLAT, cursor="hand2", command=self._clear_files, padx=14, pady=5)
        self.clear_btn.pack(side=tk.RIGHT, padx=2)

        # File listbox
        list_frame = tk.Frame(card, bg="#FFF")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)
        self.file_list = tk.Listbox(list_frame, font=('Consolas', 10), bg="#F8F4FF", fg="#212121",
            selectbackground=self.accent, selectforeground="white", relief=tk.FLAT, bd=1, height=8)
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_list.yview)
        self.file_list.configure(yscrollcommand=scroll.set)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Mode tabs
        mode_frame = tk.Frame(card, bg="#F3E5FF")
        mode_frame.pack(fill=tk.X, padx=12, pady=(8, 4))
        self.mode_var = tk.StringVar(value="seq")
        self.mode_btns = {}
        for m in ["seq", "date", "replace", "regex"]:
            btn = tk.Button(mode_frame, text="", font=('Microsoft YaHei UI', 9, 'bold'),
                bg="#FFF", fg=self.accent, relief=tk.FLAT, cursor="hand2",
                command=lambda x=m: self._switch_mode(x), padx=12, pady=5)
            btn.pack(side=tk.LEFT, padx=2, pady=3)
            self.mode_btns[m] = btn

        # Params frame
        self.params_frame = tk.Frame(card, bg="#FFF")
        self.params_frame.pack(fill=tk.X, padx=12, pady=4)

        # Seq params
        self.seq_frame = tk.Frame(self.params_frame, bg="#FFF")
        tk.Label(self.seq_frame, text="", bg="#FFF", fg="#757575", font=('Microsoft YaHei UI', 10)).pack(side=tk.LEFT)
        self.prefix_lbl = tk.Label(self.seq_frame, text="", bg="#FFF", fg="#757575", font=('Microsoft YaHei UI', 10))
        self.prefix_lbl.pack(side=tk.LEFT, padx=4)
        self.prefix_entry = tk.Entry(self.seq_frame, font=('Consolas', 10), width=12, bg="#F8F4FF", relief=tk.FLAT, bd=1)
        self.prefix_entry.insert(0, "file_")
        self.prefix_entry.pack(side=tk.LEFT, padx=4)
        self.suffix_lbl = tk.Label(self.seq_frame, text="", bg="#FFF", fg="#757575", font=('Microsoft YaHei UI', 10))
        self.suffix_lbl.pack(side=tk.LEFT, padx=4)
        self.suffix_entry = tk.Entry(self.seq_frame, font=('Consolas', 10), width=8, bg="#F8F4FF", relief=tk.FLAT, bd=1)
        self.suffix_entry.pack(side=tk.LEFT, padx=4)
        self.start_lbl = tk.Label(self.seq_frame, text="", bg="#FFF", fg="#757575", font=('Microsoft YaHei UI', 10))
        self.start_lbl.pack(side=tk.LEFT, padx=(20, 4))
        self.start_entry = tk.Entry(self.seq_frame, font=('Consolas', 10), width=5, bg="#F8F4FF", relief=tk.FLAT, bd=1)
        self.start_entry.insert(0, "1")
        self.start_entry.pack(side=tk.LEFT, padx=4)

        # Date params
        self.date_frame = tk.Frame(self.params_frame, bg="#FFF")
        tk.Label(self.date_frame, text="", bg="#FFF", fg="#757575", font=('Microsoft YaHei UI', 10)).pack(side=tk.LEFT)
        self.date_fmt_var = tk.StringVar(value="%Y%m%d")
        date_fmts = [("%Y%m%d", "20260808"), ("%Y-%m-%d", "2026-08-08"), ("%Y%m%d_%H%M", "20260808_2100")]
        self.date_combo = ttk.Combobox(self.date_frame, textvariable=self.date_fmt_var, values=[d[1] for d in date_fmts],
            state="readonly", width=15, font=('Consolas', 10))
        self.date_combo.pack(side=tk.LEFT, padx=4)
        self.date_fmt_label = tk.Label(self.date_frame, text="", bg="#FFF", fg="#757575", font=('Microsoft YaHei UI', 10))
        self.date_fmt_label.pack(side=tk.LEFT, padx=4)
        self.date_prefix = tk.Entry(self.date_frame, font=('Consolas', 10), width=10, bg="#F8F4FF", relief=tk.FLAT, bd=1)
        self.date_prefix.pack(side=tk.LEFT, padx=4)

        # Replace params
        self.replace_frame = tk.Frame(self.params_frame, bg="#FFF")
        tk.Label(self.replace_frame, text="", bg="#FFF", fg="#757575", font=('Microsoft YaHei UI', 10)).pack(side=tk.LEFT)
        self.old_entry = tk.Entry(self.replace_frame, font=('Consolas', 10), width=14, bg="#FFF0F0", relief=tk.FLAT, bd=1)
        self.old_entry.pack(side=tk.LEFT, padx=4)
        self.new_label = tk.Label(self.replace_frame, text="→", bg="#FFF", fg=self.accent, font=('Consolas', 10))
        self.new_label.pack(side=tk.LEFT, padx=4)
        self.new_entry = tk.Entry(self.replace_frame, font=('Consolas', 10), width=14, bg="#F0FFF0", relief=tk.FLAT, bd=1)
        self.new_entry.pack(side=tk.LEFT, padx=4)

        # Regex params
        self.regex_frame = tk.Frame(self.params_frame, bg="#FFF")
        tk.Label(self.regex_frame, text="", bg="#FFF", fg="#757575", font=('Microsoft YaHei UI', 10)).pack(side=tk.LEFT)
        self.pattern_entry = tk.Entry(self.regex_frame, font=('Consolas', 10), width=16, bg="#FFF0F0", relief=tk.FLAT, bd=1)
        self.pattern_entry.insert(0, r"(\d+)")
        self.pattern_entry.pack(side=tk.LEFT, padx=4)
        self.repl_label = tk.Label(self.regex_frame, text="→", bg="#FFF", fg=self.accent, font=('Consolas', 10))
        self.repl_label.pack(side=tk.LEFT, padx=4)
        self.repl_entry = tk.Entry(self.regex_frame, font=('Consolas', 10), width=12, bg="#F0FFF0", relief=tk.FLAT, bd=1)
        self.repl_entry.insert(0, r"\1")
        self.repl_entry.pack(side=tk.LEFT, padx=4)
        self._switch_mode("seq")

        # Preview area
        prev_frame = tk.Frame(card, bg="#F3E5FF")
        prev_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)
        self.preview_list = tk.Listbox(prev_frame, font=('Consolas', 10), bg="#F0FFF0", fg="#2E7D32",
            selectbackground="#C8E6C9", relief=tk.FLAT, bd=1, height=8, state=tk.DISABLED)
        prev_scroll = tk.Scrollbar(prev_frame, orient=tk.VERTICAL, command=self.preview_list.yview)
        self.preview_list.configure(yscrollcommand=prev_scroll.set)
        self.preview_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        prev_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Action buttons
        bf = tk.Frame(card, bg="#FFF")
        bf.pack(fill=tk.X, padx=12, pady=(4, 12))
        self.preview_btn = tk.Button(bf, text="", font=('Microsoft YaHei UI', 10, 'bold'),
            bg="#FF9100", fg="white", relief=tk.FLAT, cursor="hand2", command=self._preview, padx=16, pady=6)
        self.preview_btn.pack(side=tk.LEFT, padx=3)
        self.apply_btn = tk.Button(bf, text="", font=('Microsoft YaHei UI', 10, 'bold'),
            bg="#43A047", fg="white", relief=tk.FLAT, cursor="hand2", command=self._apply, padx=16, pady=6)
        self.apply_btn.pack(side=tk.LEFT, padx=3)
        self.undo_btn = tk.Button(bf, text="", font=('Microsoft YaHei UI', 10, 'bold'),
            bg="#448AFF", fg="white", relief=tk.FLAT, cursor="hand2", command=self._undo, padx=16, pady=6)
        self.undo_btn.pack(side=tk.RIGHT, padx=3)

    def _switch_mode(self, mode):
        self.mode_var.set(mode)
        for m, btn in self.mode_btns.items():
            btn.config(bg="#FFF" if m != mode else self.accent, fg=self.accent if m != mode else "#FFF")
        for fm in [self.seq_frame, self.date_frame, self.replace_frame, self.regex_frame]:
            fm.pack_forget()
        if mode == "seq": self.seq_frame.pack(fill=tk.X, pady=2)
        elif mode == "date": self.date_frame.pack(fill=tk.X, pady=2)
        elif mode == "replace": self.replace_frame.pack(fill=tk.X, pady=2)
        elif mode == "regex": self.regex_frame.pack(fill=tk.X, pady=2)

    def _add_files(self):
        files = filedialog.askopenfilenames(title="Select files to rename")
        if files:
            self.files = list(files)
            self._refresh_list()

    def _clear_files(self):
        self.files = []
        self._refresh_list()
        self.preview_list.config(state=tk.NORMAL)
        self.preview_list.delete(0, tk.END)
        self.preview_list.config(state=tk.DISABLED)

    def _refresh_list(self):
        self.file_list.delete(0, tk.END)
        for f in self.files:
            self.file_list.insert(tk.END, os.path.basename(f))
        self.file_count.config(text=f"({len(self.files)} 个文件)" if self.lang == "zh" else f"({len(self.files)} files)")

    def _get_new_names(self):
        mode = self.mode_var.get()
        names = []
        if mode == "seq":
            prefix = self.prefix_entry.get()
            suffix = self.suffix_entry.get()
            try: start = int(self.start_entry.get() or "1")
            except: start = 1
            for i, f in enumerate(self.files):
                ext = os.path.splitext(f)[1]
                names.append(f"{prefix}{start+i:03d}{suffix}{ext}")
        elif mode == "date":
            fmt = self.date_fmt_var.get()
            prefix = self.date_prefix.get()
            now = datetime.datetime.now()
            date_str = now.strftime(fmt)
            for i, f in enumerate(self.files):
                ext = os.path.splitext(f)[1]
                seq = f"_{i+1:02d}" if len(self.files) > 1 else ""
                names.append(f"{prefix}{date_str}{seq}{ext}")
        elif mode == "replace":
            old = self.old_entry.get()
            new = self.new_entry.get()
            for f in self.files:
                name = os.path.basename(f)
                names.append(name.replace(old, new))
        elif mode == "regex":
            pat = self.pattern_entry.get()
            rep = self.repl_entry.get()
            for f in self.files:
                try:
                    names.append(re.sub(pat, rep, os.path.basename(f)))
                except:
                    names.append("(invalid regex)")
        return names

    def _preview(self):
        if not self.files:
            return
        names = self._get_new_names()
        self.preview_list.config(state=tk.NORMAL)
        self.preview_list.delete(0, tk.END)
        for old, new in zip(self.files, names):
            self.preview_list.insert(tk.END, f"{os.path.basename(old)}  →  {new}")
        self.preview_list.config(state=tk.DISABLED)

    def _apply(self):
        if not self.files:
            return
        names = self._get_new_names()
        if not messagebox.askyesno(self._t("apply"), "确认应用重命名?" if self.lang == "zh" else "Confirm rename?"):
            return
        applied = []
        for old_path, new_name in zip(self.files, names):
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                applied.append((new_path, old_path))  # reverse for undo
            except Exception as e:
                messagebox.showerror("Error", str(e))
                # Undo what we've done
                for np, op in reversed(applied):
                    try: os.rename(np, op)
                    except: pass
                return
        self.undo_stack.append(applied)
        self.files = [p[0] for p in applied]
        self._refresh_list()
        messagebox.showinfo(self._t("apply"), f"{len(applied)} 个文件已重命名" if self.lang == "zh" else f"{len(applied)} files renamed")

    def _undo(self):
        if not self.undo_stack:
            return
        batch = self.undo_stack.pop()
        for new_path, old_path in reversed(batch):
            try: os.rename(new_path, old_path)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
        self.files = [p[1] for p in batch]
        self._refresh_list()

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        self.root.title(self._t("title"))
        self.title_lbl.config(text=self._t("title"))
        self.lang_btn.config(text="EN/中" if self.lang == "zh" else "中/EN")
        self.add_btn.config(text=self._t("add_files"))
        self.clear_btn.config(text=self._t("clear_list"))
        self.preview_btn.config(text=self._t("preview"))
        self.apply_btn.config(text=self._t("apply"))
        self.undo_btn.config(text=self._t("undo"))
        for m, btn in self.mode_btns.items(): btn.config(text=self._t(m))
        self.prefix_lbl.config(text=self._t("prefix"))
        self.suffix_lbl.config(text=self._t("suffix"))
        self.start_lbl.config(text=self._t("start_num"))
        self.date_fmt_label.config(text=self._t("date_fmt"))
        self.old_label.config(text=self._t("old_str")) if hasattr(self, 'old_label') else None
        # Use set for combobox labels
        try: self.date_combo.set(self._get_date_fmt_example())
        except: pass
        self._refresh_list()
        self._build_menu()

    def _get_date_fmt_example(self):
        now = datetime.datetime.now()
        return self.date_fmt_var.get() if self.lang == "zh" else now.strftime(self.date_fmt_var.get())

if __name__ == "__main__":
    BatchRename()
