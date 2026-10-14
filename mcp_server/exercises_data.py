"""
Ngân hàng bài tập mẫu và bộ kiểm thử (Test Cases) chuẩn cho PyTutor.
Gồm 5 bài tập từ cơ bản đến nâng cao:
1. Tính tổng các số từ 1 đến n (Vòng lặp & Biến tích lũy)
2. Kiểm tra số nguyên tố (Điều kiện & Tối ưu lặp)
3. Tính giai thừa n! (Vòng lặp hoặc Đệ quy)
4. Đảo ngược chuỗi (Thao tác chuỗi & Chỉ mục)
5. Đếm số lượng nguyên âm (Duyệt chuỗi & Tập hợp)
"""

EXERCISES = [
    {
        "id": "ex_01_sum_1_to_n",
        "title": "Bài 01: Tính tổng từ 1 đến n",
        "difficulty": "Dễ",
        "category": "Vòng lặp & Biến tích lũy",
        "description": """### Mô tả bài toán
Viết chương trình đọc vào một số nguyên dương $n$ từ bàn phím (sử dụng hàm `input()`).
Tính và in ra màn hình tổng các số từ $1$ đến $n$:
$$S = 1 + 2 + 3 + \\dots + n$$

### Đầu vào (Input):
- Một dòng duy nhất chứa số nguyên dương $n$ ($1 \\le n \\le 10^4$).

### Đầu ra (Output):
- Một số nguyên duy nhất là kết quả tổng $S$.

### Ví dụ:
| Input | Output | Giải thích |
| :--- | :--- | :--- |
| `3` | `6` | 1 + 2 + 3 = 6 |
| `5` | `15` | 1 + 2 + 3 + 4 + 5 = 15 |

### Mục tiêu học tập:
- Biết cách sử dụng `int(input())` để nhận dữ liệu.
- Sử dụng vòng lặp `for` với hàm `range()` và biến tích lũy cộng dồn (`+=`).
""",
        "starter_code": """# Đọc số nguyên n từ bàn phím
n = int(input())

# Khởi tạo biến tổng và tính toán
tong = 0
# Viết vòng lặp của bạn ở đây...

print(tong)
""",
        "test_cases": [
            {"input": "1\n", "expected_output": "1", "description": "Kiểm tra với n = 1"},
            {"input": "3\n", "expected_output": "6", "description": "Kiểm tra với n = 3"},
            {"input": "5\n", "expected_output": "15", "description": "Kiểm tra với n = 5"},
            {"input": "10\n", "expected_output": "55", "description": "Kiểm tra với n = 10"},
            {"input": "100\n", "expected_output": "5050", "description": "Kiểm tra giá trị lớn n = 100"},
        ]
    },
    {
        "id": "ex_02_prime_check",
        "title": "Bài 02: Kiểm tra số nguyên tố",
        "difficulty": "Trung bình",
        "category": "Cấu trúc rẽ nhánh & Vòng lặp",
        "description": """### Mô tả bài toán
Số nguyên tố là số nguyên lớn hơn $1$ và chỉ có đúng $2$ ước số dương là $1$ và chính nó (ví dụ: 2, 3, 5, 7, 11...).
Nhập vào một số nguyên $n$ từ bàn phím. Hãy in ra:
- `YES` nếu $n$ là số nguyên tố.
- `NO` nếu $n$ không phải là số nguyên tố.

### Đầu vào (Input):
- Một dòng duy nhất chứa số nguyên $n$ ($-10^6 \\le n \\le 10^6$).

### Đầu ra (Output):
- Chuỗi `YES` hoặc `NO` tương ứng (viết in hoa).

### Ví dụ:
| Input | Output |
| :--- | :--- |
| `7` | `YES` |
| `4` | `NO` |
| `1` | `NO` |
| `-5` | `NO` |

### Mục tiêu học tập:
- Xử lý các trường hợp biên ($n \\le 1$).
- Kỹ thuật cờ hiệu (flag) hoặc kết hợp lệnh `break` / `return`.
""",
        "starter_code": """n = int(input())

# Viết logic kiểm tra số nguyên tố ở đây...

""",
        "test_cases": [
            {"input": "7\n", "expected_output": "YES", "description": "Số nguyên tố thông thường (7)"},
            {"input": "4\n", "expected_output": "NO", "description": "Hợp số (4)"},
            {"input": "1\n", "expected_output": "NO", "description": "Trường hợp biên (1 không là số nguyên tố)"},
            {"input": "2\n", "expected_output": "YES", "description": "Số nguyên tố chẵn duy nhất (2)"},
            {"input": "-5\n", "expected_output": "NO", "description": "Số âm không là số nguyên tố"},
            {"input": "97\n", "expected_output": "YES", "description": "Số nguyên tố lớn (97)"},
        ]
    },
    {
        "id": "ex_03_factorial",
        "title": "Bài 03: Tính giai thừa n!",
        "difficulty": "Dễ",
        "category": "Vòng lặp / Đệ quy",
        "description": """### Mô tả bài toán
Giai thừa của một số tự nhiên $n$ (ký hiệu $n!$) là tích của các số nguyên dương từ $1$ đến $n$:
$$n! = 1 \\times 2 \\times 3 \\times \\dots \\times n$$
Quy ước: $0! = 1$.

Nhập vào số tự nhiên $n$ ($0 \\le n \\le 15$). In ra giá trị của $n!$.

### Đầu vào (Input):
- Một dòng chứa số tự nhiên $n$.

### Đầu ra (Output):
- Giá trị $n!$.

### Ví dụ:
| Input | Output |
| :--- | :--- |
| `0` | `1` |
| `4` | `24` |
| `5` | `120` |

### Mục tiêu học tập:
- Xử lý bài toán tích lũy phép nhân.
- Khởi tạo giá trị ban đầu hợp lý (bằng 1, không được bằng 0).
""",
        "starter_code": """n = int(input())

# Khởi tạo và tính n!
giai_thua = 1
# Viết tiếp code tại đây...

print(giai_thua)
""",
        "test_cases": [
            {"input": "0\n", "expected_output": "1", "description": "Trường hợp đặc biệt 0! = 1"},
            {"input": "1\n", "expected_output": "1", "description": "Kiểm tra 1! = 1"},
            {"input": "4\n", "expected_output": "24", "description": "Kiểm tra 4! = 24"},
            {"input": "5\n", "expected_output": "120", "description": "Kiểm tra 5! = 120"},
            {"input": "8\n", "expected_output": "40320", "description": "Kiểm tra 8! = 40320"},
        ]
    },
    {
        "id": "ex_04_reverse_string",
        "title": "Bài 04: Đảo ngược chuỗi ký tự",
        "difficulty": "Dễ",
        "category": "Chuỗi & Chỉ mục (String Indexing)",
        "description": """### Mô tả bài toán
Nhập vào một chuỗi ký tự $S$ từ bàn phím. In ra chuỗi đảo ngược của $S$.

### Đầu vào (Input):
- Một dòng duy nhất chứa chuỗi $S$.

### Đầu ra (Output):
- Chuỗi ký tự đã được đảo ngược.

### Ví dụ:
| Input | Output |
| :--- | :--- |
| `hello` | `olleh` |
| `Python` | `nohtyP` |
| `racecar` | `racecar` |

### Mục tiêu học tập:
- Thao tác với chuỗi trong Python (duyệt ngược hoặc sử dụng cú pháp cắt chuỗi slice `[::-1]`).
""",
        "starter_code": """s = input()

# Viết mã đảo ngược chuỗi s...

""",
        "test_cases": [
            {"input": "hello\n", "expected_output": "olleh", "description": "Chuỗi thường 'hello'"},
            {"input": "Python\n", "expected_output": "nohtyP", "description": "Chuỗi có hoa thường 'Python'"},
            {"input": "a\n", "expected_output": "a", "description": "Chuỗi 1 ký tự"},
            {"input": "racecar\n", "expected_output": "racecar", "description": "Chuỗi đối xứng (Palindrome)"},
            {"input": "12345 6789\n", "expected_output": "9876 54321", "description": "Chuỗi chứa số và khoảng trắng"},
        ]
    },
    {
        "id": "ex_05_count_vowels",
        "title": "Bài 05: Đếm số lượng nguyên âm",
        "difficulty": "Dễ",
        "category": "Chuỗi & Điều kiện",
        "description": """### Mô tả bài toán
Trong tiếng Anh, các nguyên âm gồm 5 chữ cái: `a`, `e`, `i`, `o`, `u` (không phân biệt chữ hoa hay chữ thường).
Nhập vào một chuỗi văn bản $S$. Hãy đếm và in ra tổng số nguyên âm xuất hiện trong chuỗi $S$.

### Đầu vào (Input):
- Một dòng chứa chuỗi ký tự $S$.

### Đầu ra (Output):
- Một số nguyên là tổng số nguyên âm trong chuỗi.

### Ví dụ:
| Input | Output | Giải thích |
| :--- | :--- | :--- |
| `Hello World` | `3` | Gồm các nguyên âm: 'e', 'o', 'o' |
| `Python` | `1` | Gồm nguyên âm: 'o' |
| `xyz` | `0` | Không có nguyên âm nào |

### Mục tiêu học tập:
- Duyệt qua từng ký tự của chuỗi với vòng lặp `for`.
- Sử dụng phương thức `.lower()` để chuẩn hóa chữ hoa/chữ thường.
- Kiểm tra phần tử thuộc tập hợp bằng toán tử `in`.
""",
        "starter_code": """s = input()

# Đếm số lượng nguyên âm trong s...
dem = 0

print(dem)
""",
        "test_cases": [
            {"input": "Hello World\n", "expected_output": "3", "description": "Chuỗi 'Hello World' có 3 nguyên âm"},
            {"input": "Python\n", "expected_output": "1", "description": "Chuỗi 'Python' có 1 nguyên âm"},
            {"input": "AEIOU\n", "expected_output": "5", "description": "Tất cả chữ hoa nguyên âm"},
            {"input": "bcdfg\n", "expected_output": "0", "description": "Không có nguyên âm"},
            {"input": "PyTutor Intelligent Tutoring System\n", "expected_output": "10", "description": "Câu dài phức tạp"},
        ]
    }
]


def get_all_exercises_summary() -> list[dict]:
    """Trả về danh sách tóm tắt các bài tập phục vụ hiển thị menu/danh sách."""
    return [
        {
            "id": ex["id"],
            "title": ex["title"],
            "difficulty": ex["difficulty"],
            "category": ex["category"],
            "test_cases_count": len(ex["test_cases"])
        }
        for ex in EXERCISES
    ]


def get_exercise_by_id(exercise_id: str) -> dict | None:
    """Tìm chi tiết bài tập theo ID."""
    for ex in EXERCISES:
        if ex["id"] == exercise_id:
            return ex
    return None
