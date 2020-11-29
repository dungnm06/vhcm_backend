ALL_PENDING_REPORT = '''
SELECT 
	r.id as report_id,
	r.type as report_type,
	r.reporter_id as reporter_id,
	u.username as reporter,
	r.reported_intent as reported_intent,
	r.report_data as report_data,
	td.cdate as bot_version,
	r.cdate as cdate
FROM vhcm.report r
INNER JOIN vhcm.user u
ON r.reporter_id = u.user_id
INNER JOIN vhcm.train_data td
ON r.bot_version_id = td.id
WHERE r.status = 1
'''

ALL_ACCEPTED_REPORT = '''
SELECT 
	r.id as report_id,
	r.type as report_type,
	r.reporter_id as reporter_id,
	u.username as reporter,
	r.reported_intent as reported_intent,
	r.report_data as report_data,
	r.processor_id as processor_id,
	u2.username as processor,
	kd.intent as forward_intent,
	r.mdate as mdate
FROM vhcm.report r
INNER JOIN vhcm.user u
ON r.reporter_id = u.user_id
INNER JOIN vhcm.user u2
ON r.processor_id = u2.user_id
LEFT JOIN vhcm.knowledge_data kd
ON r.forward_intent_id = kd.knowledge_data_id
WHERE r.status = 2
'''

ALL_REJECTED_REPORT = '''
SELECT 
	r.id as report_id,
	r.type as report_type,
	r.reporter_id as reporter_id,
	u.username as reporter,
	r.reported_intent as reported_intent,
	r.report_data as report_data,
	r.processor_id as processor_id,
	u2.username as processor,
	r.processor_note as reason,
	td.cdate as bot_version,
	r.mdate as mdate
FROM vhcm.report r
INNER JOIN vhcm.user u
ON r.reporter_id = u.user_id
INNER JOIN vhcm.user u2
ON r.processor_id = u2.user_id
INNER JOIN vhcm.train_data td
ON r.bot_version_id = td.id
WHERE r.status = 3
'''