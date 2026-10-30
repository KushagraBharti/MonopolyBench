import unittest

from recurrence_audit import BUILD, ERROR, analyze, compact, summarize


def unit(index, attempts, game=1, actor='p1', applied='end_turn'):
    return {'game':game,'player_id':actor,'model':'test','decision_id':f'g{game}-dec-{index:06}',
            'turn_index':index,'attempts':attempts,'applied_action_record':{'action':{'action':applied}},
            'resolution':{'fallback_used':False}}


def attempt(index=0, name=BUILD, error=False, feedback=False):
    return {'attempt_index_zero_based':index,'parsed_tool_call':{'name':name},
            'outcome':'illogical' if error else 'valid','response_condition':'standard',
            'validation_errors':[ERROR] if error else [],
            'prompt':{'payload':{'action_state':{'scenario':{'notes':[ERROR] if feedback else []}}}}}


class RecurrenceTest(unittest.TestCase):
    def rows(self, *items):
        return [compact(x, {'packet':'fixture','line':i+1}) for i,x in enumerate(items)]

    def test_feedback_requires_later_prompt(self):
        row = self.rows(unit(0,[attempt(error=True),attempt(1,feedback=True)]))[0]
        self.assertTrue(row['corrective_feedback_delivered'])
        before = self.rows(unit(0,[attempt(feedback=True),attempt(1,error=True)]))[0]
        self.assertFalse(before['corrective_feedback_delivered'])

    def test_next_decision_not_corrective_attempt(self):
        rows=self.rows(unit(0,[attempt(error=True),attempt(1,feedback=True)],applied=BUILD),
                       unit(1,[attempt(name='mortgage_property')]),unit(2,[attempt(error=True)]))
        result=analyze(rows)
        self.assertEqual(result[0]['next_decision_id'],'g1-dec-000002')
        self.assertEqual(result[0]['actor_decisions_to_next_submission'],2)
        self.assertTrue(result[0]['next_first_submission_uneven'])
        self.assertTrue(result[1]['censored_no_later_submission'])

    def test_no_cross_game_or_actor_link(self):
        result=analyze(self.rows(unit(0,[attempt(error=True)]),unit(1,[attempt()],game=2),unit(2,[attempt()],actor='p2')))
        self.assertTrue(result[0]['censored_no_later_submission'])

    def test_first_feedback_only_once(self):
        rows=self.rows(unit(0,[attempt(error=True)]),unit(1,[attempt(error=True),attempt(1,feedback=True)]),
                       unit(2,[attempt(error=True),attempt(1,feedback=True)]),unit(3,[attempt()]))
        summary=summarize(analyze(rows))
        self.assertEqual(summary['delivered_feedback']['total']['episodes'],2)
        self.assertEqual(summary['first_delivered_per_player_game']['total']['episodes'],1)

    def test_first_and_any_error_differ(self):
        rows=self.rows(unit(0,[attempt(error=True)]),unit(1,[attempt(),attempt(1,error=True)]))
        result=analyze(rows)[0]
        self.assertFalse(result['next_first_submission_uneven'])
        self.assertTrue(result['next_any_submission_uneven'])

    def test_feedback_mutation_changes_population(self):
        original=unit(0,[attempt(error=True),attempt(1,feedback=True)])
        self.assertTrue(self.rows(original)[0]['corrective_feedback_delivered'])
        original['attempts'][1]['prompt']['payload']['action_state']['scenario']['notes']=[]
        self.assertFalse(self.rows(original)[0]['corrective_feedback_delivered'])


if __name__ == '__main__':
    unittest.main()
