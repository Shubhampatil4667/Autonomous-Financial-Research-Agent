import openai
import os
import re
from typing import List, Dict, Any, Optional
from app.models.schemas import AgentStep, AgentAction
from app.services.memory_service import MemoryService
from app.tools import get_tool_registry
from app.services.logging_service import logger
from app.config import settings

class ReActAgent:
    def __init__(self, max_iterations: Optional[int] = None):
        self.max_iterations = max_iterations or settings.max_iterations
        self.memory = MemoryService()
        self.tool_registry = get_tool_registry()  # Use global instance

        # Validate API key
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Initialize sync client for sync execution loop
        from openai import OpenAI
        self.client = OpenAI(api_key=settings.openai_api_key)

        logger.info(f"ReActAgent initialized with max_iterations={self.max_iterations}")

    def _extract_company_symbol(self, query: str) -> str:
        """Extract company symbol from query using regex and common patterns"""
        # Look for stock symbols (uppercase letters, 1-5 chars)
        symbol_match = re.search(r'\b[A-Z]{1,5}\b', query.upper())
        if symbol_match:
            return symbol_match.group()

        # Common company name to symbol mapping
        company_mappings = {
            'tesla': 'TSLA',
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'amazon': 'AMZN',
            'google': 'GOOGL',
            'nvidia': 'NVDA',
            'meta': 'META',
            'netflix': 'NFLX'
        }

        query_lower = query.lower()
        for company, symbol in company_mappings.items():
            if company in query_lower:
                return symbol

        # Default fallback
        return 'TSLA'

    def think(self, query: str, context: str) -> str:
        """Generate thought using LLM with optimized parameters"""
        symbol = self._extract_company_symbol(query)

        prompt = f"""
You are a financial analyst AI agent. Your task is to analyze: {query}

Extracted company symbol: {symbol}
Current context: {context}

Available tools: {self.tool_registry.get_tool_descriptions()}

Think step by step about what information you need and which tool to use next.
If you have enough information to answer, say 'FINAL ANSWER' followed by your analysis.
Otherwise, specify the tool to use and its parameters.

Format:
Thought: [your reasoning]
Action: [tool_name]
Action Input: [parameters as JSON]
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                timeout=30  # Add timeout for API calls
            )
            thought = response.choices[0].message.content.strip()
            logger.debug(f"Generated thought: {thought[:100]}...")
            return thought
        except Exception as e:
            logger.error(f"Error generating thought: {e}")
            # Check for specific OpenAI errors if possible, or use fallback
            from openai import APIError, RateLimitError, APITimeoutError
            if isinstance(e, (APITimeoutError, RateLimitError)):
                logger.warning(f"OpenAI API issue ({type(e).__name__}), using fallback reasoning")
            
            # Improved fallback reasoning
            return f"Thought: Need to gather financial data for {query}\nAction: financial_data_api\nAction Input: {{\"symbol\": \"{symbol}\"}}"

    def act(self, action_text: str) -> str:
        """Execute action"""
        """Execute action"""
        try:
            lines = action_text.split('\n')
            tool_name = ""
            tool_input = {}

            for line in lines:
                if line.startswith("Action:"):
                    tool_name = line.replace("Action:", "").strip()
                elif line.startswith("Action Input:"):
                    import json
                    input_str = line.replace("Action Input:", "").strip()
                    tool_input = json.loads(input_str)

            if tool_name and tool_input:
                logger.info(f"Executing tool: {tool_name} with input: {tool_input}")
                result = self.tool_registry.call_tool(tool_name, **tool_input)
                if result.result is not None:
                    formatted = result.serialized_result if result.serialized_result is not None else result.result
                    observation = f"Observation: {formatted}"
                else:
                    observation = f"Error: {result.error}"
                logger.debug(f"Tool execution result: {observation}")
                return observation
            else:
                logger.warning("No valid action found in action text")
                return "Observation: No valid action found"
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return f"Error executing action: {str(e)}"

    def run(self, query: str) -> str:
        """Run ReAct loop"""
        logger.info(f"Starting ReAct analysis for query: {query}")
        context = self.memory.get_short_term_context()
        steps = []

        for i in range(self.max_iterations):
            thought = self.think(query, context)
            step = AgentStep(thought=thought)

            if "FINAL ANSWER" in thought:
                final_answer = thought.split("FINAL ANSWER:")[-1].strip()
                steps.append(step)
                self.memory.store_episodic(query, steps)
                logger.info("ReAct analysis completed successfully")
                return final_answer

            observation = self.act(thought)
            step.observation = observation
            steps.append(step)
            self.memory.add_to_short_term(step)

            context += f"\n{thought}\n{observation}"

        logger.warning("ReAct analysis reached maximum iterations")
        # Fallback
        return "Analysis complete - maximum iterations reached"