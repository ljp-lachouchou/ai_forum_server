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
  ```kotlin
  data class LoginResponse(
      val accessToken: String,
      val email: String,
      val userId: String
  )
  ```

### POST /api/v1/register
- Path params: none
- Query params: none
- Body params: `email` (string), `password` (string)
- Example (success):
  - URL: /api/v1/register
  - Body:
    {"email":"user@example.com","password":"secret123"}
- Success response example:
  ```kotlin
  data class RegisterResponse(
      val userId: String,
      val email: String,
      val accessToken: String?
  )
  ```

## Profile

### GET /api/v1/profile/get_profile
- Path params: none
- Query params: `id` (string, uuid)
- Body params: none
- Example (success):
  - URL: /api/v1/profile/get_profile?id=37ed0792-5e07-449a-bf68-2e6252bcad7d
- Success response example:
  ```kotlin
  data class ProfileResponse(
      val username: String?,
      val avatarUrl: String?,
      val bio: String?,
      val role: String,
      val createdAt: String,
      val profileAccount: String?
  )
  ```

### PUT /api/v1/profile/update_profile
- Path params: none
- Query params: none
- Body params: `id` (string, uuid), `username` (string, optional), `avatar_url` (string, optional), `bio` (string, optional)
- Example (success):
  - URL: /api/v1/profile/update_profile
  - Body:
    {"id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","username":"alice","bio":"hello"}
- Success response example:
  ```kotlin
  data class ProfileResponse(
      val username: String?,
      val avatarUrl: String?,
      val bio: String?,
      val role: String,
      val createdAt: String,
      val profileAccount: String?
  )
  ```

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
  ```kotlin
  data class PersonaUpdateStatsResponse(
      val userId: String,
      val category: String,
      val tags: List<String>,
      val duration: Int,
      val updatedAt: Long
  )
  ```

