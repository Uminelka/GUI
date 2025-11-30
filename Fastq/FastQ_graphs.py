import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import matplotlib.pyplot as plt
import statistics
import numpy as np
from fastq_reader import FastqReader

MAX_READS = 3000


class FastQCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FastQC Lite")
        self.root.geometry("800x600")

         
        self.current_path = None

         
        self.btn = tk.Button(root, text="Открыть FASTQ", command=self.open_file,
                             font=("Arial", 14))
        self.btn.pack(pady=10)

         
        self.status = tk.Label(root, text="Файл не выбран")
        self.status.pack(pady=5)

         
        self.progress = ttk.Progressbar(root, length=300)
        self.progress.pack(pady=5)

     
    def open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("FASTQ", "*.fastq *.fq *.fastq.gz *.fq.gz")]
        )
        if not path:
            return

        self.current_path = path
        self.status.config(text="Чтение данных...")

        reads = []
        self.progress["value"] = 0

        try:
            with FastqReader(path) as reader:
                for i, record in enumerate(reader.read()):
                    reads.append(record)

                    if i % 100 == 0:
                        self.progress["value"] = (i / MAX_READS) * 100
                        self.root.update()

                    if i >= MAX_READS:
                        break

            self.status.config(text=f"Загружено {len(reads)} ридов")
            self.draw_graphs(reads)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    
    def draw_graphs(self, reads):
        """
        Построение графиков FastQC:
        1) per base sequence quality
        2) per base sequence content
        3) sequence length distribution
        """
        if not reads:
            messagebox.showwarning("Нет данных", "Невозможно построить графики — нет данных")
            return

         

         
        lengths = [len(r.sequence) for r in reads]
        max_len = max(lengths)

         
        quality_per_pos = [[] for _ in range(max_len)]

         
        base_A = [0] * max_len
        base_C = [0] * max_len
        base_G = [0] * max_len
        base_T = [0] * max_len

        total_reads = len(reads)

        for r in reads:
            seq = r.sequence
            qual = r.quality

            for pos, q in enumerate(qual):
                quality_per_pos[pos].append(q)

            for pos, nt in enumerate(seq):
                if nt == "A":
                    base_A[pos] += 1
                elif nt == "C":
                    base_C[pos] += 1
                elif nt == "G":
                    base_G[pos] += 1
                elif nt == "T":
                    base_T[pos] += 1

         
        mean_quality = [np.mean(pos) if pos else 0 for pos in quality_per_pos]

         
        perc_A = [x / total_reads * 100 for x in base_A]
        perc_C = [x / total_reads * 100 for x in base_C]
        perc_G = [x / total_reads * 100 for x in base_G]
        perc_T = [x / total_reads * 100 for x in base_T]
 

        fig = plt.figure(figsize=(12, 10))

        # 1) Per base sequence quality
        ax1 = fig.add_subplot(3, 1, 1)
        ax1.plot(mean_quality, color="green")
        ax1.set_title("Per base sequence quality")
        ax1.set_xlabel("Position in read")
        ax1.set_ylabel("Mean Quality (Phred)")
        ax1.grid(True)

        # 2) Per base sequence content
        ax2 = fig.add_subplot(3, 1, 2)
        ax2.plot(perc_A, label="A", color="blue")
        ax2.plot(perc_C, label="C", color="red")
        ax2.plot(perc_G, label="G", color="orange")
        ax2.plot(perc_T, label="T", color="green")

        ax2.set_title("Per base sequence content")
        ax2.set_xlabel("Position in read")
        ax2.set_ylabel("Nucleotide (%)")
        ax2.legend()
        ax2.grid(True)

        # 3) Sequence length distribution
        ax3 = fig.add_subplot(3, 1, 3)
        ax3.hist(lengths, bins=30, color="purple")
        ax3.set_title("Sequence length distribution")
        ax3.set_xlabel("Read length")
        ax3.set_ylabel("Count")

        plt.tight_layout()
        plt.show()

 
if __name__ == "__main__":
    root = tk.Tk()
    FastQCApp(root)
    root.mainloop()

