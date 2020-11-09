GET_TRAIN_DATA = '''
SELECT 
	gq.generated_question as generated_question,
	kd.intent as intent,
	q.type as type
FROM vhcm.knowledge_data kd
INNER JOIN vhcm.knowledge_data_question q
ON kd.knowledge_data_id = q.knowledge_data_id
INNER JOIN vhcm.knowledge_data_generated_question gq
ON q.question_id = gq.question_id
WHERE kd.knowledge_data_id = ANY(VALUES {knowledge_ids})
'''