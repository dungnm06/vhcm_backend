GET_ALL_KNOWLEDGE_DATA = '''
    SELECT 
        kd.intent as intent,
        kd.intent_fullname as intent_fullname,
        kd.status as status,
        u.username as create_user,
        u.user_id as create_user_id,
        u2.username as edit_user,
        u2.user_id as edit_user_id,
        kd.cdate as cdate,
        kd.mdate as mdate
    FROM vhcm.knowledge_data kd
    INNER JOIN vhcm.user u
    ON kd.create_user_id = u.user_id
    INNER JOIN vhcm.user u2
    ON kd.edit_user_id = u2.user_id
'''
