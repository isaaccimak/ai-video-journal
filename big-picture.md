# Big Picture

1. **Persistence (Database)**
   - Currently, your application is stateless.
   - Missing: A database (e.g., SQLite, PostgreSQL) to store:
     - Journal Entries: Timestamps, transcriptions, and the generated questions.
     - Users: If you plan to support multiple users.
   - Why: Without this, the user's journal entries disappear immediately after the response.

2. **File Storage**
   - Missing: A strategy to permanently store the recorded audio/video files.
   - Why: Currently, you save to a temp_filename and delete it. A journal usually keeps the original recordings. You need a directory structure (e.g., media/YYYY/MM/DD/uuid.mp4) to organize these.

3. **Video Handling**
   - Missing: Explicit support for video files.
   - Why: You mentioned a "Video Journal". While Whisper can handle audio extracted from video, you should ensure your API accepts video MIME types (e.g., video/mp4, video/webm) and your backend handles the audio extraction robustly (using ffmpeg).

4. **Context & Memory**
   - Missing: The ability for the LLM to remember past entries.
   - Why: A good journal agent should ask questions based on trends or past events (e.g., "You mentioned feeling stressed about this project last week, how does it feel now that it's done?").
   - Solution: You need to retrieve past relevant entries (using vector search or simple history) and insert them into the LLM prompt.

5. **Frontend**
   - Missing: The user interface.
   - Why: You explicitly asked to leave space for it, but eventually, you'll need a way for the user to record and upload video.


# Cost saving

1. VAD
   - put VAD in frontend, only audio with speech is sent to backend
   - might have cutoff issues
   - requires users to have decent devices

# User Auth

1. JWT token
   - user_id
   - user_chosen_model (need to double check if this is a good idea, might go against jwt token good practices)
   - user_tier