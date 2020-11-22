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