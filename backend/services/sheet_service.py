"""
表格服务模块
支持表格数据缓存（TTL 5分钟）
"""
from typing import List, Any, Optional, Dict, Tuple
from datetime import datetime, timedelta
from core.logger import logger
from core.exceptions import SheetNotFoundError, CellNotFoundError, InvalidParameterError
from models.schemas import (
    CellData, QueryCondition, QueryOperator
)
from .wecom import wecom_service


class SheetDataCache:
    """表格数据缓存"""
    
    DEFAULT_TTL = 300  # 默认 5 分钟
    
    def __init__(self, ttl: int = DEFAULT_TTL):
        self.ttl = ttl
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
    
    def _make_key(self, spreadsheet_id: str, sheet_id: str, range_str: str) -> str:
        """生成缓存 key"""
        return f"{spreadsheet_id}:{sheet_id}:{range_str}"
    
    def get(self, spreadsheet_id: str, sheet_id: str, range_str: str) -> Optional[Any]:
        """获取缓存数据"""
        key = self._make_key(spreadsheet_id, sheet_id, range_str)
        if key not in self._cache:
            return None
        
        data, cached_at = self._cache[key]
        if datetime.now() - cached_at > timedelta(seconds=self.ttl):
            # 缓存过期
            del self._cache[key]
            logger.debug(f"缓存过期: {key}")
            return None
        
        logger.debug(f"缓存命中: {key}")
        return data
    
    def set(self, spreadsheet_id: str, sheet_id: str, range_str: str, data: Any):
        """设置缓存数据"""
        key = self._make_key(spreadsheet_id, sheet_id, range_str)
        self._cache[key] = (data, datetime.now())
        logger.debug(f"缓存写入: {key}")
    
    def invalidate(self, spreadsheet_id: str, sheet_id: Optional[str] = None):
        """使缓存失效（写入后调用）"""
        prefix = f"{spreadsheet_id}:"
        if sheet_id:
            prefix = f"{spreadsheet_id}:{sheet_id}:"
        
        keys_to_delete = [k for k in self._cache.keys() if k.startswith(prefix)]
        for key in keys_to_delete:
            del self._cache[key]
        
        if keys_to_delete:
            logger.info(f"缓存失效: {len(keys_to_delete)} 条记录")
    
    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
        logger.info("缓存已清空")


