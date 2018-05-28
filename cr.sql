SELECT r.record_id, r.id, r.vote_type, r.user_id, r.vote, r.voted, r.ip, r.comment_id
               FROM `wp_gdsr_votes_log` r 
               WHERE r.vote_type in ('article', 'comment') AND r.record_id NOT IN 
               (SELECT meta_value FROM `wp_gdrts_itemmeta` WHERE meta_key = 'gdsr-rating-import')
                LIMIT 500