### POST /api/v1/persona/update_available
- Path params: none
- Query params: none
- Body params: `id` (string, uuid)
- Example (success):
  - URL: /api/v1/persona/update_available
  - Body:
    {"id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  ```kotlin
  data class PersonaUpdateAvailableResponse(
      val id: String,
      val available: Boolean
  )
  ```

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
  ```kotlin
  data class Tag(
      val id: String,
      val displayContent: String,
      val createTime: Long
  )
  
  data class WordCreateResponse(
      val wordId: String,
      val authorId: String,
      val wordUrl: String,
      val category: String,
      val tags: List<Tag>,
      val wordName: String?,
      val status: String,
      val createdAt: Long
  )
  ```

### PUT /api/v1/words/{id}
- Path params: `id` (string, uuid)
- Query params: `author_id` (string, uuid)
- Body params: arbitrary JSON payload (object)
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111?author_id=37ed0792-5e07-449a-bf68-2e6252bcad7d
  - Body:
    {"word_name":"New title"}
- Success response example:
  null

### POST /api/v1/words/{id}/submit
- Path params: `id` (string, uuid)
- Query params: `author_id` (string, uuid)
- Body params: none
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111/submit?author_id=37ed0792-5e07-449a-bf68-2e6252bcad7d
- Success response example:
  null

### POST /api/v1/words/{id}/publish
- Path params: `id` (string, uuid)
- Query params: `admin_id` (string, uuid)
- Body params: none
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111/publish?admin_id=37ed0792-5e07-449a-bf68-2e6252bcad7d
- Success response example:
  null

### POST /api/v1/words/{id}/reject
- Path params: `id` (string, uuid)
- Query params: `admin_id` (string, uuid), `reson` (string)
- Body params: none
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111/reject?admin_id=37ed0792-5e07-449a-bf68-2e6252bcad7d&reson=manual
- Success response example:
  null

### POST /api/v1/words/{id}/archive
- Path params: `id` (string, uuid)
- Query params: none
- Body params: `admin_id` (string, uuid)
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111/archive
  - Body:
    {"admin_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  null

### DELETE /api/v1/words/{id}
- Path params: `id` (string, uuid)
- Query params: none
- Body params: none
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111
- Success response example:
  null

### GET /api/v1/words/{id}
- Path params: `id` (string, uuid)
- Query params: none
- Body params: none
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111
- Success response example:
  ```kotlin
  data class WordDetailResponse(
      val wordId: String,
      val authorId: String,
      val wordUrl: String,
      val category: String,
      val tags: List<Tag>,
      val wordName: String?,
      val status: String,
      val createdAt: Long
  )
  ```

### GET /api/v1/words/{id}/events
- Path params: `id` (string, uuid)
- Query params: none
- Body params: none
- Example (success):
  - URL: /api/v1/words/11111111-1111-1111-1111-111111111111/events
- Success response example:
  ```kotlin
  data class WordEvent(
      val id: String,
      val type: String,
      val actorId: String,
      val createdAt: Long
  )
  
  // data: List<WordEvent>
  ```


### GET /api/v1/words/feeds
- Path params: none
- Query params: `mode` (string: latest|recommend|follow), `category` (string, optional), `user_id` (string, uuid, optional), `limit` (int, optional)
- Body params: none
- Example (success):
  - URL: /api/v1/words/feeds?mode=latest&limit=20
- Success response example:
  ```kotlin
  data class WordFeedItem(
      val wordId: String,
      val wordName: String,
      val category: String,
      val authorId: String,
      val createdAt: Long
  )
  
  // data: List<WordFeedItem>
  ```


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
  ```kotlin
  data class SearchResult(
      val wordId: String,
      val wordName: String,
      val score: Double
  )
  
  data class AISearchResponse(
      val results: List<SearchResult>
  )
  ```


### POST /api/v1/ai/review
- Path params: none
- Query params: `id` (string, uuid)
- Body params: none
- Example (success):
  - URL: /api/v1/ai/review?id=11111111-1111-1111-1111-111111111111
- Success response example:
  null

### POST /api/v1/ai/assist/post
- Path params: none
- Query params: none
- Body params: `content` (string)
- Example (success):
  - URL: /api/v1/ai/assist/post
  - Body:
    {"content":"A short post about IntelliJ and Continue."}
- Success response example:
  ```kotlin
  data class AIAssistPostResponse(
      val content: String,
      val suggestions: List<String>
  )
  ```

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
  ```kotlin
  data class CommentCreateResponse(
      val commentId: String,
      val postId: String,
      val authorId: String,
      val content: String,
      val createdAt: Long
  )
  ```

### GET /api/v1/posts/{post_id}/comments
- Path params: `post_id` (string, uuid)
- Query params: none
- Body params: none
- Example (success):
  - URL: /api/v1/posts/11111111-1111-1111-1111-111111111111/comments
- Success response example:
  ```kotlin
  data class CommentItem(
      val commentId: String,
      val postId: String,
      val authorId: String,
      val content: String,
      val createdAt: Long
  )
  
  // data: List<CommentItem>
  ```


### DELETE /api/v1/comments/{comment_id}
- Path params: `comment_id` (string, uuid)
- Query params: none
- Body params: `author_id` (string, uuid)
- Example (success):
  - URL: /api/v1/comments/22222222-2222-2222-2222-222222222222
  - Body:
    {"author_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  null

### GET /api/v1/posts/{post_id}/comments/summary
- Path params: `post_id` (string, uuid)
- Query params: none
- Body params: none
- Example (success):
  - URL: /api/v1/posts/11111111-1111-1111-1111-111111111111/comments/summary
- Success response example:
  ```kotlin
  data class CommentSummaryResponse(
      val postId: String,
      val count: Int,
      val latestCommentId: String
  )
  ```

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
  ```kotlin
  data class LikeResponse(
      val postId: String,
      val userId: String,
      val liked: Boolean
  )
  ```

### POST /api/v1/posts/{post_id}/collect
- Path params: `post_id` (string, uuid)
- Query params: none
- Body params: `user_id` (string, uuid)
- Example (success):
  - URL: /api/v1/posts/11111111-1111-1111-1111-111111111111/collect
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  ```kotlin
  data class CollectResponse(
      val postId: String,
      val userId: String,
      val collected: Boolean
  )
  ```

### GET /api/v1/user/likes
- Path params: none
- Query params: `user_id` (string, uuid)
- Body params: none
- Example (success):
  - URL: /api/v1/user/likes?user_id=37ed0792-5e07-449a-bf68-2e6252bcad7d
- Success response example:
  ```kotlin
  data class UserLikeItem(
      val postId: String,
      val likedAt: Long
  )
  
  // data: List<UserLikeItem>
  ```


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
  ```kotlin
  data class TreeholeCreateResponse(
      val id: String,
      val authorId: String,
      val content: String,
      val isAnonymous: Boolean,
      val createdAt: Long
  )
  ```

### GET /api/v1/treehole/stream
- Path params: none
- Query params: `limit` (int, optional), `offset` (int, optional), `include_ai` (bool, optional)
- Body params: none
- Example (success):
  - URL: /api/v1/treehole/stream?limit=20&offset=0&include_ai=false
- Success response example:
  ```kotlin
  data class TreeholeItem(
      val id: String,
      val authorId: String,
      val content: String,
      val isAnonymous: Boolean,
      val createdAt: Long
  )
  
  // data: List<TreeholeItem>
  ```


### POST /api/v1/treehole/{treehole_id}/ai_reply
- Path params: `treehole_id` (string, uuid)
- Query params: none
- Body params: `content` (string)
- Example (success):
  - URL: /api/v1/treehole/11111111-1111-1111-1111-111111111111/ai_reply
  - Body:
    {"content":"AI reply"}
- Success response example:
  ```kotlin
  data class TreeholeAiReplyResponse(
      val replyId: String,
      val treeholeId: String,
      val content: String,
      val createdAt: Long
  )
  ```

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
  ```kotlin
  data class NotificationCreateResponse(
      val id: String,
      val userId: String,
      val type: String,
      val content: String,
      val isRead: Boolean,
      val createdAt: Long
  )
  ```

### GET /api/v1/notifications
- Path params: none
- Query params: `user_id` (string, uuid), `unread_only` (bool, optional), `limit` (int, optional)
- Body params: none
- Example (success):
  - URL: /api/v1/notifications?user_id=37ed0792-5e07-449a-bf68-2e6252bcad7d&unread_only=false&limit=20
- Success response example:
  ```kotlin
  data class NotificationItem(
      val id: String,
      val userId: String,
      val type: String,
      val content: String,
      val isRead: Boolean,
      val createdAt: Long
  )
  
  // data: List<NotificationItem>
  ```


### POST /api/v1/notifications/read
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid), `notification_ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/notifications/read
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","notification_ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  ```kotlin
  data class NotificationReadResponse(
      val updatedCount: Int,
      val notificationIds: List<String>
  )
  ```

### POST /api/v1/notifications/read_all
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid)
- Example (success):
  - URL: /api/v1/notifications/read_all
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  ```kotlin
  data class NotificationReadAllResponse(
      val updatedCount: Int
  )
  ```

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
  ```kotlin
  data class FollowCreateResponse(
      val userId: String,
      val followId: String,
      val following: Boolean
  )
  ```