class SheetService:
    """表格操作服务"""
    
    # Mock数据存储（用于开发测试）
    _mock_data: Dict[str, List[List[Any]]] = {}
    
    def __init__(self):
        self.use_mock = not wecom_service.is_configured
        self._cache = SheetDataCache()  # 表格数据缓存
        if self.use_mock:
            logger.warning("企业微信未配置，使用Mock模式")
            self._init_mock_data()
    
    def _init_mock_data(self):
        """初始化Mock数据"""
        self._mock_data["test_sheet"] = [
            ["姓名", "年龄", "部门", "入职日期"],
            ["张三", 28, "技术部", "2023-01-15"],
            ["李四", 32, "产品部", "2022-06-20"],
            ["王五", 25, "测试部", "2023-08-01"],
            ["赵六", 30, "技术部", "2021-03-10"],
        ]
    
    def _col_to_letter(self, col: int) -> str:
        """列号转字母（1->A, 2->B, ...）"""
        result = ""
        while col > 0:
            col -= 1
            result = chr(col % 26 + ord('A')) + result
            col //= 26
        return result
    
    def _make_range(self, start_row: int, start_col: int, end_row: int, end_col: int) -> str:
        """生成范围字符串（如 A1:C5）"""
        start = f"{self._col_to_letter(start_col)}{start_row}"
        end = f"{self._col_to_letter(end_col)}{end_row}"
        return f"{start}:{end}"
    
    async def write_data(
        self,
        spreadsheet_id: str,
        sheet_id: Optional[str],
        data: List[CellData]
    ) -> int:
        """写入数据到表格"""
        if not data:
            return 0
        
        if self.use_mock:
            return self._mock_write(spreadsheet_id, data)
        
        # 按行组织数据
        rows_data: Dict[int, Dict[int, Any]] = {}
        for cell in data:
            if cell.row not in rows_data:
                rows_data[cell.row] = {}
            rows_data[cell.row][cell.col] = cell.value
        
        # 计算范围
        min_row = min(rows_data.keys())
        max_row = max(rows_data.keys())
        min_col = min(min(cols.keys()) for cols in rows_data.values())
        max_col = max(max(cols.keys()) for cols in rows_data.values())
        
        # 构建二维数组
        values = []
        for row in range(min_row, max_row + 1):
            row_values = []
            for col in range(min_col, max_col + 1):
                value = rows_data.get(row, {}).get(col, "")
                row_values.append(value)
            values.append(row_values)
        
        range_str = self._make_range(min_row, min_col, max_row, max_col)
        
        await wecom_service.write_sheet_data(
            spreadsheet_id,
            sheet_id or "Sheet1",
            range_str,
            values
        )
        
        # 写入后使相关缓存失效
        self._cache.invalidate(spreadsheet_id, sheet_id)
        
        logger.info(f"写入表格成功: {spreadsheet_id}, 范围: {range_str}, 单元格数: {len(data)}")
        return len(data)
    
    def _mock_write(self, spreadsheet_id: str, data: List[CellData]) -> int:
        """Mock写入"""
        if spreadsheet_id not in self._mock_data:
            self._mock_data[spreadsheet_id] = []
        
        sheet = self._mock_data[spreadsheet_id]
        
        for cell in data:
            if cell.row < 1 or cell.col < 1:
                raise InvalidParameterError(f"行号和列号必须 >= 1，当前: row={cell.row}, col={cell.col}")
            # 扩展行
            while len(sheet) < cell.row:
                sheet.append([])
            # 扩展列
            while len(sheet[cell.row - 1]) < cell.col:
                sheet[cell.row - 1].append(None)
            # 写入值
            sheet[cell.row - 1][cell.col - 1] = cell.value
        
        # 写入后使相关缓存失效
        self._cache.invalidate(spreadsheet_id)
        
        logger.info(f"[Mock] 写入表格: {spreadsheet_id}, 单元格数: {len(data)}")
        return len(data)
    
    async def read_all(
        self,
        spreadsheet_id: str,
        sheet_id: Optional[str]
    ) -> List[List[Any]]:
        """读取全部数据（带缓存）"""
        if self.use_mock:
            return self._mock_read_all(spreadsheet_id)
        
        sheet = sheet_id or "Sheet1"
        range_str = "A1:ZZ10000"
        
        # 检查缓存
        cached = self._cache.get(spreadsheet_id, sheet, range_str)
        if cached is not None:
            return cached
        
        # 先获取表格信息确定范围
        info = await wecom_service.get_spreadsheet_info(spreadsheet_id)
        # 读取数据
        result = await wecom_service.read_sheet_data(
            spreadsheet_id,
            sheet,
            range_str
        )
        
        data = result.get("data", [])
        
        # 写入缓存
        self._cache.set(spreadsheet_id, sheet, range_str, data)
        
        return data
    
    def _mock_read_all(self, spreadsheet_id: str) -> List[List[Any]]:
        """Mock读取全部"""
        if spreadsheet_id not in self._mock_data:
            # 返回默认测试数据
            return self._mock_data.get("test_sheet", [])
        return self._mock_data[spreadsheet_id]
    
    async def read_cell(
        self,
        spreadsheet_id: str,
        sheet_id: Optional[str],
        row: int,
        col: int
    ) -> Any:
        """读取单元格（带缓存）"""
        if self.use_mock:
            return self._mock_read_cell(spreadsheet_id, row, col)
        
        sheet = sheet_id or "Sheet1"
        range_str = self._make_range(row, col, row, col)
        
        # 检查缓存
        cached = self._cache.get(spreadsheet_id, sheet, range_str)
        if cached is not None:
            return cached
        
        result = await wecom_service.read_sheet_data(
            spreadsheet_id,
            sheet,
            range_str
        )
        
        data = result.get("data", [[]])
        value = data[0][0] if data and data[0] else None
        
        # 写入缓存
        self._cache.set(spreadsheet_id, sheet, range_str, value)
        
        return value
    
    def _mock_read_cell(self, spreadsheet_id: str, row: int, col: int) -> Any:
        """Mock读取单元格"""
        data = self._mock_data.get(spreadsheet_id) or self._mock_data.get("test_sheet", [])
        
        if row > len(data) or row < 1:
            raise CellNotFoundError(f"行 {row} 不存在")
        if col > len(data[row - 1]) or col < 1:
            raise CellNotFoundError(f"列 {col} 不存在")
        
        return data[row - 1][col - 1]
    
    async def read_range(
        self,
        spreadsheet_id: str,
        sheet_id: Optional[str],
        start_row: int,
        start_col: int,
        end_row: int,
        end_col: int
    ) -> List[List[Any]]:
        """读取范围（带缓存）"""
        if self.use_mock:
            return self._mock_read_range(spreadsheet_id, start_row, start_col, end_row, end_col)
        
        sheet = sheet_id or "Sheet1"
        range_str = self._make_range(start_row, start_col, end_row, end_col)
        
        # 检查缓存
        cached = self._cache.get(spreadsheet_id, sheet, range_str)
        if cached is not None:
            return cached
        
        result = await wecom_service.read_sheet_data(
            spreadsheet_id,
            sheet,
            range_str
        )
        
        data = result.get("data", [])
        
        # 写入缓存
        self._cache.set(spreadsheet_id, sheet, range_str, data)
        
        return data
    
    def _mock_read_range(
        self,
        spreadsheet_id: str,
        start_row: int,
        start_col: int,
        end_row: int,
        end_col: int
    ) -> List[List[Any]]:
        """Mock读取范围"""
        data = self._mock_data.get(spreadsheet_id) or self._mock_data.get("test_sheet", [])
        
        result = []
        for row_idx in range(start_row - 1, min(end_row, len(data))):
            row_data = []
            for col_idx in range(start_col - 1, min(end_col, len(data[row_idx]) if row_idx < len(data) else 0)):
                if row_idx < len(data) and col_idx < len(data[row_idx]):
                    row_data.append(data[row_idx][col_idx])
                else:
                    row_data.append(None)
            result.append(row_data)
        
        return result
    
    async def query(
        self,
        spreadsheet_id: str,
        sheet_id: Optional[str],
        conditions: List[QueryCondition],
        logic: str = "and"
    ) -> List[List[Any]]:
        """条件查询"""
        # 先读取全部数据
        all_data = await self.read_all(spreadsheet_id, sheet_id)
        
        if not all_data or len(all_data) < 2:
            return []
        
        # 第一行为表头
        header = all_data[0]
        rows = all_data[1:]
        
        # 过滤
        result = [header]
        for row in rows:
            if self._match_conditions(row, conditions, logic):
                result.append(row)
        
        return result
    
    def _match_conditions(
        self,
        row: List[Any],
        conditions: List[QueryCondition],
        logic: str
    ) -> bool:
        """检查行是否匹配条件"""
        results = []
        
        for cond in conditions:
            col_idx = cond.col - 1
            if col_idx >= len(row):
                results.append(False)
                continue
            
            cell_value = row[col_idx]
            match = self._compare(cell_value, cond.operator, cond.value)
            results.append(match)
        
        if logic == "or":
            return any(results)
        return all(results)
    
    def _compare(self, cell_value: Any, operator: QueryOperator, compare_value: Any) -> bool:
        """比较值"""
        try:
            if operator == QueryOperator.EQ:
                return str(cell_value) == str(compare_value)
            elif operator == QueryOperator.NE:
                return str(cell_value) != str(compare_value)
            elif operator == QueryOperator.GT:
                return float(cell_value) > float(compare_value)
            elif operator == QueryOperator.GE:
                return float(cell_value) >= float(compare_value)
            elif operator == QueryOperator.LT:
                return float(cell_value) < float(compare_value)
            elif operator == QueryOperator.LE:
                return float(cell_value) <= float(compare_value)
            elif operator == QueryOperator.CONTAINS:
                return str(compare_value) in str(cell_value)
            elif operator == QueryOperator.STARTS_WITH:
                return str(cell_value).startswith(str(compare_value))
            elif operator == QueryOperator.ENDS_WITH:
                return str(cell_value).endswith(str(compare_value))
        except (ValueError, TypeError):
            return False
        
        return False


# 单例
sheet_service = SheetService()
