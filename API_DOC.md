# API Documentation (Parameters + Types + Examples)

Base URL: http://127.0.0.1:8000

## Auth

### POST /api/v1/login
- Path params: none
- Query params: none
- Body params: `email` (string), `password` (string)
- Example (success):
  - URL: /api/v1/login
  - Body:
    {"email":"user@example.com","password":"secret123"}
- Success response example:
  {"code":200,"msg":"success","data":{"access_token":"xxxx","email":"81005762@qq.com","user_id":"b024f8bf-a96c-4d5a-a8d6-a033e5720c93"}}

### POST /api/v1/register
- Path params: none
- Query params: none
- Body params: `email` (string), `password` (string)
- Example (success):
  - URL: /api/v1/register
  - Body:
    {"email":"user@example.com","password":"secret123"}
- Success response example:
  {"code":200,"msg":"success","data":{"access_token":"xxxx","email":"81005762@qq.com","user_id":"b024f8bf-a96c-4d5a-a8d6-a033e5720c93"}}

## Profile

### GET /api/v1/profile/get_profile
- Path params: none
- Query params: `id` (string, uuid)
- Body params: none
- Example (success):
  - URL: /api/v1/profile/get_profile?id=37ed0792-5e07-449a-bf68-2e6252bcad7d
- Success response example:
  {"code":200,"msg":"success","data":{"id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","email":"81005762@qq.com","username":"alice","avatar_url":"https://example.com/avatar.png","bio":"hello"}}

### PUT /api/v1/profile/update_profile
- Path params: none
- Query params: none
- Body params: `id` (string, uuid), `username` (string, optional), `avatar_url` (string, optional), `bio` (string, optional)
- Example (success):
  - URL: /api/v1/profile/update_profile
  - Body:
    {"id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","username":"alice","bio":"hello"}
- Success response example:
  {"code":200,"msg":"success","data":{"id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","username":"alice","avatar_url":"https://example.com/avatar.png","bio":"hello"}}

## Persona

### PUT /api/v1/persona/update_stats
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid), `category` (string), `tags` (list[string]), `duration` (int)
- Example (success):
  - URL: /api/v1/persona/update_stats
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","category":"AI??","tags":["AI","RAG"],"duration":12}
- Success response example:
  {"code":200,"msg":"success","data":{"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","category":"AI??","tags":["AI","RAG"],"duration":12,"updated_at":1700000000}}

