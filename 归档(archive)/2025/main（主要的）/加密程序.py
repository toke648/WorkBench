# 1.转换成摩尔电码
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.'
}

str1 = "HELLO WORLD 123"
for i in str1:
    if i != " ":
        print(MORSE_CODE_DICT[i], end=" ")

def morse_encrypt(str1):
    encrypted_str = ""
    for i in str1:
        if i != " ":
            encrypted_str += MORSE_CODE_DICT[i] + " "
        else:
            encrypted_str += " "
            
    return encrypted_str

print()

# 2.凯撒加密（每个字符向后移动三位）
str1 = "HELLO WORLD 123"

for i in str1:
    if i != " ":
        print(chr(ord(i) + 3), end="")

def caesar_encrypt(str1, shift):
    encrypted_str = ""
    for i in str1:
        if i != " ":
            encrypted_str += chr(ord(i) + shift)
        else:
            encrypted_str += " "
    return encrypted_str

print()

# 3.ASCII 码
str1 = "HELLO WORLD 123"

for i in str1:
    if i != " ":
        print(ord(i), end="")

print()

# 3.反转
str1 = "HELLO WORLD 123"

print(str1[::-1])


# 4.维吉尼亚密码密钥加密（每个字符向后移动密钥对应的值）H——>4 E——>8 L——>6 ...（加密的方式术语称为多表代换密码）
str1 = "HELLO WORLD 123"

key = "486"

for i in range(len(str1)):
    if str1[i] != " ":
        shift = int(key[i % len(key)])
        print(chr(ord(str1[i]) + shift), end="")

def key_encrypt(text, key):
    result = ''
    key_index = 0
    
    for char in text:
        if char.isprintable():
            shift = ord(key[key_index % len(key)]) - ord('a')
            result += chr((ord(char) - ord(' ') - shift) % 95 + ord(' '))
            key_index += 1
        else:
            result += char
    
    return result

print()

# 5.base64加密(base64是一种编码方式，用于将二进制数据转换为可打印的ASCII字符串，常用于在网络传输中安全地表示二进制数据，例如在电子邮件中传输图片或文件)
import base64

str1 = "HELLO WORLD 123"

# 编码
encoded_str = base64.b64encode(str1.encode('utf-8'))
print(encoded_str.decode('utf-8'))

# 解码
decoded_str = base64.b64decode(encoded_str).decode('utf-8')
print(decoded_str)



# 星辰、大海、诗、传奇、远方

# 密文：古老且深邃的星星、最初的海浪掀起的浪花、诞生出的一百个故事、破碎带来的超越、彼此共同的真实

list = {"星辰": "NGC2237::PSR_B1919+21", "大海": "mtDNA_HVR1::L0a1", "诗": "Borges::Lealtad", "传奇": "Euler::Identity", "远方": "Brain_in_a_Vat::You_are_my_proof"}


## 复合加密实现（5层加密模式）

str1 = "古老且深邃的星星、最初的海浪掀起的浪花、诞生出的一百个故事、破碎带来的超越、彼此共同的真实"
print(str1)

str1 = str1[::-1]  # 反转
print(str1)
str1 = caesar_encrypt(str1, 3)  # 凯撒加密
print(str1)
str1 = key_encrypt(str1, "tim") # 这种在原则上算是什么加密方式？ 维吉尼亚密码密钥加密
print(str1)
phy_str = ""
for i in str1:
        if i != " ":
            phy_str += str(ord(i)) + " "  # ASCII码

print(phy_str)
str1 = morse_encrypt(phy_str)  # 摩尔电码
print(str1)  # 输出最终加密结果


# ---------------------------------------------------------------