### DELETE /api/v1/follows
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid), `follow_id` (string, uuid)
- Example (success):
  - URL: /api/v1/follows
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","follow_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d"}
- Success response example:
  null

### GET /api/v1/follows
- Path params: none
- Query params: `user_id` (string, uuid)
- Body params: none
- Example (success):
  - URL: /api/v1/follows?user_id=37ed0792-5e07-449a-bf68-2e6252bcad7d
- Success response example:
  ```kotlin
  data class FollowItem(
      val userId: String,
      val followId: String,
      val createdAt: Long
  )
  
  // data: List<FollowItem>
  ```


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
  ```kotlin
  data class ReportCreateResponse(
      val reportId: String,
      val status: String
  )
  ```

## Sync

### GET /api/v1/sync/changelog
- Path params: none
- Query params: `since` (int, optional), `limit` (int, optional)
- Body params: none
- Example (success):
  - URL: /api/v1/sync/changelog?since=0&limit=100
- Success response example:
  ```kotlin
  data class ChangelogItem(
      val id: String,
      val type: String,
      val op: String,
      val updatedAt: Long
  )
  
  // data: List<ChangelogItem>
  ```


### POST /api/v1/sync/words
- Path params: none
- Query params: none
- Body params: `ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/sync/words
  - Body:
    {"ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  ```kotlin
  data class SyncWordItem(
      val wordId: String,
      val wordName: String,
      val category: String,
      val updatedAt: Long
  )
  
  // data: List<SyncWordItem>
  ```


### POST /api/v1/sync/comments
- Path params: none
- Query params: none
- Body params: `ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/sync/comments
  - Body:
    {"ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  ```kotlin
  data class SyncCommentItem(
      val commentId: String,
      val postId: String,
      val content: String,
      val updatedAt: Long
  )
  
  // data: List<SyncCommentItem>
  ```


### POST /api/v1/sync/treeholes
- Path params: none
- Query params: none
- Body params: `ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/sync/treeholes
  - Body:
    {"ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  ```kotlin
  data class SyncTreeholeItem(
      val id: String,
      val content: String,
      val updatedAt: Long
  )
  
  // data: List<SyncTreeholeItem>
  ```


### POST /api/v1/sync/notifications
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid), `ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/sync/notifications
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  ```kotlin
  data class SyncNotificationItem(
      val id: String,
      val type: String,
      val content: String,
      val updatedAt: Long
  )
  
  // data: List<SyncNotificationItem>
  ```


### POST /api/v1/sync/likes
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid), `ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/sync/likes
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  ```kotlin
  data class SyncLikeItem(
      val postId: String,
      val liked: Boolean,
      val updatedAt: Long
  )
  
  // data: List<SyncLikeItem>
  ```


### POST /api/v1/sync/bookmarks
- Path params: none
- Query params: none
- Body params: `user_id` (string, uuid), `ids` (list[string, uuid])
- Example (success):
  - URL: /api/v1/sync/bookmarks
  - Body:
    {"user_id":"37ed0792-5e07-449a-bf68-2e6252bcad7d","ids":["11111111-1111-1111-1111-111111111111"]}
- Success response example:
  ```kotlin
  data class SyncBookmarkItem(
      val postId: String,
      val bookmarked: Boolean,
      val updatedAt: Long
  )
  
  // data: List<SyncBookmarkItem>
  ```

