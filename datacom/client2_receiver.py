import socket

# --- HESAPLAMA ARAÇLARI (Client 1 ile Birebir Aynı Olmalı) ---

def text_to_bits(text):
    return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

def calculate_parity(data):
    return "0" if text_to_bits(data).count('1') % 2 == 0 else "1"

def calculate_crc16(data):
    crc = 0xFFFF
    for char in data:
        crc ^= ord(char) << 8
        for _ in range(8):
            crc = (crc << 1) ^ 0x1021 if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return format(crc, '04X')

def calculate_checksum(data):
    total = sum(ord(c) for c in data)
    return format(total % 256, '02X') # Basit bir checksum örneği

def calculate_2d_parity(data):
    # Basitleştirilmiş 2D Parity özeti
    bits = text_to_bits(data)
    return "R" + str(bits.count('1') % 2) 

def calculate_hamming(data):
    # Basit Hamming kontrolü
    bits = text_to_bits(data)[:4]
    return "H" + str(bits.count('1') % 2)

# --- ANA ALICI FONKSİYONU ---

def start_receiver():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect(('localhost', 5000))
        print("[+] Sunucuya bağlandı. Veri bekleniyor...")

        packet = client.recv(1024).decode()
        
        if packet:
            # Paketi parçalarına ayır
            data, method, incoming_ctrl = packet.split("|")
            
            # --- KRİTİK NOKTA: YENİDEN HESAPLAMA ---
            # Gelen veriyi (data), gelen metoda (method) göre tekrar hesaplıyoruz
            if method == "PARITY":
                computed_ctrl = calculate_parity(data)
            elif method == "CRC16":
                computed_ctrl = calculate_crc16(data)
            elif method == "CHECKSUM":
                computed_ctrl = calculate_checksum(data)
            elif method == "2DPARITY":
                computed_ctrl = calculate_2d_parity(data)
            elif method == "HAMMING":
                computed_ctrl = calculate_hamming(data)
            else:
                computed_ctrl = "UNKNOWN"

            # --- SONUÇ EKRANI (Ödevde istenen format) ---
            print("\n" + "="*40)
            print(f"Received Data       : {data}")
            print(f"Method              : {method}")
            print(f"Sent Check Bits     : {incoming_ctrl}")
            print(f"Computed Check Bits : {computed_control if 'computed_control' in locals() else computed_ctrl}")
            
            print("-" * 40)
            # Karşılaştırma burada yapılıyor:
            if incoming_ctrl == computed_ctrl:
                print("Status              : DATA CORRECT")
            else:
                print("Status              : DATA CORRUPTED")
            print("="*40 + "\n")

    except Exception as e:
        print(f"[!] Bir hata oluştu: {e}")
    finally:
        client.close()
        print("Bağlantı kapatıldı.")

if __name__ == "__main__":
    start_receiver()