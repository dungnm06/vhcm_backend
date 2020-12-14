INTENT_STATS = '''
SELECT
	kd.intent as intent,
	kd.status as status,
	kdr.status as review_status,
	COUNT(kdr.id) as review_count
FROM vhcm.knowledge_data kd
LEFT JOIN vhcm.knowledge_data_review kdr
ON kdr.knowledge_data_id = kd.knowledge_data_id 
WHERE kd.edit_user_id = {user_id}
AND kd.status in (1,2)
GROUP BY kd.intent, kd.status, kdr.status
'''

DRAFT_COUNT = '''
SELECT
	COUNT(kdr.id) as draft_count
FROM vhcm.knowledge_data_review kdr
WHERE kdr.status = 3
AND kdr.review_user_id = {user_id}
'''

INTENT_DONE_BY_MONTH = '''
SELECT 
	COUNT(kd.intent) as intent_done,
	to_char(mmyy, 'MM/YY') as month
FROM generate_series(now() - INTERVAL '6 month', now(), '1 month') as mmyy
LEFT JOIN vhcm.knowledge_data kd 
ON (
	to_char(mmyy, 'YY') = to_char(kd.mdate, 'YY') 
	AND to_char(mmyy, 'MM') = to_char(kd.mdate, 'MM') 
	AND kd.status = 2
)
GROUP BY mmyy
ORDER BY mmyy ASC
'''

GLOBAL_INTENT_STATS = '''
SELECT
	kd.status as status,
	COUNT(kd.intent) as intent_count
FROM vhcm.knowledge_data kd
GROUP BY kd.status
'''

UNSEEN_REPORT = '''
SELECT
    COUNT(cr.id) as "count"
FROM vhcm.knowledge_data_comment_report cr
INNER JOIN vhcm.user u
ON cr.report_to_id = u.user_id
INNER JOIN vhcm.knowledge_data_comment cm
ON cm.id = cr.comment_id
INNER JOIN vhcm.knowledge_data kd
ON cm.knowledge_data_id = kd.knowledge_data_id
INNER JOIN vhcm.user u2
ON u2.user_id = cm.user_id
WHERE u.user_id = {user_id}
AND cr.user_seen = false
'''
