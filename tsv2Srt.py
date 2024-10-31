import tkinter as tk
from tkinter import filedialog, messagebox

def convert_tsv_to_srt(tsv_file, srt_file):
    with open(tsv_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(srt_file, 'w', encoding='utf-8') as f:
        for index, line in enumerate(lines):
            start, end, text = line.strip().split('\t')
            f.write(f"{index + 1}\n")
            f.write(f"{start.replace('.', ',')} --> {end.replace('.', ',')}\n")
            f.write(f"{text}\n\n")

def select_tsv_file():
    tsv_file = filedialog.askopenfilename(title="Selecciona un archivo TSV", filetypes=[("TSV files", "*.tsv")])
    if tsv_file:
        srt_file = filedialog.asksaveasfilename(defaultextension=".srt", title="Guardar como", filetypes=[("SRT files", "*.srt")])
        if srt_file:
            try:
                convert_tsv_to_srt(tsv_file, srt_file)
                messagebox.showinfo("Éxito", "Conversión completada con éxito.")
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

def main():
    root = tk.Tk()
    root.title("Convertidor de TSV a SRT")
    root.geometry("300x150")

    label = tk.Label(root, text="Convierte archivos TSV a SRT", padx=10, pady=10)
    label.pack()

    convert_button = tk.Button(root, text="Seleccionar archivo TSV", command=select_tsv_file)
    convert_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
