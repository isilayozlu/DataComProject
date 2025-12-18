import socket

# --- YARDIMCI VE MATEMATİKSEL FONKSİYONLAR ---

def text_to_bits(text):
    """Metni 8 bitlik ikilik (binary) sistem dizisine çevirir."""
    return ''.join(format(ord(c), '08b') for c in text)

def calculate_parity(data):
    """
    Tek Boyutlu Parity Check (Eşlik Denetimi):
    Toplam '1' sayısı çift ise '0', tek ise '1' döner (Even Parity).
    """
    return "0" if text_to_bits(data).count('1') % 2 == 0 else "1"

def calculate_2d_parity(data):
    """
    İki Boyutlu (LRC) Parity Check:
    Veriyi satırlara böler, hem satır hem de sütunlar için ayrı parity hesaplar.
    Hatanın hem olduğunu anlar hem de yerini saptayabilir.
    """
    bits = text_to_bits(data)
    # Veriyi 8 bitlik satırlara ayır
    rows = [bits[i:i+8] for i in range(0, len(bits), 8)]
    # Eksik bit varsa son satırı 0 ile tamamla
    while len(rows[-1]) < 8: rows[-1] = rows[-1].ljust(8, '0')
    
    # Satır parity'lerini hesapla
    row_p = "".join("0" if r.count('1') % 2 == 0 else "1" for r in rows)
    # Sütun parity'lerini hesapla
    col_p = "".join("0" if sum(int(rows[r][c]) for r in range(len(rows))) % 2 == 0 else "1" for c in range(8))
    
    return f"R{row_p}C{col_p}"



def calculate_crc16(data):
    """
    CRC-16 (Cyclic Redundancy Check):
    Veriyi matematiksel bir polinoma böler. Kalan değeri (remainder) hata kodu olarak kullanır.
    Ağ iletişiminde en yaygın kullanılan hata tespit yöntemidir.
    """
    crc = 0xFFFF # Başlangıç değeri
    for char in data:
        crc ^= ord(char) << 8
        for _ in range(8):
            # CRC Polinomu (0x1021) ile XOR işlemi yapılır
            crc = (crc << 1) ^ 0x1021 if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return format(crc, '04X')

def calculate_hamming(data):
    """
    Hamming (7,4) Özeti:
    Verinin ilk 4 bitine göre kontrol bitleri oluşturur. 
    Sadece hatayı bulmakla kalmaz, 1 bitlik hataları düzeltebilir.
    """
    b = text_to_bits(data)[:4].ljust(4, '0')
    p1 = (int(b[0]) + int(b[1]) + int(b[3])) % 2
    p2 = (int(b[0]) + int(b[2]) + int(b[3])) % 2
    p3 = (int(b[1]) + int(b[2]) + int(b[3])) % 2
    return f"{p1}{p2}{p3}"

def calculate_checksum(data):
    """
    Internet Checksum (16-bit):
    Veriyi 16-bitlik bloklar halinde toplar, taşan bitleri ekler ve sonucun tersini alır.
    IP ve TCP paketlerinde kullanılır.
    """
    total = sum(ord(data[i]) + (ord(data[i+1]) << 8 if i+1 < len(data) else 0) for i in range(0, len(data), 2))
    # 16 bitten taşan kısımları (carry) başa ekle
    while total >> 16: total = (total & 0xFFFF) + (total >> 16)
    return format(~total & 0xFFFF, '04X')

# --- ANA GÖNDERİCİ FONKSİYONU ---

def start_client1():
    # Sunucuya bağlan
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('localhost', 5000))
        
        data = input("Gönderilecek Metni Girin: ")
        print("\nHata Kontrol Yöntemi Seçin:")
        print("1: Parity\n2: 2D Parity\n3: CRC16\n4: Hamming\n5: Checksum")
        ch = input("Seçiminiz: ")
        
        # Seçime göre fonksiyon eşleştirmesi
        methods = {
            "1":("PARITY", calculate_parity), 
            "2":("2DPARITY", calculate_2d_parity), 
            "3":("CRC16", calculate_crc16), 
            "4":("HAMMING", calculate_hamming), 
            "5":("CHECKSUM", calculate_checksum)
        }
        
        # Seçilen metodu al, seçim geçersizse varsayılan olarak Parity kullan
        m_name, m_func = methods.get(ch, ("PARITY", calculate_parity))
        
        # Kontrol kodunu hesapla (Örn: Veri 'A' ise CRC sonucu 'B2C1' gibi)
        ctrl = m_func(data)
        
        # Paketi oluştur (Örn: "Merhaba|CRC16|B2C1")
        packet = f"{data}|{m_name}|{ctrl}"
        
        # Sunucuya gönder
        client.send(packet.encode())
        print(f"\n[+] Paket Gönderildi: {packet}")
        
    except ConnectionRefusedError:
        print("[!] Hata: Sunucuya bağlanılamadı!")
    finally:
        client.close()

if __name__ == "__main__": 
    start_client1()