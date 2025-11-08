# turing_simulator.py
# -*- coding: utf-8 -*-
"""
Simulador visual de Máquina de Turing (versión educativa) + Probador de Expresiones Regulares
Autor: Julio Hernández (1105824) – Maquina de Turing
Requisitos: Python 3.x (Tkinter incluido en Windows/macOS; en Linux instalar: sudo apt-get install python3-tk)
Ejecución: python turing_simulator.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
from typing import Dict, Tuple, Set, List

BLANK = "_"  # Símbolo de blanco en la cinta


class TuringMachine:
    """
    Máquina de Turing determinista minimalista.
    Transiciones: dict[(estado, símbolo_lectura)] = (símbolo_escritura, movimiento, siguiente_estado)
    movimiento en {"L","R","S"}  (Left/Right/Stay)
    """
    def __init__(self, states: Set[str], input_alphabet: Set[str], tape_alphabet: Set[str],
                 transitions: Dict[Tuple[str, str], Tuple[str, str, str]],
                 start_state: str, accept_states: Set[str], reject_states: Set[str] = None):
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states
        self.reject_states = reject_states or set()
        self.reset("")

    def reset(self, input_string: str):
        self.tape: List[str] = list(input_string) if input_string else [BLANK]
        self.head = 0
        self.state = self.start_state
        self.halted = False
        self.result = None  # "ACCEPT" | "REJECT" | None

    def ensure_cell(self, index: int):
        if index < 0:
            self.tape.insert(0, BLANK)
            self.head += 1
        elif index >= len(self.tape):
            self.tape.append(BLANK)

    def step(self) -> Tuple[str, str, str]:
        """Ejecuta un paso de la máquina."""
        if self.halted:
            raise RuntimeError("La máquina ya está detenida.")

        self.ensure_cell(self.head)
        current_symbol = self.tape[self.head]
        key = (self.state, current_symbol)

        # Si no hay transición definida: decidir según el estado actual
        if key not in self.transitions:
            if self.state in self.accept_states:
                self.halted = True
                self.result = "ACCEPT"
            else:
                self.halted = True
                self.result = "REJECT"
            return (current_symbol, "S", self.state)

        # Ejecutar transición
        write, move, next_state = self.transitions[key]

        # Escribir
        self.tape[self.head] = write

        # Mover cabeza
        if move == "L":
            self.head -= 1
        elif move == "R":
            self.head += 1
        # "S" -> sin movimiento

        self.ensure_cell(self.head)

        # Cambiar estado
        self.state = next_state

        # Verificar si es estado de aceptación o rechazo
        if self.state in self.accept_states:
            self.halted = True
            self.result = "ACCEPT"
        elif self.state in self.reject_states:
            self.halted = True
            self.result = "REJECT"

        return (write, move, next_state)


# ---------- DEMOS: DFA envueltos como TM derecha-solo ----------

def build_right_moving_tm_from_dfa(name: str, alphabet: Set[str], dfa_states: Set[str],
                                   start: str, accepts: Set[str],
                                   delta: Dict[Tuple[str, str], str]) -> TuringMachine:
    """
    Construye una TM que simula un DFA moviéndose solo a la derecha.
    Al llegar a BLANCO, pasa a HALT_A o HALT_R según estado de aceptación.
    """
    tm_states = set(dfa_states) | {"HALT_A", "HALT_R"}
    tape_alphabet = set(alphabet) | {BLANK}
    transitions: Dict[Tuple[str, str], Tuple[str, str, str]] = {}

    # Transiciones del DFA -> TM
    for (q, a), q2 in delta.items():
        transitions[(q, a)] = (a, "R", q2)

    # Al encontrar BLANCO decidir aceptación
    for q in dfa_states:
        if q in accepts:
            transitions[(q, BLANK)] = (BLANK, "S", "HALT_A")
        else:
            transitions[(q, BLANK)] = (BLANK, "S", "HALT_R")

    # Estados de halt (se quedan en sí mismos)
    transitions[("HALT_A", BLANK)] = (BLANK, "S", "HALT_A")
    transitions[("HALT_R", BLANK)] = (BLANK, "S", "HALT_R")

    return TuringMachine(
        states=tm_states,
        input_alphabet=set(alphabet),
        tape_alphabet=tape_alphabet,
        transitions=transitions,
        start_state=start,
        accept_states={"HALT_A"},
        reject_states={"HALT_R"}
    )


def demo_tm_ends_with_abb() -> TuringMachine:
    # (a|b)*abb
    Σ = {"a", "b"}
    q0, q1, q2, q3 = "q0", "q1", "q2", "q3"
    dfa_states = {q0, q1, q2, q3}
    start, accepts = q0, {q3}
    δ = {
        (q0, "a"): q1, (q0, "b"): q0,
        (q1, "a"): q1, (q1, "b"): q2,
        (q2, "a"): q1, (q2, "b"): q3,
        (q3, "a"): q1, (q3, "b"): q0,
    }
    return build_right_moving_tm_from_dfa("ends_with_abb", Σ, dfa_states, start, accepts, δ)


def demo_tm_0star1star() -> TuringMachine:
    # 0*1*
    Σ = {"0", "1"}
    q0, q1, qdead = "q0", "q1", "qdead"
    dfa_states = {q0, q1, qdead}
    start, accepts = q0, {q0, q1}
    δ = {
        (q0, "0"): q0, (q0, "1"): q1,
        (q1, "1"): q1, (q1, "0"): qdead,
        (qdead, "0"): qdead, (qdead, "1"): qdead,
    }
    return build_right_moving_tm_from_dfa("0*1*", Σ, dfa_states, start, accepts, δ)


def demo_tm_ab_star() -> TuringMachine:
    # (ab)*
    Σ = {"a", "b"}
    even, a_seen, dead = "even", "a_seen", "dead"
    dfa_states = {even, a_seen, dead}
    start, accepts = even, {even}
    δ = {
        (even, "a"): a_seen, (even, "b"): dead,
        (a_seen, "b"): even, (a_seen, "a"): dead,
        (dead, "a"): dead, (dead, "b"): dead,
    }
    return build_right_moving_tm_from_dfa("(ab)*", Σ, dfa_states, start, accepts, δ)


def demo_tm_1_01_star_0() -> TuringMachine:
    # 1(01)*0
    Σ = {"0", "1"}
    q0, q1, q2, dead = "q0", "q1", "q2", "dead"
    dfa_states = {q0, q1, q2, dead}
    start, accepts = q0, {q2}
    δ = {
        (q0, "1"): q1, (q0, "0"): dead,
        (q1, "0"): q2, (q1, "1"): dead,
        (q2, "1"): q1, (q2, "0"): dead,
        (dead, "0"): dead, (dead, "1"): dead,
    }
    return build_right_moving_tm_from_dfa("1(01)*0", Σ, dfa_states, start, accepts, δ)


def demo_tm_contains_a() -> TuringMachine:
    # (a+b)*a(a+b)*  -> contiene al menos una 'a'
    Σ = {"a", "b"}
    no_a, yes_a = "no_a", "yes_a"
    dfa_states = {no_a, yes_a}
    start, accepts = no_a, {yes_a}
    δ = {
        (no_a, "a"): yes_a, (no_a, "b"): no_a,
        (yes_a, "a"): yes_a, (yes_a, "b"): yes_a,
    }
    return build_right_moving_tm_from_dfa("(a+b)*a(a+b)*", Σ, dfa_states, start, accepts, δ)


DEMO_BUILDERS = {
    "(a|b)*abb": demo_tm_ends_with_abb,
    "0*1*": demo_tm_0star1star,
    "(ab)*": demo_tm_ab_star,
    "1(01)*0": demo_tm_1_01_star_0,
    "(a+b)*a(a+b)*": demo_tm_contains_a,
}

REGEX_PRESETS = [
    (r"(a|b)*abb", "Termina con 'abb'"),
    (r"0*1*", "Ceros seguidos de unos (en ese orden)"),
    (r"(ab)*", "Repeticiones del bloque 'ab'"),
    (r"1(01)*0", "10, 1010, 101010, ..."),
    (r"(a+b)*a(a+b)*", "Contiene al menos una 'a'"),
    (r"(0|1)*10(0|1)*", "Contiene la subcadena '10'"),
    (r"a*b*a*", "Bloques de a's, b's, a's"),
    (r"(ba|ab)+", "Una o más 'ba' o 'ab'"),
    (r"1*", "Solo unos (o vacío)"),
    (r"(a)?", "Vacío o 'a'"),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Máquina de Turing + Expresiones Regulares")
        self.geometry("1200x700")
        self.configure(bg="#f5f5f7")
        self.resizable(True, True)

        self.tm = list(DEMO_BUILDERS.values())[0]()
        self.running = False

        self._setup_style()
        self._build_ui()
        self._draw_tape()

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background="#f5f5f7")
        style.configure("TLabel", background="#f5f5f7", foreground="#111827", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("State.TLabel", font=("Segoe UI", 11, "bold"), foreground="#111827")
        style.configure("Result.TLabel", font=("Segoe UI", 11, "bold"), foreground="#111827")
        style.configure("TButton", padding=4, font=("Segoe UI", 9))
        style.map("TButton",
                  background=[("active", "#dbeafe")],
                  foreground=[("active", "#111827")])
        style.configure("TLabelframe", background="#f5f5f7", foreground="#111827")
        style.configure("TLabelframe.Label", background="#f5f5f7", foreground="#111827",
                        font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        # Fila superior: cadena + demo
        top_bar = ttk.Frame(root)
        top_bar.pack(fill="x", pady=(0, 5))

        ttk.Label(top_bar, text="Cadena de entrada:", style="Header.TLabel").pack(side="left", padx=(0, 4))
        self.entry_input = ttk.Entry(top_bar, width=40)
        self.entry_input.pack(side="left", padx=(0, 14))
        self.entry_input.insert(0, "abbababb")

        ttk.Label(top_bar, text="Demo:", style="Header.TLabel").pack(side="left", padx=(0, 4))
        self.combo_demo = ttk.Combobox(top_bar, values=list(DEMO_BUILDERS.keys()),
                                       state="readonly", width=24)
        self.combo_demo.current(0)
        self.combo_demo.pack(side="left")
        self.combo_demo.bind("<<ComboboxSelected>>", self.on_change_demo)

        # Estado
        self.lbl_state = ttk.Label(root, text="Estado: —", style="State.TLabel")
        self.lbl_state.pack(anchor="w", pady=(2, 6))

        # Cinta centrada
        self.canvas = tk.Canvas(
            root,
            height=190,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#d1d5db"
        )
        self.canvas.pack(fill="x", expand=False, pady=(0, 8))

        # Controles
        controls = ttk.Frame(root)
        controls.pack(fill="x", pady=(0, 4))

        self.btn_reset = ttk.Button(controls, text="Reset", command=self.on_reset)
        self.btn_step = ttk.Button(controls, text="Paso", command=self.on_step)
        self.btn_run = ttk.Button(controls, text="Run", command=self.on_run)
        self.btn_pause = ttk.Button(controls, text="Pausa", command=self.on_pause)

        for b in (self.btn_reset, self.btn_step, self.btn_run, self.btn_pause):
            b.pack(side="left", padx=4)

        ttk.Label(controls, text="Velocidad:", style="Header.TLabel").pack(side="left", padx=(18, 4))
        self.speed = tk.DoubleVar(value=5.0)
        self.scale_speed = ttk.Scale(controls, variable=self.speed, from_=1, to=10,
                                     orient="horizontal", length=220)
        self.scale_speed.pack(side="left")

        # Resultado
        self.lbl_result = ttk.Label(root, text="Resultado: —", style="Result.TLabel")
        self.lbl_result.pack(anchor="w", pady=(0, 8))

        # Expresiones Regulares
        regex_frame = ttk.LabelFrame(root, text="Expresiones Regulares — Casos de prueba del simulador")
        regex_frame.pack(fill="both", expand=True, pady=(4, 0))

        ttk.Label(regex_frame,
                  text="Selecciona una expresión regular de prueba:",
                  style="Header.TLabel").pack(anchor="w", padx=8, pady=(6, 4))

        self.regex_list = tk.Listbox(
            regex_frame,
            height=6,
            bg="#ffffff",
            fg="#111827",
            selectbackground="#bfdbfe",
            selectforeground="#111827",
            highlightthickness=1,
            highlightbackground="#d1d5db",
            activestyle="none",
            font=("Segoe UI", 9)
        )
        for pattern, desc in REGEX_PRESETS:
            self.regex_list.insert("end", f"{pattern}  —  {desc}")
        self.regex_list.pack(fill="x", padx=8, pady=(0, 6))

        test_row = ttk.Frame(regex_frame)
        test_row.pack(fill="x", padx=8, pady=(0, 6))
        ttk.Label(test_row, text="Cadena a evaluar:", style="Header.TLabel").pack(side="left")
        self.entry_regex_test = ttk.Entry(test_row, width=40)
        self.entry_regex_test.pack(side="left", padx=(6, 8))
        self.entry_regex_test.insert(0, "abbababb")
        ttk.Button(test_row, text="Evaluar Regex Seleccionada",
                   command=self.on_eval_regex).pack(side="left")

        self.lbl_regex = ttk.Label(regex_frame, text="Resultado Regex: —", style="Result.TLabel")
        self.lbl_regex.pack(anchor="w", padx=10, pady=(2, 4))

        ttk.Label(
            regex_frame,
            text="Estas expresiones regulares se utilizan como casos de prueba para validar "
                 "el comportamiento del simulador de Máquina de Turing.",
            wraplength=1150
        ).pack(anchor="w", padx=10, pady=(0, 8))

    # ---------- Dibujo de cinta ----------
    def _draw_tape(self):
        self.canvas.delete("all")

        cell_w = 40
        cell_h = 50

        width = self.canvas.winfo_width() or 1100

        head = self.tm.head
        # mostramos un rango fijo alrededor del cabezal
        visible_cells = max(10, (width // cell_w) - 2)
        half = visible_cells // 2
        left_idx = max(0, head - half)
        right_idx = min(len(self.tm.tape) - 1, head + half)

        num_cells = right_idx - left_idx + 1
        total_width = num_cells * cell_w
        margin = max(20, (width - total_width) // 2)

        x = margin
        y = 45

        for i in range(left_idx, right_idx + 1):
            symbol = self.tm.tape[i]
            is_head = (i == head)

            rect_color = "#ffffff"
            outline = "#d1d5db"
            if is_head:
                rect_color = "#eff6ff"
                outline = "#2563eb"

            self.canvas.create_rectangle(
                x, y, x + cell_w, y + cell_h,
                fill=rect_color, outline=outline, width=2 if is_head else 1
            )
            self.canvas.create_text(
                x + cell_w / 2, y + cell_h / 2,
                text=symbol,
                fill="#111827",
                font=("Consolas", 18, "bold")
            )
            self.canvas.create_text(
                x + cell_w / 2, y + cell_h + 14,
                text=str(i),
                fill="#6b7280",
                font=("Consolas", 9)
            )
            x += cell_w

        # Flecha de la cabeza
        if left_idx <= head <= right_idx:
            head_x = margin + (head - left_idx) * cell_w + cell_w / 2
            self.canvas.create_polygon(
                head_x - 10, y - 18,
                head_x + 10, y - 18,
                head_x, y - 2,
                fill="#2563eb", outline="#2563eb"
            )

        # Actualizar etiquetas
        self.lbl_state.config(text=f"Estado: {self.tm.state}")
        res = self.tm.result or "—"
        self.lbl_result.config(text=f"Resultado: {res}")

    # ---------- Eventos ----------
    def on_change_demo(self, _evt=None):
        demo_key = self.combo_demo.get()
        builder = DEMO_BUILDERS[demo_key]
        self.tm = builder()
        self.on_reset()

    def on_reset(self):
        s = self.entry_input.get()
        bad = [ch for ch in s if ch not in self.tm.tape_alphabet]
        if bad:
            messagebox.showerror(
                "Símbolos inválidos",
                f"Símbolos fuera del alfabeto permitido {self.tm.tape_alphabet}: {set(bad)}"
            )
            return
        self.tm.reset(s)
        self.running = False
        self._draw_tape()

    def on_step(self):
        if self.tm.halted:
            self._draw_tape()
            return
        try:
            self.tm.step()
        except RuntimeError:
            # Si ya está detenida, solo refrescar
            pass
        self._draw_tape()
        self.update_idletasks()

    def on_run(self):
        self.running = True
        self._run_loop()

    def on_pause(self):
        self.running = False

    def _run_loop(self):
        if not self.running:
            return
        if not self.tm.halted:
            self.on_step()
            speed = self.speed.get()
            delay_ms = int(500 / max(1, speed))
            self.after(delay_ms, self._run_loop)
        else:
            self._draw_tape()

    def on_eval_regex(self):
        idxs = self.regex_list.curselection()
        if not idxs:
            messagebox.showinfo("Aviso", "Selecciona una expresión regular de la lista.")
            return
        pattern, desc = REGEX_PRESETS[idxs[0]]
        test_str = self.entry_regex_test.get()
        try:
            ok = re.fullmatch(pattern, test_str) is not None
        except re.error:
            messagebox.showerror("Error", "La expresión regular seleccionada es inválida.")
            return

        msg = "ACEPTADA" if ok else "RECHAZADA"
        self.lbl_regex.config(text=f"Resultado Regex: {msg}  |  {pattern}  —  {desc}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
