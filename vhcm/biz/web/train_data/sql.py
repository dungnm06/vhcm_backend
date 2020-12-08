GET_DATA = '''
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

GET_TRAIN_DATA_KNOWLEDGE_DATA_INFO = '''
SELECT
	kd.knowledge_data_id as knowledge_data_id,
	kd.intent as intent,
	kd.intent_fullname as intent_fullname,
	u.username as edit_user
FROM vhcm.train_data td
INNER JOIN vhcm.knowledge_data_train_data_link kdtd
ON td.id = kdtd.train_data_id
INNER JOIN vhcm.knowledge_data kd
ON kd.knowledge_data_id = kdtd.knowledge_data_id
INNER JOIN vhcm.user u
ON kdtd.edit_user_id = u.user_id
WHERE td.id = {id}
ORDER BY kd.knowledge_data_id
'''