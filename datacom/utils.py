# --- Bu dosyada metni bitlere çevirme, Parity ve CRC hesaplama mantığını kuruyoruz.
import binascii

def text_to_bits(text):
    """Metni 8-bitlik binary (string) formatına çevirir."""
    return ''.join(format(ord(c), '08b') for c in text)

def bits_to_text(bits):
    """Binary string'i tekrar metne çevirir."""
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

# --- 1. PARITY BIT (EVEN PARITY) ---
def calculate_parity(data):
    """Verideki 1'lerin sayısına göre Even Parity bitini döner."""
    # Verideki '1' sayısını say, eğer tekse '1' ekle ki çift olsun.
    bit_str = text_to_bits(data)
    ones_count = bit_str.count('1')
    return "0" if ones_count % 2 == 0 else "1"

# --- 2. CRC-16 (CYCLIC REDUNDANCY CHECK) ---
def calculate_crc16(data):
    """Verinin CRC-16 değerini hesaplar."""
    # Basit bir CRC16 uygulaması (XMODEM standardı benzeri)
    data_bytes = data.encode('utf-8')
    crc = 0x0000
    for byte in data_bytes:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return format(crc, '04X') # 4 haneli Hexadecimal döner