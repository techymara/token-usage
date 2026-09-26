# nyt-tv-tracker 📺

An interactive checklist for **The New York Times' 100 Best TV Shows of the 21st Century**.

- ✅ "I've seen it" and 👀 "I want to see it" checkboxes for all 100 shows
- Checks are saved in the browser (localStorage) and survive a refresh
- Live counter (`You've seen: X/100`), progress bars and a fun verdict
- **Share on X** button with a pre-filled post: *"I've watched 47 out of 100 of the NYT's best TV shows of the 21st century 📺 [link]"*
- **Share links carry your checks**: the link encodes your list in the URL, so anyone who opens it sees your checkmarks (read-only) and how many you've both seen, then can start their own
- **Copy my list** puts a text version of your list on the clipboard
- Filter (All / Seen / Not seen / Want to see) and search
- Light and dark mode, works on phones

No dependencies: `server.js` is a tiny Node static server and the whole app is `public/index.html`.

## Run locally

```bash
cd nyt-tv-tracker
npm start          # http://localhost:3000
```

## Deploy to Render (free)

1. Push this repo to GitHub (already done if you're reading this there).
2. Go to <https://dashboard.render.com> → **New +** → **Web Service** → connect this repo.
3. Settings:
   - **Root Directory:** `nyt-tv-tracker`
   - **Runtime:** Node
   - **Build Command:** `npm install`
   - **Start Command:** `npm start`
   - **Instance Type:** Free
4. Click **Create Web Service**. You'll get a URL like `https://nyt-tv-tracker.onrender.com`. That's the link people share.

Free Render services sleep when idle, so the first visit after a while can take ~30s to wake.

**Even simpler:** `public/index.html` is fully self-contained, so you can also drop it on any static host
(Render Static Site with publish directory `nyt-tv-tracker/public`, GitHub Pages, Netlify) with no server at all.
