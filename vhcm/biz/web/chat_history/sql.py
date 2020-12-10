GET_ALL_CHATLOG = '''
SELECT
	ch.log_id as log_id,
	u.user_id as user_id,
	u.username as username,
	ch.session_start as session_start,
	ch.session_end as session_end,
	ch.data_version_id as bot_version
FROM vhcm.chat_history ch
INNER JOIN vhcm.user u
ON ch.user_id = u.user_id
ORDER BY ch.session_end DESC
'''