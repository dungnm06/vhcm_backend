DEACTIVE_USER_RELATIVES = '''
BEGIN TRANSACTION;
UPDATE vhcm.knowledge_data_review
SET status = {review_draft_status}
WHERE id in (
	SELECT
		kdr.id
	FROM vhcm.knowledge_data kd
	INNER JOIN vhcm.user u
	ON u.user_id = kd.edit_user_id
	INNER JOIN vhcm.knowledge_data_review kdr
	ON kd.knowledge_data_id = kdr.knowledge_data_id
	WHERE u.user_id = {review_user_id}
	AND kd.status != {kd_done_status}
);
UPDATE vhcm.knowledge_data
SET status = {kd_available_status}
WHERE knowledge_data_id in (
	SELECT
		kd.knowledge_data_id
	FROM vhcm.knowledge_data kd
	INNER JOIN vhcm.user u
	ON u.user_id = kd.edit_user_id
	WHERE u.user_id = {kd_user_id}
);
COMMIT;
'''

GET_REPORTED = '''
SELECT
	cr.report_id as "report_id",
	kd.knowledge_data_id as "knowledge_data_id",
	kd.intent as "intent",
	kd.intent_fullname as "intent_fullname",
	u2.user_id as "report_user_id",
	u2.username as "report_username",
	cm.comment as "report_comment",
	cr.user_seen as "user_seen",
	cm.cdate as "cdate"
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
'''
