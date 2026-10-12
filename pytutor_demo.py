import streamlit as st
import urllib.request
import json
import io
import sys
from streamlit_ace import st_ace

st.set_page_config(layout="wide", page_title="PyTutor Demo")

# CSS để giống giao diện wireframe
st.markdown("""
<style>
    .stApp { font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; }
    .header-box { padding: 10px; border-bottom: 2px solid #2E5F88; margin-bottom: 10px; font-weight: bold; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header-box'>PYTUTOR - BÀI 03: VÒNG LẶP (DEMO NHANH)</div>", unsafe_allow_html=True)

# Khởi tạo layout 3 cột
col1, col2, col3 = st.columns([1, 1.5, 1.2])

# --- CỘT 1: ĐỀ BÀI ---
with col1:
    st.subheader("Đề bài")
    st.markdown("""
    **Yêu cầu:**  
    Viết một hàm `tinh_tong(n)` tính tổng các số từ 1 đến n (bao gồm cả n).
    
    **Ví dụ:**
    - `tinh_tong(3)` trả về `6` (vì 1+2+3 = 6)
    - `tinh_tong(5)` trả về `15`
    
    **Mục tiêu học tập:**  
    Hiểu cách sử dụng vòng lặp `for` hoặc `while` và biến cộng dồn (accumulator).
    """)

# --- CỘT 2: CODE EDITOR & TEST RUNNER ---
with col2:
    st.subheader("Trình soạn thảo")
    
    # Starter code
    default_code = "def tinh_tong(n):\n    # Viết code của bạn ở đây\n    pass\n"
    
    # Trình gõ code
    student_code = st_ace(value=default_code, language="python", theme="github", key="code_editor", height=250)
    
    if st.button("Chạy thử & Chấm điểm", type="primary"):
        st.session_state["test_run"] = True
        
        # Mô phỏng MCP Server - Chạy code an toàn và bắt lỗi
        stdout_capture = io.StringIO()
        sys.stdout = stdout_capture
        local_scope = {}
        
        try:
            # 1. Chạy code sinh viên định nghĩa
            exec(student_code, {}, local_scope)
            
            # 2. Test cases
            func = local_scope.get('tinh_tong')
            if not func:
                result_text = "❌ Lỗi: Không tìm thấy hàm `tinh_tong`. Bạn có đổi tên hàm không?"
            else:
                test_cases = [(3, 6), (5, 15), (1, 1)]
                passed = 0
                log = []
                for args, expected in test_cases:
                    actual = func(args)
                    if actual == expected:
                        passed += 1
                        log.append(f"✅ Test(n={args}): Đạt")
                    else:
                        log.append(f"❌ Test(n={args}): Sai. Trả về {actual}, mong đợi {expected}")
                
                result_text = f"Kết quả: {passed}/{len(test_cases)} Test cases đạt.\n" + "\n".join(log)
                
        except Exception as e:
            result_text = f"❌ Lỗi thực thi (Runtime Error):\n{str(e)}"
            
        sys.stdout = sys.__stdout__
        st.session_state["test_result"] = result_text

    st.subheader("Console (Test Kết quả)")
    if "test_result" in st.session_state:
        st.code(st.session_state["test_result"])
    else:
        st.info("Chưa chạy code.")

# --- CỘT 3: AI TUTOR ---
with col3:
    st.subheader("AI Tutor")
    st.info("Nhấn 'Yêu cầu gợi ý' để nhận hỗ trợ từ Qwen2.5-14B dựa trên kết quả test của bạn.")
    
    if st.button("💡 Yêu cầu gợi ý (Level 1)"):
        if "test_result" not in st.session_state:
            st.warning("Vui lòng chạy thử code trước khi xin gợi ý!")
        else:
            with st.spinner("AI đang phân tích code..."):
                prompt = f"""Bạn là AI Tutor dạy lập trình Python.
                - Đề bài: Viết hàm tinh_tong(n) tính tổng các số từ 1 đến n.
                - Code của sinh viên:\n{student_code}
                - Kết quả Test:\n{st.session_state["test_result"]}
                
                Nhiệm vụ: Đưa ra 1 đoạn nhận xét ngắn gọn gọn (dưới 100 chữ) bằng tiếng Việt để gợi mở cho sinh viên sửa lỗi. Tuyệt đối KHÔNG viết code giải sẵn, chỉ định hướng.
                """
                
                try:
                    url = "http://101.96.66.232:8037/ollama/api/generate"
                    headers = {"Content-Type": "application/json", "x-ollama-seckey": "neutv"}
                    data = {"model": "qwen2.5:14b-instruct-ctx16k", "prompt": prompt, "stream": False}
                    
                    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
                    resp = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
                    ai_reply = json.loads(resp)["response"]
                    
                    st.success("🤖 Tutor: \n\n" + ai_reply)
                    
                except Exception as e:
                    st.error(f"Lỗi kết nối AI: {e}")
