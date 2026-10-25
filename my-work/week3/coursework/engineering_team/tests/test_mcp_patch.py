import asyncio
import runpy
import unittest
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from crewai.mcp.tool_resolver import MCPToolResolver
from mcp.types import TextContent


class MCPNameRegressionTest(unittest.TestCase):
    def test_discovered_name_is_preserved_through_execution(self):
        runpy.run_path(str(Path(__file__).resolve().parents[1] / 'src/engineering_team/patch.py'))
        session = AsyncMock()
        session.list_tools.return_value = SimpleNamespace(tools=[
            SimpleNamespace(name='resolve-library-id', description='Find library',
                            inputSchema={'type': 'object', 'properties': {}}),
            SimpleNamespace(name='query-docs', description='Read docs',
                            inputSchema={'type': 'object', 'properties': {}}),
        ])
        session.call_tool.return_value = SimpleNamespace(
            content=[TextContent(type='text', text='Gradio documentation')])

        @asynccontextmanager
        async def transport(*args, **kwargs):
            yield None, None, None

        @asynccontextmanager
        async def client(*args, **kwargs):
            yield session

        resolver = MCPToolResolver(agent=None, logger=Mock())
        with patch('mcp.client.streamable_http.streamablehttp_client', transport), \
             patch('mcp.ClientSession', client):
            tools = resolver.resolve(['https://mcp.context7.com/mcp#resolve-library-id'])
            self.assertEqual(len(tools), 1)
            tool = tools[0]
            self.assertIn('resolve_library_id', tool.name)
            self.assertEqual(tool.original_tool_name, 'resolve-library-id')
            result = asyncio.run(tool._execute_tool(libraryName='gradio', query='Blocks'))
            self.assertEqual(result, 'Gradio documentation')
            session.call_tool.assert_awaited_once_with(
                'resolve-library-id', {'libraryName': 'gradio', 'query': 'Blocks'})


if __name__ == '__main__':
    unittest.main()