# 函数实现
def complex_encrypt_5(plain_text):
    plain_text = plain_text[::-1]  # 反转
    print(plain_text)

    # 凯撒加密
    encrypted_str = ""
    for i in plain_text:
        if i != " ":
            encrypted_str += chr(ord(i) + 3)
        else:
            encrypted_str += " "  
    print(encrypted_str)

    # 维吉尼亚密码密钥加密
    result = ''
    key_index = 0
    
    for char in encrypted_str:
        if char.isprintable():
            shift = ord(key[key_index % len(key)]) - ord('a')
            result += chr((ord(char) - ord(' ') - shift) % 95 + ord(' '))
            key_index += 1
        else:
            result += char
    print(result)

    phy_str = ""
    for i in result:
        if i != " ":
            phy_str += str(ord(i)) + " "  # ASCII码
    
    print(phy_str)


    plain_text = morse_encrypt(phy_str)  # 摩尔电码
    return plain_text


text = "这是一个加密测试文本"
print(complex_encrypt_5(text))





# 解密流程实现
import base64

def complex_encrypt_with_base64(plain_text):
    plain_text = plain_text[::-1]  # 反转
    print("反转后:", plain_text)

    # 凯撒加密
    encrypted_str = ""
    for i in plain_text:
        if i != " ":
            encrypted_str += chr(ord(i) + 3)
        else:
            encrypted_str += " "  
    print("凯撒加密后:", encrypted_str)

    # 使用base64代替维吉尼亚加密
    encoded_bytes = base64.b64encode(encrypted_str.encode('utf-8'))
    result = encoded_bytes.decode('utf-8')
    print("Base64加密后:", result)

    # 转换为ASCII码
    phy_str = ""
    for i in result:
        if i != " ":
            phy_str += str(ord(i)) + " "  # ASCII码
    
    print("ASCII码:", phy_str)

    # 莫尔斯电码编码
    plain_text = morse_encrypt(phy_str)
    return plain_text

def complex_decrypt_with_base64(morse_text):
    # 莫尔斯解码
    def morse_decode(morse_str):
        # 通过 / 代表空格 
        morse_dict = {
            '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
            '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9'
        }
        morse_groups = morse_str.strip().split(' ')
        decoded_numbers = []
        for group in morse_groups:
            if group in morse_dict:
                decoded_numbers.append(morse_dict[group])
        return ''.join(decoded_numbers)
    
    # 莫尔斯解码
    digit_str = morse_decode(morse_text)
    numbers = digit_str.split()
    
    # ASCII码转字符
    ascii_text = ''.join(chr(int(num)) for num in numbers)
    
    # Base64解码
    decoded_bytes = base64.b64decode(ascii_text.encode('utf-8'))
    base64_decrypted = decoded_bytes.decode('utf-8')
    
    # 凯撒解密
    caesar_decrypted = ""
    for char in base64_decrypted:
        if char != " ":
            caesar_decrypted += chr(ord(char) - 3)
        else:
            caesar_decrypted += " "
    
    # 字符串反转
    final_result = caesar_decrypted[::-1]
    
    return final_result




def complex_encrypt_fixed(plain_text, key="tim"):
    print("=== 加密过程 ===")
    plain_text = plain_text[::-1]  # 反转
    print("1. 反转后:", plain_text)

    # 凯撒加密
    encrypted_str = ""
    for i in plain_text:
        if i != " ":
            encrypted_str += chr(ord(i) + 3)
        else:
            encrypted_str += " "  
    print("2. 凯撒加密后:", encrypted_str)

    # 维吉尼亚加密（修复版）
    result = ''
    key_index = 0
    
    for char in encrypted_str:
        if char.isprintable():
            shift = ord(key[key_index % len(key)]) - ord('a')
            # 确保在可打印ASCII范围内
            encrypted_code = (ord(char) - 32 - shift) % 95 + 32
            result += chr(encrypted_code)
            key_index += 1
        else:
            result += char
    print("3. 维吉尼亚加密后:", repr(result))

    # 转换为ASCII码（只记录可打印字符）
    phy_str = ""
    for i in result:
        phy_str += str(ord(i)) + " "
    
    print("4. ASCII码:", phy_str)

    phy_str = morse_encrypt(phy_str)  # 摩尔电码编码
    print("5. 摩尔电码编码后:", phy_str)
    
    return phy_str  # 直接返回ASCII码，避免莫尔斯编码问题

# 简单测试
text = "这是一个加密测试文本"
encrypted_ascii = complex_encrypt_fixed(text)
print(f"\n最终ASCII码: {encrypted_ascii}")





