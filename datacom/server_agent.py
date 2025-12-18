import socket
import random

# --- HATA OLUŞTURMA FONKSİYONLARI ---

def bit_flip(data):
    """
    Verinin içindeki rastgele bir bit'i tersine çevirir (0 ise 1, 1 ise 0 yapar).
    Tek bitlik hataları simüle eder.
    """
    if not data: return data
    # Karakterleri 8 bitlik (1 byte) ikilik sisteme çevirir
    bits = list(''.join(format(ord(c), '08b') for c in data))
    # Rastgele bir bit seçer
    idx = random.randint(0, len(bits) - 1)
    # Bit'i ters çevirir
    bits[idx] = '1' if bits[idx] == '0' else '0'
    # Bitleri tekrar karakterlere dönüştürerek metni birleştirir
    return "".join(chr(int("".join(bits[i:i+8]), 2)) for i in range(0, len(bits), 8))

def burst_error(data):
    """
    Verinin belirli bir kısmını (ardışık karakterleri) bozar.
    'Burst Error' denilen ardışık hata türünü simüle eder.
    """
    if len(data) < 2: return "ERR" + data
    lst = list(data)
    # Hatanın başlayacağı rastgele bir nokta seçer
    start = random.randint(0, len(lst)-1)
    # Seçilen noktadan itibaren 3 karakteri '#' ile değiştirerek bozma yapar
    for i in range(start, min(start+3, len(lst))): 
        lst[i] = '#'
    return "".join(lst)

# --- ANA SUNUCU DÖNGÜSÜ ---

def start_server():
    # TCP Soketi oluşturuluyor (IPv4, TCP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Sunucuyu localhost 5000 portuna bağla ve dinlemeye başla
    server.bind(('localhost', 5000))
    server.listen(2) # Aynı anda 2 bağlantıya izin ver
    
    print("Server Beklemede (Önce Client 2'yi, sonra Client 1'i açın)...")
    
    # İki istemcinin de bağlanmasını bekle
    c2, _ = server.accept() # Hedef İstemci (Veriyi alan)
    c1, _ = server.accept() # Kaynak İstemci (Veriyi gönderen)
    
    # Client 1'den gelen paketi al (Format: veri|metot|kontrol_kodu)
    packet = c1.recv(1024).decode()
    data, method, ctrl = packet.split("|") # Paketi parçalara ayır
    
    # Kullanıcıya veriyi nasıl bozmak istediğini sor
    print(f"\n1: Bit Flip (Bit Çevirme)\n 2: Substitution (Değiştirme)\n 3: Burst Error\n 4: No Error\n")
    ch = input("Uygulanacak hata türünü seçin: ")
    
    corrupted = data # Varsayılan olarak veri temiz
    
    # Seçime göre veriyi bozma işlemleri
    if ch == "1": 
        corrupted = bit_flip(data) # Rastgele 1 bit değiştir
    elif ch == "2": 
        # İlk karakteri 'Z' harfi ile değiştirir
        corrupted = data.replace(data[0], 'Z', 1) if data else data
    elif ch == "3": 
        corrupted = burst_error(data) # Ardışık karakterleri boz
    
    # Yeni (belki bozulmuş) paketi oluştur ve Client 2'ye gönder
    new_packet = f"{corrupted}|{method}|{ctrl}"
    c2.send(new_packet.encode())
    
    print(f"İşlem Tamamlandı. İletilen Paket: {new_packet}")
    
    # Tüm bağlantıları kapat
    c1.close()
    c2.close()
    server.close()

if __name__ == "__main__": 
    start_server()