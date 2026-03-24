

### 1. The "Theme of the Week" (Classic Leaderboard)
This is your bread-and-butter engagement tool. Every Monday, announce a specific prompt template or theme (e.g., "Cyberpunk 2077," "Studio Ghibli Style," or "Ancient Egypt").

* **The Hook:** Users compete for the "Top Voted" spot.
* **The Engagement:** A dedicated "Challenge Gallery" where users can scroll and heart their favorites.
* **The Prize:** A "Weekly Champion" badge on their profile or bonus tokens for more generations.

### 2. "Who Prompted it Better?" (Side-by-Side Battles)
Instead of a giant gallery, show users two random images side-by-side that were created using the same template.

* **The Hook:** Users click on the one they like better (Tinder-style swiping or "Hot or Not" mechanics). 
* **The Engagement:** This creates an ELO rating system (a competitive score) for the creations, making the leaderboard more scientific and addictive to climb.
* **The Visual:** 

### 3. "Mystery Prompt" Challenge
You provide a blurred or pixelated version of a "Target Image" created by a specific template. Users have to upload their own photo and try to get as close to that aesthetic as possible.

* **The Hook:** A "Similarity Score" (you can actually use Gemini’s multimodal capabilities to compare the user's result with the target).
* **The Engagement:** Users keep trying to tweak their input to get a 99% match.

### 4. Community "Collaborative Canvas"
Create a challenge where the "Most Liked" image of the day becomes the background or the "inspiration" for the next day's prompt.

* **The Hook:** The community builds a visual story together over 7 days.
* **The Engagement:** People check back daily to see how the "story" has evolved based on the previous winner.

---

### Comparison of Challenge Types

| Challenge Type | Difficulty to Build | Viral Potential | Best For... |
| :--- | :--- | :--- | :--- |
| **Weekly Theme** | Low | Medium | Consistent daily traffic |
| **Photo Battles** | Medium | High | "Boredom busting" sessions |
| **Mystery Prompt** | High | Medium | Power users who love the tech |
| **Story Canvas** | Medium | High | Community building & Retention |

---

### Pro-Tip: Use "Smart Sorting"
Don't just show the most liked images at the top of your API feed, or the same person will always win. Use a **"Trending" algorithm** that balances:
$$Score = \frac{Likes}{(Hours\ Since\ Post + 2)^{1.5}}$$
This ensures new, fresh creations have a chance to reach the top.

