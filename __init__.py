import logging
from datetime import datetime
from pathlib import Path
def run_logger(file_path: Path,level: int = logging.INFO,handler_type:str='file'):
    file_path.mkdir(parents=True, exist_ok=True)
    log_file = file_path / f"Simple_Agent_Tool_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    parent_logger=logging.getLogger('Simple_Agent_Tool')
    if not parent_logger.handlers:
        handler=None
        if handler_type=='file':
            handler = logging.FileHandler(log_file, encoding="utf-8")
        elif handler_type=='console':
            handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
            )
        )

        parent_logger.addHandler(handler)
        parent_logger.setLevel(level)
        parent_logger.info("日志初始化完成")
    else:
        parent_logger.info("日志在之前已经初始化")
run_logger(Path(__file__).parent/'logs')
from .Data import *
from .Message import *
from .ReadFile import *
from .Model import *
from .ContextManager import *
from .Tool import *
__all__ = [
    'Data',
    'BaseMessage',
    'HumanMessage',
    'SystemMessage',
    'AIMMessage',
    'HistoryMessage',
    'Model',
    'Model_no_history',
    'ReadFile',
    'BaseTool',
    'ToolMessage',
    'ToolCall',
    'Model_With_Tool',
    'AICallMessage',
    'ContextManager',
    'AsyncModel_no_history',
    'AsyncModel_With_Tool',
    'AsyncModel',
]