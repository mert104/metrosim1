import heapq
from collections import deque, defaultdict
import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Dict, Tuple


class Istasyon:
    def __init__(self, idx: str, ad: str, hat: str, renk: str, x: float = 0.0, y: float = 0.0):
        self.idx = idx
        self.ad = ad
        self.hat = hat
        self.renk = renk
        self.x = x
        self.y = y
        self.komsular: List[Tuple['Istasyon', int]] = []

    def komsu_ekle(self, istasyon: 'Istasyon', sure: int):
        self.komsular.append((istasyon, sure))


class MetroAgi:
    def __init__(self):
        self.istasyonlar: Dict[str, Istasyon] = {}
        self.hatlar: Dict[str, List[Istasyon]] = defaultdict(list)
        self.delays: Dict[Tuple[str, str], int] = {}

    def istasyon_ekle(self, idx: str, ad: str, hat: str, renk: str, x: float = 0.0, y: float = 0.0) -> None:
        if idx not in self.istasyonlar:
            istasyon = Istasyon(idx, ad, hat, renk, x, y)
            self.istasyonlar[idx] = istasyon
            self.hatlar[hat].append(istasyon)

    def baglanti_ekle(self, istasyon1_id: str, istasyon2_id: str, sure: int) -> None:
        istasyon1 = self.istasyonlar[istasyon1_id]
        istasyon2 = self.istasyonlar[istasyon2_id]
        istasyon1.komsu_ekle(istasyon2, sure)
        istasyon2.komsu_ekle(istasyon1, sure)

    def en_az_aktarma_bul(self, baslangic_id: str, hedef_id: str) -> Optional[List[Istasyon]] :
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None

        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]

        kuyruk = deque([(baslangic, [baslangic])])
        ziyaret_edildi = set([baslangic])

        while kuyruk:
            istasyon, yol = kuyruk.popleft()
            if istasyon == hedef:
                return yol

            for komsu, _ in istasyon.komsular:
                if komsu not in ziyaret_edildi:
                    ziyaret_edildi.add(komsu)
                    kuyruk.append((komsu, yol + [komsu]))

        return None

    def en_hizli_rota_bul(self, baslangic_id: str, hedef_id: str) -> Optional[Tuple[List[Istasyon], int]]:
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None

        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]
        g_score = {baslangic: 0}
        pq = [(0, id(baslangic), baslangic, [baslangic])]

        while pq:
            f_deger, _, current_station, yol = heapq.heappop(pq)
            current_sure = g_score[current_station]

            if current_station == hedef:
                return (yol, current_sure)

            for komsu, edge_sure in current_station.komsular:
                tentative_g = current_sure + edge_sure

                if (komsu not in g_score) or (tentative_g < g_score[komsu]):
                    g_score[komsu] = tentative_g
                    h_deger = 0
                    f_komsu = tentative_g + h_deger
                    heapq.heappush(pq, (f_komsu, id(komsu), komsu, yol + [komsu]))

        return None

    @staticmethod
    def print_route(rota: List[Istasyon]) -> str:
        if not rota:
            return "Rota yok."
        output_names = []
        for i, ist in enumerate(rota):
            if i == 0:
                output_names.append(ist.ad)
            else:
                if ist.ad != rota[i-1].ad:
                    output_names.append(ist.ad)
                else:
                    output_names.append(f"({ist.hat})")
        return " -> ".join(output_names)


def run_gui(metro_obj: MetroAgi):
    window = tk.Tk()
    window.title("Metro Simulation")

    tk.Label(window, text="Başlangıç İstasyonu:").grid(row=0, column=0)
    tk.Label(window, text="Hedef İstasyon:").grid(row=1, column=0)

    start_var = tk.StringVar()
    end_var = tk.StringVar()

    station_ids = list(metro_obj.istasyonlar.keys())
    combo_start = ttk.Combobox(window, textvariable=start_var, values=station_ids)
    combo_start.grid(row=0, column=1)
    combo_end = ttk.Combobox(window, textvariable=end_var, values=station_ids)
    combo_end.grid(row=1, column=1)

    result_label = tk.Label(window, text="")
    result_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def find_routes():
        s_id = start_var.get()
        e_id = end_var.get()
        if not s_id or not e_id:
            return
        bfs_route = metro_obj.en_az_aktarma_bul(s_id, e_id)
        a_star_route = metro_obj.en_hizli_rota_bul(s_id, e_id)
        result_text = ""
        if bfs_route:
            result_text += "BFS (En Az Durak): " + MetroAgi.print_route(bfs_route) + "\n"
        if a_star_route:
            a_route, a_cost = a_star_route
            result_text += f"A* (En Hızlı): {MetroAgi.print_route(a_route)} (Süre: {a_cost})\n"
        result_label.config(text=result_text)

    tk.Button(window, text="Rota Bul", command=find_routes).grid(row=2, column=0, columnspan=2, pady=5)

    window.mainloop()


if __name__ == "__main__":
    metro = MetroAgi()

    # İstasyonları ekle
    metro.istasyon_ekle("K1", "Kızılay", "Kırmızı Hat", "Kırmızı", 0, 0)
    metro.istasyon_ekle("K2", "Ulus", "Kırmızı Hat", "Kırmızı", 1, 1)
    metro.istasyon_ekle("K3", "Demetevler", "Kırmızı Hat", "Kırmızı", 2, 2)
    metro.istasyon_ekle("K4", "OSB", "Kırmızı Hat", "Kırmızı", 3, 3)

    metro.istasyon_ekle("M1", "AŞTİ", "Mavi Hat", "Mavi", -1, 0)
    metro.istasyon_ekle("M2", "Kızılay", "Mavi Hat", "Mavi", 0, 0)
    metro.istasyon_ekle("M3", "Sıhhiye", "Mavi Hat", "Mavi", 0, 1)
    metro.istasyon_ekle("M4", "Gar", "Mavi Hat", "Mavi", 1, 2)

    metro.istasyon_ekle("T1", "Batıkent", "Turuncu Hat", "Turuncu", 2, 1)
    metro.istasyon_ekle("T2", "Demetevler", "Turuncu Hat", "Turuncu", 2, 2)
    metro.istasyon_ekle("T3", "Gar", "Turuncu Hat", "Turuncu", 1, 2)
    metro.istasyon_ekle("T4", "Keçiören", "Turuncu Hat", "Turuncu", 1, 3)

    # Bağlantıları ekle
    metro.baglanti_ekle("K1", "K2", 4)
    metro.baglanti_ekle("K2", "K3", 6)
    metro.baglanti_ekle("K3", "K4", 8)
    metro.baglanti_ekle("M1", "M2", 5)
    metro.baglanti_ekle("M2", "M3", 3)
    metro.baglanti_ekle("M3", "M4", 4)
    metro.baglanti_ekle("T1", "T2", 7)
    metro.baglanti_ekle("T2", "T3", 9)
    metro.baglanti_ekle("T3", "T4", 5)
    metro.baglanti_ekle("K1", "M2", 2)
    metro.baglanti_ekle("K3", "T2", 3)
    metro.baglanti_ekle("M4", "T3", 2)

    run_gui(metro)
