"""Verify OpenAI agent settings reach the SDK without making API requests."""
import os
import unittest
from unittest.mock import patch

from openai.types.chat import ChatCompletion

from engineering_team.crew import EngineeringTeam


class OpenAISettingsTest(unittest.TestCase):
    def test_openai_agents_forward_reasoning_and_output_budget(self):
        response = ChatCompletion(
            id='offline-response', object='chat.completion', created=0,
            model='gpt-5.5', choices=[{
                'index': 0, 'finish_reason': 'stop',
                'message': {'role': 'assistant', 'content': 'Ready'},
            }], usage={'prompt_tokens': 1, 'completion_tokens': 1, 'total_tokens': 2},
        )
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'offline-test',
            'GOOGLE_API_KEY': 'offline-test',
            'ANTHROPIC_API_KEY': 'offline-test',
        }):
            team = EngineeringTeam()
            for name in ('engineering_lead', 'test_engineer'):
                with self.subTest(agent=name):
                    llm = getattr(team, name)().llm
                    resource = llm._get_sync_client().chat.completions
                    with patch.object(resource, 'create', return_value=response) as create:
                        self.assertEqual(llm.call([{'role': 'user', 'content': 'Ready?'}]), 'Ready')
                    self.assertEqual(create.call_args.kwargs.get('reasoning_effort'), 'none')
                    self.assertEqual(create.call_args.kwargs.get('max_completion_tokens'), 24000)


if __name__ == '__main__':
    unittest.main()
