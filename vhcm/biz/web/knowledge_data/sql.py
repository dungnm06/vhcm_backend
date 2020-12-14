GET_ALL_KNOWLEDGE_DATA = '''
SELECT 
	kd.knowledge_data_id as knowledge_data_id,
	kd.intent as intent,
	kd.intent_fullname as intent_fullname,
	kd.status as status,
	u.username as create_user,
	u.user_id as create_user_id,
	u2.username as edit_user,
	u2.user_id as edit_user_id,
	kd.cdate as cdate,
	kd.mdate as mdate,
	COALESCE(kd_accept.accept_count, 0) as accept_count,
	COALESCE(kd_reject.refuse_count, 0) as refuse_count,
	kdr_user.status as user_review
FROM vhcm.knowledge_data kd
INNER JOIN vhcm.user u
ON kd.create_user_id = u.user_id
INNER JOIN vhcm.user u2
ON kd.edit_user_id = u2.user_id
LEFT JOIN (
	SELECT
		kd1.knowledge_data_id,
		COUNT(kd1.knowledge_data_id) as accept_count
	FROM vhcm.knowledge_data kd1
	INNER JOIN vhcm.knowledge_data_review kdr1
	ON kdr1.knowledge_data_id = kd1.knowledge_data_id
	WHERE kdr1.status = 1
	GROUP BY kd1.knowledge_data_id
) kd_accept
ON kd_accept.knowledge_data_id = kd.knowledge_data_id
LEFT JOIN (
	SELECT
		kd2.knowledge_data_id,
		COUNT(kd2.knowledge_data_id) as refuse_count
	FROM vhcm.knowledge_data kd2
	INNER JOIN vhcm.knowledge_data_review kdr2
	ON kdr2.knowledge_data_id = kd2.knowledge_data_id
	WHERE kdr2.status = 2
	GROUP BY kd2.knowledge_data_id
) kd_reject
ON kd_reject.knowledge_data_id = kd.knowledge_data_id
LEFT JOIN (
	SELECT
		kd3.knowledge_data_id,
		kdr3.status
	FROM vhcm.knowledge_data kd3
	INNER JOIN vhcm.knowledge_data_review kdr3
	ON kdr3.knowledge_data_id = kd3.knowledge_data_id
	WHERE kdr3.review_user_id = {user_id}
) kdr_user
ON kdr_user.knowledge_data_id = kd.knowledge_data_id
{sql_filter}
ORDER BY kd.mdate
'''

GET_ALL_TRAINABLE_KNOWLEDGE_DATA = '''
SELECT 
    kd.knowledge_data_id as id,
    kd.intent as intent,
    kd.intent_fullname as intent_fullname,
    u.username as edit_user,
    u.user_id as edit_user_id,
    kd.cdate as cdate,
    kd.mdate as mdate
FROM vhcm.knowledge_data kd
INNER JOIN vhcm.user u
ON kd.edit_user_id = u.user_id
WHERE kd.status = 2
ORDER BY kd.mdate DESC
'''

GET_LATEST_KNOWLEDGE_DATA_TRAIN_DATA = '''
SELECT
	result_data.knowledge_data_id as knowledge_data_id,
	result_data.id as train_data_id,
	result_data.filename as train_data
FROM (
	SELECT 
		kd.knowledge_data_id,
		td.id,
		td.filename,
  		RANK() OVER (PARTITION BY kd.knowledge_data_id ORDER BY td.mdate DESC)
  	FROM vhcm.knowledge_data kd
	INNER JOIN vhcm.user u
	ON kd.edit_user_id = u.user_id
	LEFT JOIN vhcm.knowledge_data_train_data_link kdtd
	ON kd.knowledge_data_id = kdtd.knowledge_data_id
	INNER JOIN vhcm.train_data td
	ON td.id = kdtd.train_data_id
	WHERE kd.knowledge_data_id = ANY(VALUES {knowledge_datas})
) result_data
WHERE result_data.rank <= 3
'''

GET_ALL_REVIEWS = '''
SELECT 
	u.user_id as user_id,
	u.username as username,
	kdr.status as status,
	kdr.review_detail as review,
	kdr.mdate as mdate
FROM vhcm.knowledge_data_review kdr
INNER JOIN vhcm.user u
ON kdr.review_user_id = u.user_id
WHERE kdr.status != 3
AND kdr.knowledge_data_id = {knowledge_data_id}
'''

GET_ALL_COMMENTS = '''
SELECT
	cm.id as "id",
	cm.reply_to_id as "reply_to",
	cm.comment as "comment",
	cm.status as "status",
	cm.edited as "edited",
	cm.able_to_delete as "able_to_delete",
	cm.mdate as "mdate",
	u.user_id as "user",
	u.username as "username",
	u.fullname as "user_fullname",
	u.email as "user_email",
	u.avatar as "user_avatar",
	cru.report_id as "report_id",
	cru.report_to_id as "report_to",
	cru.username as "report_to_username"
FROM vhcm.knowledge_data_comment cm
INNER JOIN vhcm.user u
ON cm.user_id = u.user_id
LEFT JOIN (
	SELECT
		cr.comment_id,
		cr.report_id,
		cr.report_to_id,
		u2.username
	FROM vhcm.knowledge_data_comment_report cr
	INNER JOIN vhcm.user u2
	ON cr.report_to_id = u2.user_id
) cru
ON cm.id = cru.comment_id
WHERE cm.knowledge_data_id = {knowledge_data_id}
ORDER BY cm.cdate DESC
'''

UPDATE_REPORT_SEEN_STATE = '''
UPDATE vhcm.knowledge_data_comment_report
SET user_seen = true
WHERE id in (
	SELECT
		cr.id
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
	AND kd.knowledge_data_id = {knowledge_data_id}
)
'''
