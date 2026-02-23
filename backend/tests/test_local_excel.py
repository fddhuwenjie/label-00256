"""
本地 Excel API 集成测试
"""
import pytest
import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app


class TestLocalExcelAPI:
    """本地 Excel API 集成测试"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def api_key(self):
        return "test-api-key-256"
    
    @pytest.fixture
    def local_file_key(self):
        return "local-file-key-256"
    
    def test_export_and_download(self, client, local_file_key):
        """测试导出并下载 xlsx 文件"""
        # 导出数据
        export_response = client.post(
            "/api/v1/sheets/local/export",
            json={
                "data": [
                    ["Name", "Age", "City"],
                    ["Alice", 25, "Beijing"],
                    ["Bob", 30, "Shanghai"]
                ],
                "filename": "test_export.xlsx",
                "sheet_name": "TestSheet"
            },
            headers={"X-API-Key": local_file_key}
        )
        
        assert export_response.status_code == 200
        result = export_response.json()
        assert result["success"] == True
        assert "file_id" in result["data"]
        
        file_id = result["data"]["file_id"]
        
        # 下载文件
        download_response = client.get(
            f"/api/v1/sheets/local/download/{file_id}",
            headers={"X-API-Key": local_file_key}
        )
        
        assert download_response.status_code == 200
        assert "spreadsheetml" in download_response.headers.get("content-type", "")
        
        # 清理：删除文件
        delete_response = client.delete(
            f"/api/v1/sheets/local/{file_id}",
            headers={"X-API-Key": local_file_key}
        )
        assert delete_response.status_code == 200
    
    def test_list_files(self, client, api_key):
        """测试列出文件"""
        response = client.get(
            "/api/v1/sheets/local/files",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert "uploads" in result["data"]
        assert "exports" in result["data"]
    
    def test_download_not_found(self, client, api_key):
        """测试下载不存在的文件"""
        response = client.get(
            "/api/v1/sheets/local/download/nonexistent_file_id",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 404
    
    def test_delete_not_found(self, client, local_file_key):
        """测试删除不存在的文件"""
        response = client.delete(
            "/api/v1/sheets/local/nonexistent_file_id",
            headers={"X-API-Key": local_file_key}
        )
        
        assert response.status_code == 404
    
    def test_permission_denied_without_local_permission(self, client):
        """测试无 local 权限时被拒绝"""
        readonly_key = "readonly-key-256"
        
        # 尝试导出（需要 local 权限）
        response = client.post(
            "/api/v1/sheets/local/export",
            json={"data": [["test"]]},
            headers={"X-API-Key": readonly_key}
        )
        
        assert response.status_code == 403
    
    def test_upload_invalid_file_type(self, client, local_file_key):
        """测试上传非 xlsx 文件"""
        # 创建一个假的 txt 文件
        fake_file = io.BytesIO(b"This is not an xlsx file")
        
        response = client.post(
            "/api/v1/sheets/local/upload",
            files={"file": ("test.txt", fake_file, "text/plain")},
            headers={"X-API-Key": local_file_key}
        )
        
        assert response.status_code == 400
    
    def test_read_nonexistent_file(self, client, api_key):
        """测试读取不存在的文件"""
        response = client.get(
            "/api/v1/sheets/local/read/nonexistent_file_id",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 400


class TestLocalExcelWithRealFile:
    """使用真实 xlsx 文件的测试（需要 openpyxl）"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def local_file_key(self):
        return "local-file-key-256"
    
    @pytest.fixture
    def xlsx_file(self):
        """创建测试用的 xlsx 文件"""
        try:
            from openpyxl import Workbook
            
            wb = Workbook()
            ws = wb.active
            ws.title = "TestData"
            
            # 写入测试数据
            data = [
                ["ID", "Name", "Score"],
                [1, "Alice", 95],
                [2, "Bob", 87],
                [3, "Charlie", 92]
            ]
            
            for row_idx, row in enumerate(data, 1):
                for col_idx, value in enumerate(row, 1):
                    ws.cell(row=row_idx, column=col_idx, value=value)
            
            # 保存到内存
            file_stream = io.BytesIO()
            wb.save(file_stream)
            file_stream.seek(0)
            
            return file_stream
        except ImportError:
            pytest.skip("openpyxl not installed")
    
    def test_upload_and_read_xlsx(self, client, local_file_key, xlsx_file):
        """测试上传并读取 xlsx 文件"""
        # 上传文件
        upload_response = client.post(
            "/api/v1/sheets/local/upload",
            files={"file": ("test_data.xlsx", xlsx_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers={"X-API-Key": local_file_key}
        )
        
        assert upload_response.status_code == 200
        result = upload_response.json()
        assert result["success"] == True
        
        file_id = result["data"]["file_id"]
        assert result["data"]["row_count"] == 4
        assert result["data"]["column_count"] == 3
        
        # 读取文件
        read_response = client.get(
            f"/api/v1/sheets/local/read/{file_id}",
            headers={"X-API-Key": local_file_key}
        )
        
        assert read_response.status_code == 200
        read_result = read_response.json()
        assert read_result["success"] == True
        assert read_result["data"]["row_count"] == 4
        
        # 读取指定范围
        range_response = client.get(
            f"/api/v1/sheets/local/read/{file_id}?range=A1:B2",
            headers={"X-API-Key": local_file_key}
        )
        
        assert range_response.status_code == 200
        
        # 清理
        client.delete(
            f"/api/v1/sheets/local/{file_id}",
            headers={"X-API-Key": local_file_key}
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