# class ComplexEncryption_test:
#     def __init__(self, key="tim"):
#         self.key = key

#     import base64

import base64

def morse_encrypt(text):
    """莫尔斯电码编码"""
    morse_dict = {
        '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
        '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
        ' ': ' '
    }
    morse_text = ""
    for char in text:
        if char in morse_dict:
            morse_text += morse_dict[char] + " "
    return morse_text.strip()

def morse_decode_safe(morse_str):
    """安全的莫尔斯电码解码，避免大整数问题"""
    morse_dict = {
        '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
        '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9'
    }
    
    morse_groups = morse_str.strip().split(' ')
    decoded_digits = []
    
    for group in morse_groups:
        if group in morse_dict:
            decoded_digits.append(morse_dict[group])
    
    # 返回数字字符串，不直接转换
    return ''.join(decoded_digits)

def parse_ascii_codes_safe(digit_str):
    """安全解析ASCII码，避免大整数问题"""
    # 按空格分割数字（加密时每个ASCII码后面都有空格）
    numbers = []
    current_num = ""
    
    for char in digit_str:
        if char == ' ':
            if current_num:
                # 检查数字是否在合理范围内
                num = int(current_num)
                if 0 <= num <= 1114111:  # Unicode最大范围
                    numbers.append(num)
                current_num = ""
        else:
            current_num += char
    
    # 处理最后一个数字
    if current_num:
        num = int(current_num)
        if 0 <= num <= 1114111:
            numbers.append(num)
    
    return numbers

def complex_encrypt_with_base64(plain_text):
    """使用Base64的加密函数"""
    print("=== 加密过程 ===")
    
    # 步骤1: 字符串反转
    reversed_text = plain_text[::-1]
    print("1. 反转后:", reversed_text)

    # 步骤2: 凯撒加密 (每个字符ASCII码+3)
    caesar_encrypted = ""
    for char in reversed_text:
        if char != " ":
            caesar_encrypted += chr(ord(char) + 3)
        else:
            caesar_encrypted += " "  
    print("2. 凯撒加密后:", caesar_encrypted)

    # 步骤3: Base64编码
    base64_encoded = base64.b64encode(caesar_encrypted.encode('utf-8')).decode('utf-8')
    print("3. Base64编码后:", base64_encoded)

    # 步骤4: 转换为ASCII码字符串
    ascii_str = ""
    for char in base64_encoded:
        ascii_str += str(ord(char)) + " "
    print("4. ASCII码长度:", len(ascii_str.split()))
    
    # 步骤5: 莫尔斯电码编码
    morse_result = morse_encrypt(ascii_str)
    print("5. 莫尔斯电码完成")
    
    return morse_result

def complex_decrypt_with_base64(morse_text):
    """使用Base64的解密函数 - 修复版"""
    print("\n=== 解密过程 ===")
    
    # 步骤1: 莫尔斯电码解码
    print("1. 莫尔斯电码解码")
    digit_str = morse_decode_safe(morse_text)
    print(f"   数字字符串长度: {len(digit_str)}")
    
    # 步骤2: 安全解析ASCII码
    print("2. 解析ASCII码")
    ascii_codes = parse_ascii_codes_safe(digit_str)
    print(f"   解析出 {len(ascii_codes)} 个ASCII码")
    
    if not ascii_codes:
        print("   ❌ 没有解析出有效的ASCII码")
        return None
    
    # 步骤3: ASCII码转字符
    print("3. ASCII码转字符")
    try:
        base64_text = ''.join(chr(code) for code in ascii_codes)
        print(f"   Base64文本前50字符: {base64_text[:50]}")
    except Exception as e:
        print(f"   ❌ ASCII转字符错误: {e}")
        return None
    
    # 步骤4: Base64解码
    print("4. Base64解码")
    try:
        decoded_bytes = base64.b64decode(base64_text.encode('utf-8'))
        base64_decrypted = decoded_bytes.decode('utf-8')
        print(f"   Base64解密后: {base64_decrypted}")
    except Exception as e:
        print(f"   ❌ Base64解码错误: {e}")
        return None
    
    # 步骤5: 凯撒解密
    print("5. 凯撒解密")
    caesar_decrypted = ""
    for char in base64_decrypted:
        if char != " ":
            caesar_decrypted += chr(ord(char) - 3)
        else:
            caesar_decrypted += " "
    print(f"   凯撒解密后: {caesar_decrypted}")
    
    # 步骤6: 字符串反转
    print("6. 字符串反转")
    final_result = caesar_decrypted[::-1]
    print(f"   最终结果: {final_result}")
    
    return final_result

