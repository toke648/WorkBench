"""
文档解析模块
支持PDF、DOCX、TXT等格式的文档解析
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional


class DocumentParser:
    """文档解析器"""
    
    def __init__(self):
        """初始化文档解析器"""
        self.pdf_available = False
        self.docx_available = False
        
        # 检查依赖
        try:
            import PyPDF2
            self.pdf_available = True
        except ImportError:
            print("⚠️ PyPDF2未安装，PDF解析功能不可用")
        
        try:
            from docx import Document as DocxDocument
            self.docx_available = True
        except ImportError:
            print("⚠️ python-docx未安装，DOCX解析功能不可用")
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含文档信息的字典
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return {
                "success": False,
                "error": f"文件不存在: {file_path}"
            }
        
        ext = file_path.suffix.lower()
        filename = file_path.name
        
        try:
            if ext == ".txt":
                content = self._parse_txt(file_path)
            elif ext == ".pdf":
                content = self._parse_pdf(file_path)
            elif ext in [".docx", ".doc"]:
                content = self._parse_docx(file_path)
            else:
                return {
                    "success": False,
                    "error": f"不支持的文件格式: {ext}"
                }
            
            return {
                "success": True,
                "filename": filename,
                "file_path": str(file_path),
                "file_type": ext,
                "content": content,
                "size": file_path.stat().st_size,
                "char_count": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"解析失败: {str(e)}"
            }
    
    def _parse_txt(self, file_path: Path) -> str:
        """解析TXT文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def _parse_pdf(self, file_path: Path) -> str:
        """解析PDF文件"""
        if not self.pdf_available:
            raise ImportError("PyPDF2未安装")
        
        import PyPDF2
        content = ""
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        return content.strip()
    
    def _parse_docx(self, file_path: Path) -> str:
        """解析DOCX文件"""
        if not self.docx_available:
            raise ImportError("python-docx未安装")
        
        from docx import Document
        doc = Document(file_path)
        content = ""
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        return content.strip()
    
    def batch_parse(self, file_paths: list) -> Dict[str, Dict[str, Any]]:
        """
        批量解析文档
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            文件名到解析结果的字典
        """
        results = {}
        for file_path in file_paths:
            result = self.parse(file_path)
            filename = os.path.basename(file_path)
            results[filename] = result
        return results

