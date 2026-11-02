import tkinter as tk
from tkinter import messagebox
import random
import math

# ---------- Вспомогательные функции RSA ----------

def is_prime(n, k=20):
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def gen_prime(bits):
    while True:
        p = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(p):
            return p


def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x, y = egcd(b, a % b)
    return g, y, x - (a // b) * y


def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("Обратного элемента нет")
    return x % m


def gen_rsa_keys(bits=64):
    """Генерирует пару ключей RSA. Возвращает (e, d, n)."""
    p = gen_prime(bits)
    q = gen_prime(bits)
    while q == p:
        q = gen_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    if math.gcd(e, phi) != 1:
        e = 3
        while math.gcd(e, phi) != 1:
            e += 2
    d = modinv(e, phi)
    return e, d, n


# ---------- Основное приложение ----------

class RSAApp:
    def __init__(self, root, role):
        self.root = root
        self.role = role  # "sender" или "receiver"

        # Ключи для шифрования сообщения
        self.msg_e = None
        self.msg_d = None
        self.msg_n = None
        self.msg_n_peer = None  # открытый ключ партнёра для шифрования

        # Ключи для подписи
        self.sig_e = None
        self.sig_d = None
        self.sig_n = None
        self.sig_n_peer = None  # открытый ключ партнёра для проверки

        self.build_ui()

    def build_ui(self):
        self.root.title("Отправитель" if self.role == "sender" else "Получатель")

        # Заголовки
        tk.Label(self.root, text="Для подписи", font=("Arial", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=5)
        tk.Label(self.root, text="Для сообщения", font=("Arial", 10, "bold")).grid(
            row=0, column=2, columnspan=2, sticky="w", padx=5)

        # Открытые ключи
        tk.Label(self.root, text="Открытый ключ:").grid(row=1, column=0, sticky="w", padx=5)
        self.sig_pub_entry = tk.Entry(self.root, width=25)
        self.sig_pub_entry.grid(row=1, column=1, padx=5)

        tk.Label(self.root, text="Открытый ключ:").grid(row=1, column=2, sticky="w", padx=5)
        self.msg_pub_entry = tk.Entry(self.root, width=25)
        self.msg_pub_entry.grid(row=1, column=3, padx=5)

        # N
        tk.Label(self.root, text="N:").grid(row=2, column=0, sticky="w", padx=5)
        self.sig_n_label = tk.Label(self.root, text="", width=25, anchor="w", relief="sunken")
        self.sig_n_label.grid(row=2, column=1, padx=5)

        tk.Label(self.root, text="N:").grid(row=2, column=2, sticky="w", padx=5)
        self.msg_n_label = tk.Label(self.root, text="", width=25, anchor="w", relief="sunken")
        self.msg_n_label.grid(row=2, column=3, padx=5)

        # Кнопки
        tk.Button(self.root, text="Сгенерировать ключи", command=self.generate_keys).grid(
            row=3, column=0, columnspan=2, pady=5)
        tk.Button(self.root, text="Послать", command=self.send_keys).grid(
            row=3, column=2, columnspan=2, pady=5)

        tk.Button(self.root, text="Зашифровать и подписаться",
                  command=self.encrypt_and_sign).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(self.root, text="Получить", command=self.receive).grid(
            row=4, column=2, pady=5)
        tk.Button(self.root, text="Проверить", command=self.verify).grid(
            row=4, column=3, pady=5)

        # Окно сообщения
        tk.Label(self.root, text="Окно сообщения").grid(
            row=5, column=0, columnspan=4, sticky="w", padx=5)
        self.text = tk.Text(self.root, width=70, height=12)
        self.text.grid(row=6, column=0, columnspan=4, padx=5, pady=5)

    # ---------- Логика ----------

    def generate_keys(self):
        # Ключи для подписи
        self.sig_e, self.sig_d, self.sig_n = gen_rsa_keys(bits=32)
        self.sig_pub_entry.delete(0, tk.END)
        self.sig_pub_entry.insert(0, str(self.sig_e))
        self.sig_n_label.config(text=str(self.sig_n))

        # Ключи для сообщения
        self.msg_e, self.msg_d, self.msg_n = gen_rsa_keys(bits=32)
        self.msg_pub_entry.delete(0, tk.END)
        self.msg_pub_entry.insert(0, str(self.msg_e))
        self.msg_n_label.config(text=str(self.msg_n))

        messagebox.showinfo("Готово", "Ключи сгенерированы")

    def send_keys(self):
        """Передаёт открытые ключи партнёру через глобальное хранилище."""
        if self.role == "sender":
            shared["sender_sig_pub"] = (self.sig_e, self.sig_n)
            shared["sender_msg_pub"] = (self.msg_e, self.msg_n)
        else:
            shared["receiver_sig_pub"] = (self.sig_e, self.sig_n)
            shared["receiver_msg_pub"] = (self.msg_e, self.msg_n)
        messagebox.showinfo("Послано", "Открытые ключи переданы")

    def encrypt_and_sign(self):
        """Шифрует сообщение и подписывает его."""
        if self.role != "sender":
            messagebox.showerror("Ошибка", "Только отправитель шифрует и подписывает")
            return

        text = self.text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Ошибка", "Введите сообщение")
            return

        # Получаем открытые ключи получателя
        if "receiver_msg_pub" not in shared or "receiver_sig_pub" not in shared:
            messagebox.showerror("Ошибка", "Получатель ещё не послал ключи")
            return

        recv_msg_e, recv_msg_n = shared["receiver_msg_pub"]
        recv_sig_e, recv_sig_n = shared["receiver_sig_pub"]

        # Шифруем сообщение (по байтам, т.к. RSA работает с числами)
        data = text.encode("utf-8")
        encrypted = []
        for b in data:
            encrypted.append(pow(b, recv_msg_e, recv_msg_n))

        # Подпись: хэш = сумма байтов (упрощённо, для демонстрации)
        h = sum(data) % self.sig_n
        signature = pow(h, self.sig_d, self.sig_n)

        # Сохраняем в общее хранилище
        shared["cipher"] = encrypted
        shared["signature"] = signature
        shared["sender_sig_pub_for_verify"] = (self.sig_e, self.sig_n)

        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END,
                         f"Зашифровано ({len(encrypted)} чисел) и подписано.\n"
                         f"Подпись: {signature}")

    def receive(self):
        """Получатель расшифровывает сообщение."""
        if self.role != "receiver":
            messagebox.showerror("Ошибка", "Только получатель получает сообщение")
            return

        if "cipher" not in shared:
            messagebox.showerror("Ошибка", "Сообщение ещё не отправлено")
            return

        encrypted = shared["cipher"]
        decrypted = bytes(pow(c, self.msg_d, self.msg_n) for c in encrypted)
        text = decrypted.decode("utf-8")

        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, text)

    def verify(self):
        """Получатель проверяет подпись."""
        if self.role != "receiver":
            messagebox.showerror("Ошибка", "Проверяет получатель")
            return

        if "signature" not in shared or "sender_sig_pub_for_verify" not in shared:
            messagebox.showerror("Ошибка", "Нет подписи")
            return

        text = self.text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Ошибка", "Нет сообщения для проверки")
            return

        sig_e, sig_n = shared["sender_sig_pub"]
        signature = shared["signature"]

        # Восстанавливаем хэш из подписи
        h_recv = pow(signature, sig_e, sig_n)
        # Считаем хэш от полученного текста
        h_calc = sum(text.encode("utf-8")) % sig_n

        if h_recv == h_calc:
            messagebox.showinfo("Проверка", "Подпись верна")
        else:
            messagebox.showerror("Проверка", "Подпись неверна")


# ---------- Запуск двух окон ----------

shared = {}  # общее хранилище для имитации канала связи

root_sender = tk.Tk()
app_sender = RSAApp(root_sender, "sender")

root_receiver = tk.Toplevel(root_sender)
app_receiver = RSAApp(root_receiver, "receiver")

root_sender.mainloop()