# 简化测试版本（避免莫尔斯编码问题）
def simple_encrypt_decrypt_test(plain_text):
    """简化测试，跳过莫尔斯编码"""
    print("=== 简化加密测试 ===")
    
    # 加密
    reversed_text = plain_text[::-1]
    caesar_encrypted = "".join(chr(ord(c) + 3) if c != " " else " " for c in reversed_text)
    base64_encoded = base64.b64encode(caesar_encrypted.encode('utf-8')).decode('utf-8')
    
    print(f"原始文本: {plain_text}")
    print(f"Base64结果: {base64_encoded}")
    
    # 解密
    base64_decoded = base64.b64decode(base64_encoded.encode('utf-8')).decode('utf-8')
    caesar_decrypted = "".join(chr(ord(c) - 3) if c != " " else " " for c in base64_decoded)
    final_result = caesar_decrypted[::-1]
    
    print(f"解密结果: {final_result}")
    print(f"验证: {'✅ 成功' if final_result == plain_text else '❌ 失败'}")
    
    return base64_encoded

# 测试
if __name__ == "__main__":
    # 测试简化版本
    print("测试简化版本（跳过莫尔斯编码）:")
    text = "这是一个加密测试文本"
    encrypted = simple_encrypt_decrypt_test(text)
    
    print("\n" + "="*50)
    
    # 测试完整版本
    print("测试完整版本（包含莫尔斯编码）:")
    try:
        encrypted_full = complex_encrypt_with_base64(text)
        print(f"加密完成，莫尔斯电码长度: {len(encrypted_full)}")
        
        decrypted_full = complex_decrypt_with_base64(encrypted_full)
        if decrypted_full:
            print(f"解密结果: {decrypted_full}")
            print(f"验证: {'✅ 成功' if decrypted_full == text else '❌ 失败'}")
    except Exception as e:
        print(f"完整版本测试失败: {e}")


import base64

def morse_encrypt(text):
    """莫尔斯电码编码"""
    morse_dict = {
        '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
        '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
        ' ': '/'  # 7个空格表示单词间隔
    }
    morse_text = ""
    for char in text:
        if char in morse_dict:
            morse_text += morse_dict[char] + " "
    return morse_text.strip()

def morse_decode_fixed(morse_str):
    """修复的莫尔斯电码解码"""
    morse_dict = {
        '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
        '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9',
        '/': ' '  # 7个空格对应原始空格
    }
    
    # 先用多个空格分割单词，再用单个空格分割字符
    words = morse_str.split('       ')
    decoded_text = ""
    
    for word in words:
        characters = word.strip().split(' ')
        for char in characters:
            if char in morse_dict:
                decoded_text += morse_dict[char]
        decoded_text += " "  # 在单词间添加空格
    
    return decoded_text.strip()

def complex_encrypt_with_base64(plain_text):
    """使用Base64的加密函数"""
    print("=== 加密过程 ===")
    
    # 步骤1: 字符串反转
    reversed_text = plain_text[::-1]
    print("1. 反转后:", reversed_text)

    # 步骤2: 凯撒加密 (每个字符ASCII码+3)
    caesar_encrypted = ""
    for char in reversed_text:
        if char != " ":
            caesar_encrypted += chr(ord(char) + 3)
        else:
            caesar_encrypted += " "  
    print("2. 凯撒加密后:", caesar_encrypted)

    # 步骤3: Base64编码
    base64_encoded = base64.b64encode(caesar_encrypted.encode('utf-8')).decode('utf-8')
    print("3. Base64编码后:", base64_encoded)

    # 步骤4: 转换为ASCII码字符串（保留空格分隔）
    ascii_str = ""
    for char in base64_encoded:
        ascii_str += str(ord(char)) + " "  # 重要：每个ASCII码后加空格
    print("4. ASCII码字符串:", ascii_str)
    
    # 步骤5: 莫尔斯电码编码
    morse_result = morse_encrypt(ascii_str)
    print("5. 莫尔斯电码完成")
    
    return morse_result

