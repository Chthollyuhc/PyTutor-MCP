import os
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

def create_mcp_report():
    template_path = r"C:\Users\Admin\Downloads\Sales-support-AI-pilot\Bao_cao.docx"
    output_path = r"C:\Users\Admin\Downloads\Sales-support-AI-pilot\Bao_cao_MCP_PyTutor_Tran_Khanh.docx"
    
    # Check if template exists, if so use it, else create a blank Document
    if os.path.exists(template_path):
        doc = Document(template_path)
    else:
        doc = Document()
    
    # Styles config
    DARK = "1F2933"
    BLUE = "2E5F88"
    
    # Ensure styles exist
    styles = doc.styles
    if "Heading 1" in styles:
        h1 = styles["Heading 1"]
        h1.font.bold = True
        h1.font.color.rgb = RGBColor.from_string(BLUE)
    if "Heading 2" in styles:
        h2 = styles["Heading 2"]
        h2.font.bold = True
        h2.font.color.rgb = RGBColor.from_string(BLUE)
        
    # Append report content
    p = doc.add_paragraph()
    r = p.add_run("BÁO CÁO NGHIÊN CỨU: MODEL CONTEXT PROTOCOL (MCP)")
    r.bold = True
    r.font.size = Pt(16)
    r.font.color.rgb = RGBColor.from_string(BLUE)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p = doc.add_paragraph("Mục đích: Thuyết phục Giảng viên hướng dẫn về tính phù hợp của MCP trong đồ án tốt nghiệp\nNguồn tham khảo: modelcontextprotocol.io, MCP-Solver (SAT 2025), Paper2Agent (Nature, 2026)")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_heading("1. MCP LÀ GÌ?", level=1)
    doc.add_paragraph("Model Context Protocol (MCP) là một giao thức mã nguồn mở, được Anthropic công bố vào tháng 11 năm 2024, với mục tiêu xây dựng một chuẩn giao tiếp thống nhất giữa các mô hình AI (LLM) và các nguồn dữ liệu, công cụ, hệ thống bên ngoài.")
    doc.add_paragraph("Nếu REST API là chuẩn giao tiếp cho phần mềm truyền thống, thì MCP là chuẩn giao tiếp cho các hệ thống AI có khả năng hành động (Agentic AI).")
    
    doc.add_heading("1.1. Sự khác biệt so với API truyền thống", level=2)
    tbl = doc.add_table(rows=6, cols=3)
    tbl.style = "Table Grid"
    tbl.rows[0].cells[0].text = "Tiêu chí"
    tbl.rows[0].cells[1].text = "REST API"
    tbl.rows[0].cells[2].text = "Model Context Protocol (MCP)"
    
    rows = [
        ("Đối tượng sử dụng", "Lập trình viên viết code để gọi", "AI Model/Agent tự khám phá và gọi"),
        ("Cách kết nối", "Hardcode từng endpoint cụ thể", "Dynamic – Agent tự phát hiện tool tại runtime"),
        ("Tích hợp", "Phải viết lại cho mỗi cặp (AI, Tool)", "Cài một lần – dùng được với mọi AI"),
        ("Vai trò", "Tầng thực thi (Execution Layer)", "Tầng điều phối Agent"),
        ("Ngôn ngữ giao tiếp", "JSON/HTTP cho phần mềm", "JSON-RPC 2.0 tối ưu cho LLM")
    ]
    for i, (col1, col2, col3) in enumerate(rows):
        tbl.rows[i+1].cells[0].text = col1
        tbl.rows[i+1].cells[1].text = col2
        tbl.rows[i+1].cells[2].text = col3
        
    doc.add_heading("2. KIẾN TRÚC CỦA MCP", level=1)
    doc.add_paragraph("MCP sử dụng mô hình Client-Server với ba thành phần chính:\n"
                      "- MCP HOST: Ứng dụng người dùng tương tác (IDE, Web App) tích hợp LLM.\n"
                      "- MCP CLIENT: Cầu nối bên trong Host để giao tiếp.\n"
                      "- MCP SERVER: Cung cấp Tools, Resources và Prompts cho Client.\n")
    
    doc.add_heading("Các loại tài nguyên MCP Server cung cấp:", level=2)
    doc.add_paragraph("1. Tools (Công cụ): Các hàm mà AI có thể gọi để thực thi hành động. Ví dụ: run_tests, analyze_ast.\n"
                      "2. Resources (Tài nguyên): Dữ liệu mà AI có thể đọc để lấy ngữ cảnh. Ví dụ: Nội dung đề bài.\n"
                      "3. Prompts (Hướng dẫn): Template câu hỏi định nghĩa sẵn.")
    
    doc.add_heading("3. CÁCH MCP HOẠT ĐỘNG TRONG PYTUTOR", level=1)
    doc.add_paragraph("Bước 1: Sinh viên viết code và bấm yêu cầu gợi ý\n"
                      "Bước 2: HOST (Backend PyTutor) gọi MCP Client gửi Tool Call 'run_tests'\n"
                      "Bước 3: MCP Server (Python Sandbox) chạy code và trả kết quả thực (PASS/FAIL, lỗi traceback)\n"
                      "Bước 4: Client chuyển kết quả cho LLM. LLM suy luận dựa trên BẰNG CHỨNG THỰC.\n"
                      "Bước 5: LLM sinh ra gợi ý thích ứng và hiển thị cho sinh viên.\n")
    
    doc.add_heading("4. BẰNG CHỨNG THỰC TIỄN", level=1)
    doc.add_paragraph("- Tháng 12/2025: MCP được quản lý bởi Agentic AI Foundation (Linux Foundation) với sự tham gia của Google, Microsoft, OpenAI...\n"
                      "- GitHub Copilot, Cursor IDE, VS Code đều đã hỗ trợ toàn diện.\n"
                      "- Bài báo MCP-Solver (SAT 2025): Hoàn toàn loại bỏ ảo giác trong toán học bằng cách bọc z3/minizinc thành MCP.\n"
                      "- Paper2Agent (Nature, 2026): Biến bài báo nghiên cứu thành MCP Server.")
    
    doc.add_heading("5. LÝ DO ỨNG DỤNG VÀO ĐỒ ÁN PYTUTOR", level=1)
    doc.add_paragraph("Giải quyết vấn đề cốt lõi của ITS: LLM cần kết quả chạy thật (Ground Truth) để làm căn cứ sư phạm. "
                      "Sử dụng MCP giúp dễ dàng mở rộng thêm công cụ (tính điểm, chấm C++) mà không cần viết lại toàn bộ API, "
                      "mang lại tính minh bạch cho hệ thống (có thể giải thích được gợi ý lấy từ kết quả test case nào).")
    
    doc.add_page_break()
    doc.save(output_path)
    print("Report generated:", output_path)

if __name__ == "__main__":
    create_mcp_report()
