"""
表格操作测试
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

API_KEY = "test-api-key-256"
HEADERS = {"X-API-Key": API_KEY}


class TestHealth:
    """健康检查测试"""
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestSheetsAPI:
    """表格API测试"""
    
    def test_read_without_auth(self):
        """测试未认证访问"""
        response = client.get("/api/v1/sheets/read?spreadsheet_id=test")
        assert response.status_code == 401
    
    def test_read_with_invalid_key(self):
        """测试无效API Key"""
        response = client.get(
            "/api/v1/sheets/read?spreadsheet_id=test",
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == 401
    
    def test_read_all(self):
        """测试读取全部数据"""
        response = client.get(
            "/api/v1/sheets/read?spreadsheet_id=test_sheet",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert len(data["data"]) > 0
    
    def test_read_cell(self):
        """测试读取单元格"""
        response = client.get(
            "/api/v1/sheets/cell?spreadsheet_id=test_sheet&row=1&col=1",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["value"] == "姓名"
    
    def test_read_range(self):
        """测试读取范围"""
        response = client.get(
            "/api/v1/sheets/range?spreadsheet_id=test_sheet&start_row=1&start_col=1&end_row=2&end_col=2",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
    
    def test_write_data(self):
        """测试写入数据"""
        response = client.post(
            "/api/v1/sheets/write",
            headers=HEADERS,
            json={
                "spreadsheet_id": "test_write",
                "data": [
                    {"row": 1, "col": 1, "value": "测试"},
                    {"row": 1, "col": 2, "value": "数据"}
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["updated_cells"] == 2
    
    def test_query_data(self):
        """测试条件查询"""
        response = client.post(
            "/api/v1/sheets/query",
            headers=HEADERS,
            json={
                "spreadsheet_id": "test_sheet",
                "conditions": [
                    {"col": 3, "operator": "eq", "value": "技术部"}
                ],
                "logic": "and"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # 应该返回表头 + 匹配的行
        assert len(data["data"]) >= 1


class TestQueryOperators:
    """查询操作符测试"""
    
    def test_query_contains(self):
        """测试包含查询"""
        response = client.post(
            "/api/v1/sheets/query",
            headers=HEADERS,
            json={
                "spreadsheet_id": "test_sheet",
                "conditions": [
                    {"col": 1, "operator": "contains", "value": "三"}
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_query_gt(self):
        """测试大于查询"""
        response = client.post(
            "/api/v1/sheets/query",
            headers=HEADERS,
            json={
                "spreadsheet_id": "test_sheet",
                "conditions": [
                    {"col": 2, "operator": "gt", "value": 28}
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