def complex_decrypt_with_base64_fixed(morse_text):
    """修复的解密函数"""
    print("\n=== 解密过程 ===")
    
    # 步骤1: 莫尔斯电码解码
    print("1. 莫尔斯电码解码")
    digit_str_with_spaces = morse_decode_fixed(morse_text)
    print(f"   带空格的数字字符串: {digit_str_with_spaces}")
    
    # 步骤2: 直接按空格分割ASCII码
    print("2. 解析ASCII码")
    ascii_codes = []
    numbers = digit_str_with_spaces.split()
    for num_str in numbers:
        try:
            ascii_codes.append(int(num_str))
        except ValueError:
            continue
    
    print(f"   解析出 {len(ascii_codes)} 个ASCII码: {ascii_codes}")
    
    if not ascii_codes:
        print("   ❌ 没有解析出有效的ASCII码")
        return None
    
    # 步骤3: ASCII码转字符
    print("3. ASCII码转字符")
    try:
        base64_text = ''.join(chr(code) for code in ascii_codes)
        print(f"   Base64文本: {base64_text}")
    except Exception as e:
        print(f"   ❌ ASCII转字符错误: {e}")
        return None
    
    # 步骤4: Base64解码
    print("4. Base64解码")
    try:
        decoded_bytes = base64.b64decode(base64_text.encode('utf-8'))
        base64_decrypted = decoded_bytes.decode('utf-8')
        print(f"   Base64解密后: {base64_decrypted}")
    except Exception as e:
        print(f"   ❌ Base64解码错误: {e}")
        return None
    
    # 步骤5: 凯撒解密
    print("5. 凯撒解密")
    caesar_decrypted = ""
    for char in base64_decrypted:
        if char != " ":
            caesar_decrypted += chr(ord(char) - 3)
        else:
            caesar_decrypted += " "
    print(f"   凯撒解密后: {caesar_decrypted}")
    
    # 步骤6: 字符串反转
    print("6. 字符串反转")
    final_result = caesar_decrypted[::-1]
    print(f"   最终结果: {final_result}")
    
    return final_result

# 测试修复版本
if __name__ == "__main__":
    text = "这是一个加密测试文本"
    
    print("测试修复版本:")
    encrypted = complex_encrypt_with_base64(text)
    print(f"\n加密完成")
    print(f"莫尔斯电码前100字符: {encrypted}")
    
    decrypted = complex_decrypt_with_base64_fixed(encrypted)
    if decrypted:
        print(f"\n解密结果: {decrypted}")
        print(f"验证: {'✅ 成功' if decrypted == text else '❌ 失败'}")



# --------------------------------------------------------------------------------

# 凯撒加密
test1 = "古老且深邃的星星"

for i in test1:
    if i != " ":
        print(chr(ord(i) + 3), end="")
print()

# Atbash加密
test2 = "最初的海浪掀起的浪花"
# for i in test2:
#     if i != " ":
#         print(chr(ord("Z") - ord(i) + ord("A")), end="")
# print()

# 维吉尼亚密码密钥加密
test3 = "诞生出的一百个故事"
key = "KEY"
key_index = 0

for i in test3:
    if i != " ":
        print(chr(ord(i) + ord(key[key_index]) - ord("A")), end="")
        key_index = (key_index + 1) % len(key)
    else:
        print(" ", end="")
print()

# 栅栏密码加密
test4 = "破碎带来的超越"
rail1 = ""
rail2 = ""
for i in range(len(test4)):
    if i % 2 == 0:
        rail1 += test4[i]
    else:
        rail2 += test4[i]
