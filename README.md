# Whoville Holiday Games

A single-app Streamlit party game hub with a 1966 Grinch-inspired visual theme.

## Included games

- **Geopardy** — one 6-category, 30-clue board; teams rotate turns; host marks correct/incorrect; correct answers earn the clue value.
- **Frumpy Fued: Fast Money** — each team gets its own six-question set, played by two spokespersons over two rounds. The second round cannot repeat the team's exact first-round answer to the same question. Answers are fuzzy-matched against ranked survey answers for points.
- **Name that T-Who-n** — three turns per team; song eras shuffle among the 2010s, 1990s, early 2000s, and 2020s and today. Both title and artist must each reach 80% similarity to earn a point. An optional audio upload lets the host play a clip.

The shared leaderboard displays each team's total and a color-coded score bar: green for Geopardy, yellow for Frumpy Fued, and blue for Name that T-Who-n.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, and the complete `assets/` folder.
3. In Streamlit Community Cloud, choose the repository and set the main file path to `app.py`.
4. Deploy.

## Host workflow

- Start on Home and enter the number of teams and team names.
- Use the sidebar to switch between games.
- The app keeps scores and game progress in Streamlit session state while the app session remains active.
- Use **Reset all games** in the sidebar to clear scores and reshuffle question/song assignments.
- For a tied game, the app displays a sudden-death prompt and lets the host award the win to the team that wins the live tiebreaker.

## Customization notes

- The uploaded Cindy's Crew sign and Whoville menu are stored in `assets/` and used as visual references in the Home page.
- Edit the `JEOPARDY`, `FEUD_BANK`, and `SONGS` lists near the top of `app.py` to customize questions and content.
- The question banks are tailored to a multigenerational Bay Area family party, with a thoughtful mix of Bay Area hip-hop, classic and contemporary R&B, sitcoms such as *Martin*, *My Wife and Kids*, *In Living Color*, and *The Wayans Bros.*, plus comedies such as *Friday*, *Coming to America*, and *The Nutty Professor*. The Frumpy Fued point values are host-created game values, not claims about a published survey. Each team receives songs from three randomly selected eras, with one song per era. The Name that T-Who-n song clues are original descriptive hints rather than reproduced song lyrics. You can optionally upload a short audio clip during a turn if you have the rights to play it.
- The app is designed for one host-controlled device. It does not currently provide separate player logins, cloud database persistence, or synchronized multi-device buzzers.
