from typing import Dict, Any, Callable, List
from pydantic import BaseModel
from app.models.schemas import ToolInput, ToolOutput

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.dict()
        if isinstance(value, list):
            return [ToolRegistry._serialize_value(v) for v in value]
        if isinstance(value, dict):
            return {k: ToolRegistry._serialize_value(v) for k, v in value.items()}
        return value

    def register_tool(self, name: str, description: str,
                     input_schema: Dict[str, Any],
                     output_schema: Dict[str, Any],
                     function: Callable):
        """Register a tool"""
        self.tools[name] = {
            "description": description,
            "input_schema": input_schema,
            "output_schema": output_schema,
            "function": function
        }

    def get_tool(self, name: str) -> Dict[str, Any]:
        """Get tool by name"""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tools.keys())

    def call_tool(self, name: str, **kwargs) -> ToolOutput:
        """Call a tool with arguments"""
        tool = self.get_tool(name)
        if not tool:
            return ToolOutput(name=name, result=None, error=f"Tool {name} not found")

        try:
            result = tool["function"](**kwargs)
            serialized = self._serialize_value(result)
            return ToolOutput(name=name, result=result, serialized_result=serialized)
        except Exception as e:
            return ToolOutput(name=name, result=None, serialized_result=None, error=str(e))

    def get_tool_descriptions(self) -> str:
        """Get descriptions of all tools for LLM"""
        descriptions = []
        for name, tool in self.tools.items():
            desc = f"{name}: {tool['description']}\n"
            desc += f"Input: {tool['input_schema']}\n"
            desc += f"Output: {tool['output_schema']}\n"
            descriptions.append(desc)
        return "\n".join(descriptions)