print(rail1 + rail2)

# 简单替换密码 (KEY: REALITY -> TRUTHY)
test5 = "彼此共同的真实"
join_char = " "
substitution_dict = {
    '现': 'T', '实': 'R', '的': 'U', '共': 'T', '同': 'H', '彼': 'Y'
}
encrypted_text = ""
for char in test5:
    if char in substitution_dict:
        encrypted_text += substitution_dict[char]
    else:
        encrypted_text += char
encrypted_text = join_char.join(encrypted_text)
print(encrypted_text)




# 凯撒密码 3
test1 = "古老且深邃的星星"
def caesar_encrypt_custom(text, shift):
    encrypted = ""
    for char in text:
        if char != " ":
            encrypted += chr(ord(char) + shift)
        else:
            encrypted += " "
    return encrypted
print(caesar_encrypt_custom(test1, 3))

# bs64 加密
import base64
test2 = "最初的海浪掀起的浪花"
encoded_bytes = base64.b64encode(test2.encode('utf-8'))
encoded_str = encoded_bytes.decode('utf-8')
print(encoded_str)

# 转换为二进制
test3 = "诞生出一百个故事"
binary_str = ' '.join(format(ord(char), '08b') for char in test3)
print(binary_str)

# 转换为unicode编码
test4 = "破碎带来的超越"
unicode_str = ' '.join(format(ord(char), '04x') for char in test4)
print(unicode_str)

# 维吉尼加密 key: toke648
test5 = "彼此共同的真实"
key = "toke648"

def vigenere_encrypt(plain_text, key):
    encrypted_text = ""
    key_index = 0
    for char in plain_text:
        if char != " ":
            encrypted_text += chr(ord(char) + ord(key[key_index]) - ord("A"))
            key_index = (key_index + 1) % len(key)
        else:
            encrypted_text += " "
    return encrypted_text

print(vigenere_encrypt(test5, key))


import base64

encoded_str = "5pyA5Yid55qE5rW35rWq5o6A6LW355qE5rWq6Iqx"
decoded_bytes = base64.b64decode(encoded_str)
decoded_str = decoded_bytes.decode('utf-8')
print(decoded_str)


# 我突然想到一种加密方法，这种怎么样？
# 自定义换位密码（原理）
# 将字符拆分为四组，并定义密匙为1234
# 意为第一个字符序列换到第二个，第二个字符序列换到第三个，第三个换到第一个，第一个换到第四个

test_str = "Hello World 123"
def custom_transposition_encrypt(text, key):
    n = len(key)
    groups = ['' for _ in range(n)]
    
    for i, char in enumerate(text):
        group_index = i % n
        groups[group_index] += char
    
    encrypted_text = ''
    for index in sorted(range(n), key=lambda x: key[x]):
        encrypted_text += groups[index]
    
    return encrypted_text
key = "3142"
print(custom_transposition_encrypt(test_str, key))



# 自定义换位密码解密实现
def custom_transposition_decrypt(encrypted_text, key):
    n = len(key)
    group_lengths = [len(encrypted_text) // n + (1 if i < len(encrypted_text) % n else 0) for i in range(n)]
    
    groups = ['' for _ in range(n)]
    start = 0
    for index in sorted(range(n), key=lambda x: key[x]):
        length = group_lengths[index]
        groups[index] = encrypted_text[start:start + length]
        start += length
    
    decrypted_text = ''
    for i in range(max(group_lengths)):
        for group in groups:
            if i < len(group):
                decrypted_text += group[i]
    
    return decrypted_text
key = "3142"
encrypted_str = custom_transposition_encrypt(test_str, key)
print(custom_transposition_decrypt(encrypted_str, key))


# 测试更长的文本
long_text = "This is a longer example text to demonstrate the encryption method!"
key = "54098009"

encrypted = custom_transposition_encrypt(long_text, key)
decrypted = custom_transposition_decrypt(encrypted, key)

print(f"原始文本: {long_text}")
print(f"加密结果: {encrypted}")
print(f"解密结果: {decrypted}")
print(f"加解密成功: {long_text == decrypted}")