### POST /api/v1/persona/update_available
- Path params: none
- Query params: none
- Body params: `id` (string, uuid)
- Example (success):
  - URL: /api/v1/persona/update_available
  - Body:
    {"id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  {"code":200,"msg":"success","data":{"id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","available":true}}

## Words

### POST /api/v1/words
- Path params: none
- Query params: none
- Body params: `author_id` (string, uuid), `word_url` (string), `category` (string), `tags` (list[object]), `word_name` (string, optional)
- Example (success):
  - URL: /api/v1/words
  - Body:
    {"author_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","word_url":"https://example.com/doc","category":"AI??","tags":[{"id":"ai","display_content":"AI","create_time":0}],"word_name":"AI intro"}
- Success response example:
  {"code":200,"msg":"success","data":{"word_id":"11111111-1111-1111-1111-111111111111","author_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","word_url":"https://example.com/doc","category":"AI??","tags":[{"id":"ai","display_content":"AI","create_time":0}],"word_name":"AI intro","status":"draft","created_at":1700000000}}

### PUT /api/v1/words/{id}
- Path params: `id` (string, uuid)
- Query params: `author_id` (string, uuid)
- Body params: arbitrary JSON payload (object)
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111?author_id=37ed0792-5e07-449a-bf68-2e6252bcad7d
  - Body:
    {"word_name":"New title"}
- Success response example:
  {"code":200,"msg":"success","data":{"word_id":"11111111-1111-1111-1111-111111111111","updated_fields":{"word_name":"New title"},"updated_at":1700000100}}

### POST /api/v1/words/{id}/submit
- Path params: `id` (string, uuid)
- Query params: `author_id` (string, uuid)
- Body params: none
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111/submit?author_id=37ed0792-5e07-449a-bf68-2e6252bcad7d
- Success response example:
  {"code":200,"msg":"success","data":{"id":"11111111-1111-1111-1111-111111111111","status":"submitted"}}

### POST /api/v1/words/{id}/publish
- Path params: `id` (string, uuid)
- Query params: `admin_id` (string, uuid)
- Body params: none
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111/publish?admin_id=37ed0792-5e07-449a-bf68-2e6252bcad7d
- Success response example:
  {"code":200,"msg":"success","data":{"id":"11111111-1111-1111-1111-111111111111","status":"published"}}

### POST /api/v1/words/{id}/reject
- Path params: `id` (string, uuid)
- Query params: `admin_id` (string, uuid), `reson` (string)
- Body params: none
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111/reject?admin_id=37ed0792-5e07-449a-bf68-2e6252bcad7d&reson=manual
- Success response example:
  {"code":200,"msg":"success","data":{"id":"11111111-1111-1111-1111-111111111111","status":"rejected","reason":"manual"}}

### POST /api/v1/words/{id}/archive
- Path params: `id` (string, uuid)
- Query params: none
- Body params: `admin_id` (string, uuid)
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111/archive
  - Body:
    {"admin_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  {"code":200,"msg":"success","data":{"id":"11111111-1111-1111-1111-111111111111","status":"archived"}}

### DELETE /api/v1/words/{id}
- Path params: `id` (string, uuid)
- Query params: none
- Body params: none
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111
- Success response example:
  {"code":200,"msg":"success","data":{"id":"11111111-1111-1111-1111-111111111111","deleted":true}}

### GET /api/v1/words/{id}
- Path params: `id` (string, uuid)
- Query params: none
- Body params: none
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111
- Success response example:
  {"code":200,"msg":"success","data":{"word_id":"11111111-1111-1111-1111-111111111111","author_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","word_url":"https://example.com/doc","category":"AI??","tags":[{"id":"ai","display_content":"AI","create_time":0}],"word_name":"AI intro","status":"published","created_at":1700000000}}

### GET /api/v1/words/{id}/events
- Path params: `id` (string, uuid)
- Query params: none
- Body params: none
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111/events
- Success response example:
  {"code":200,"msg":"success","data":[{"id":"e1","type":"publish","actor_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","created_at":1700000200}]}

### GET /api/v1/words/feeds
- Path params: none
- Query params: `mode` (string: latest|recommend|follow), `category` (string, optional), `user_id` (string, uuid, optional), `limit` (int, optional)
- Body params: none
- Example (success):
  - URL: /api/v1/words/feeds?mode=latest&limit=20
- Success response example:
  {"code":200,"msg":"success","data":[{"word_id":"11111111-1111-1111-1111-111111111111","word_name":"AI intro","category":"AI??","author_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","created_at":1700000000}]}

## AI

### POST /api/v1/ai/search
- Path params: none
- Query params: none
- Body params: `u_id` (string, uuid), `query` (string)
- Example (success):
  - URL: /api/v1/ai/search
  - Body:
    {"u_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","query":"vector search"}
- Success response example:
  {"code":200,"msg":"success","data":{"results":[{"word_id":"11111111-1111-1111-1111-111111111111","word_name":"AI intro","score":0.92}]}}

### POST /api/v1/ai/review
- Path params: none
- Query params: `id` (string, uuid)
- Body params: none
- Example (success):
  - URL: /api/v1/ai/review?id=11111111-1111-1111-1111-111111111111
- Success response example:
  {"code":200,"msg":"success","data":{"id":"11111111-1111-1111-1111-111111111111","reviewed":true}}

### POST /api/v1/ai/assist/post
- Path params: none
- Query params: none
- Body params: `content` (string)
- Example (success):
  - URL: /api/v1/ai/assist/post
  - Body:
    {"content":"A short post about IntelliJ and Continue."}
- Success response example:
  {"code":200,"msg":"success","data":{"content":"A short post about IntelliJ and Continue.","suggestions":["Add a hook","Include a CTA"]}}

## Comments

### POST /api/v1/posts/{post_id}/comments
- Path params: `post_id` (string, uuid)
- Query params: none
- Body params: `author_id` (string, uuid), `content` (string)
- Example (success):
  - URL: /api/v1/posts/11111111-1111-1111-1111-111111111111/comments
  - Body:
    {"author_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","content":"Nice post"}
- Success response example:
  {"code":200,"msg":"success","data":{"comment_id":"22222222-2222-2222-2222-222222222222","post_id":"11111111-1111-1111-1111-111111111111","author_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","content":"Nice post","created_at":1700000300}}

### GET /api/v1/posts/{post_id}/comments
- Path params: `post_id` (string, uuid)
- Query params: none
- Body params: none
- Example (success):
  - URL: /api/v1/posts/11111111-1111-1111-1111-111111111111/comments
- Success response example:
  {"code":200,"msg":"success","data":[{"comment_id":"22222222-2222-2222-2222-222222222222","post_id":"11111111-1111-1111-1111-111111111111","author_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","content":"Nice post","created_at":1700000300}]}

### DELETE /api/v1/comments/{comment_id}
- Path params: `comment_id` (string, uuid)
- Query params: none
- Body params: `author_id` (string, uuid)
- Example (success):
  - URL: /api/v1/comments/22222222-2222-2222-2222-222222222222
  - Body:
    {"author_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  {"code":200,"msg":"success","data":{"comment_id":"22222222-2222-2222-2222-222222222222","deleted":true}}

### GET /api/v1/posts/{post_id}/comments/summary
- Path params: `post_id` (string, uuid)
- Query params: none
- Body params: none
- Example (success):
  - URL: /api/v1/posts/11111111-1111-1111-1111-111111111111/comments/summary
- Success response example:
  {"code":200,"msg":"success","data":{"post_id":"11111111-1111-1111-1111-111111111111","count":3,"latest_comment_id":"22222222-2222-2222-2222-222222222222"}}

## Interactions

### POST /api/v1/posts/{post_id}/like
- Path params: `post_id` (string, uuid)
- Query params: none
- Body params: `user_id` (string, uuid)
- Example (success):
  - URL: /api/v1/posts/11111111-1111-1111-1111-111111111111/like
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  {"code":200,"msg":"success","data":{"post_id":"11111111-1111-1111-1111-111111111111","user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","liked":true}}

### POST /api/v1/posts/{post_id}/collect
- Path params: `post_id` (string, uuid)
- Query params: none
- Body params: `user_id` (string, uuid)
- Example (success):
  - URL: /api/v1/posts/11111111-1111-1111-1111-111111111111/collect
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  {"code":200,"msg":"success","data":{"post_id":"11111111-1111-1111-1111-111111111111","user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","collected":true}}

### GET /api/v1/user/likes
- Path params: none
- Query params: `user_id` (string, uuid)
- Body params: none
- Example (success):
  - URL: /api/v1/user/likes?user_id=37ed0792-5e07-449a-bf68-2e6252bcad7d
- Success response example:
  {"code":200,"msg":"success","data":[{"post_id":"11111111-1111-1111-1111-111111111111","liked_at":1700000400}]}

## Treehole

### POST /api/v1/treehole
- Path params: none
- Query params: none
- Body params: `author_id` (string, uuid), `content` (string), `is_anonymous` (bool, optional)
- Example (success):
  - URL: /api/v1/treehole
  - Body:
    {"author_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","content":"hello","is_anonymous":false}
- Success response example:
  {"code":200,"msg":"success","data":{"id":"33333333-3333-3333-3333-333333333333","author_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","content":"hello","is_anonymous":false,"created_at":1700000500}}

### GET /api/v1/treehole/stream
- Path params: none
- Query params: `limit` (int, optional), `offset` (int, optional), `include_ai` (bool, optional)
- Body params: none
- Example (success):
  - URL: /api/v1/treehole/stream?limit=20&offset=0&include_ai=false
- Success response example:
  {"code":200,"msg":"success","data":[{"id":"33333333-3333-3333-3333-333333333333","author_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","content":"hello","is_anonymous":false,"created_at":1700000500}]}

### POST /api/v1/treehole/{treehole_id}/ai_reply
- Path params: `treehole_id` (string, uuid)
- Query params: none
- Body params: `content` (string)
- Example (success):
  - URL: /api/v1/treehole/11111111-1111-1111-1111-111111111111/ai_reply
  - Body:
    {"content":"AI reply"}
- Success response example:
  {"code":200,"msg":"success","data":{"reply_id":"44444444-4444-4444-4444-444444444444","treehole_id":"11111111-1111-1111-1111-111111111111","content":"AI reply","created_at":1700000600}}

## Notifications

### POST /api/v1/notifications
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid), `type` (string), `content` (string), `ref_type` (string, optional), `ref_id` (string, uuid, optional)
- Example (success):
  - URL: /api/v1/notifications
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","type":"system","content":"hello"}
- Success response example:
  {"code":200,"msg":"success","data":{"id":"55555555-5555-5555-5555-555555555555","user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","type":"system","content":"hello","is_read":false,"created_at":1700000700}}

### GET /api/v1/notifications
- Path params: none
- Query params: `user_id` (string, uuid), `unread_only` (bool, optional), `limit` (int, optional)
- Body params: none
- Example (success):
  - URL: /api/v1/notifications?user_id=37ed0792-5e07-449a-bf68-2e6252bcad7d&unread_only=false&limit=20
- Success response example:
  {"code":200,"msg":"success","data":[{"id":"55555555-5555-5555-5555-555555555555","user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","type":"system","content":"hello","is_read":false,"created_at":1700000700}]}

### POST /api/v1/notifications/read
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid), `notification_ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/notifications/read
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","notification_ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  {"code":200,"msg":"success","data":{"updated_count":1,"notification_ids":["11111111-1111-1111-1111-111111111111"]}}

### POST /api/v1/notifications/read_all
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid)
- Example (success):
  - URL: /api/v1/notifications/read_all
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  {"code":200,"msg":"success","data":{"updated_count":5}}

## Follows

### POST /api/v1/follows
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid), `follow_id` (string, uuid)
- Example (success):
  - URL: /api/v1/follows
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","follow_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  {"code":200,"msg":"success","data":{"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","follow_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","following":true}}

### DELETE /api/v1/follows
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid), `follow_id` (string, uuid)
- Example (success):
  - URL: /api/v1/follows
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","follow_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  {"code":200,"msg":"success","data":{"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","follow_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","following":false}}

### GET /api/v1/follows
- Path params: none
- Query params: `user_id` (string, uuid)
- Body params: none
- Example (success):
  - URL: /api/v1/follows?user_id=37ed0792-5e07-449a-bf68-2e6252bcad7d
- Success response example:
  {"code":200,"msg":"success","data":[{"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","follow_id":"88888888-8888-8888-8888-888888888888","created_at":1700000800}]}

## Reports

### POST /api/v1/reports
- Path params: none
- Query params: none
- Body params: `reporter_id` (string, uuid, optional), `target_type` (string), `target_id` (string, uuid), `reason` (string)
- Example (success):
  - URL: /api/v1/reports
  - Body:
    {"reporter_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","target_type":"word","target_id":"11111111-1111-1111-1111-111111111111","reason":"spam"}
- Success response example:
  {"code":200,"msg":"success","data":{"report_id":"66666666-6666-6666-6666-666666666666","status":"received"}}

## Sync

### GET /api/v1/sync/changelog
- Path params: none
- Query params: `since` (int, optional), `limit` (int, optional)
- Body params: none
- Example (success):
  - URL: /api/v1/sync/changelog?since=0&limit=100
- Success response example:
  {"code":200,"msg":"success","data":[{"id":"77777777-7777-7777-7777-777777777777","type":"word","op":"update","updated_at":1700000900}]}

### POST /api/v1/sync/words
- Path params: none
- Query params: none
- Body params: `ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/sync/words
  - Body:
    {"ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  {"code":200,"msg":"success","data":[{"word_id":"11111111-1111-1111-1111-111111111111","word_name":"AI intro","category":"AI??","updated_at":1700000900}]}

### POST /api/v1/sync/comments
- Path params: none
- Query params: none
- Body params: `ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/sync/comments
  - Body:
    {"ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  {"code":200,"msg":"success","data":[{"comment_id":"22222222-2222-2222-2222-222222222222","post_id":"11111111-1111-1111-1111-111111111111","content":"Nice post","updated_at":1700000900}]}

### POST /api/v1/sync/treeholes
- Path params: none
- Query params: none
- Body params: `ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/sync/treeholes
  - Body:
    {"ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  {"code":200,"msg":"success","data":[{"id":"33333333-3333-3333-3333-333333333333","content":"hello","updated_at":1700000900}]}

### POST /api/v1/sync/notifications
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid), `ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/sync/notifications
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  {"code":200,"msg":"success","data":[{"id":"55555555-5555-5555-5555-555555555555","type":"system","content":"hello","updated_at":1700000900}]}

### POST /api/v1/sync/likes
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid), `ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/sync/likes
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  {"code":200,"msg":"success","data":[{"post_id":"11111111-1111-1111-1111-111111111111","liked":true,"updated_at":1700000900}]}

### POST /api/v1/sync/bookmarks
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid), `ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/sync/bookmarks
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  {"code":200,"msg":"success","data":[{"post_id":"11111111-1111-1111-1111-111111111111","bookmarked":true,"updated_at":1700000900}]}
