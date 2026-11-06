from pathlib import Path
import random
import re
import html
from difflib import SequenceMatcher
from importlib import import_module

import streamlit as st

try:
    fuzzy_ratio = import_module("rapidfuzz.fuzz").ratio
except Exception:
    def fuzzy_ratio(a, b):
        return int(100 * SequenceMatcher(None, a, b).ratio())

BASE_DIR = Path(__file__).parent
ASSET_DIR = BASE_DIR / "assets"

GAME_LOGOS = {
    "geo": "Grinch-Themed Geopardy Christmas Logo.png",
    "feud": "Frumpy Feud_ Fast Money Holiday Logo.png",
    "song": "Whoville Name That T-Who-n Sign.png",
}
HOME_LOGO = "Grinchmas Games Sign Graphic.png"
SIDEBAR_LOGO = "Grinchmas Games Whoville Logo.png"
LEADERBOARD_LOGO = "Whoville Christmas Leaderboard Sign.png"

def show_asset(filename, width=None):
    path = ASSET_DIR / filename
    if path.exists():
        if width is None:
            st.image(str(path), use_container_width=True)
        else:
            st.image(str(path), width=width)

st.set_page_config(page_title="Grinchmas Games", layout="wide")

# ----------------------------- THEME ---------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Nunito:wght@400;600;700;800;900&display=swap');
:root { --grinch:#79b82a; --lime:#d6ed13; --red:#e51d24; --cream:#fff7e8; --evergreen:#17652d; --gold:#f5c62c; --ink:#171717; }
.stApp { background:radial-gradient(circle at 15% 5%, #f1f8dc 0, #fff8e9 42%, #f8f0df 100%); color:var(--ink); }
[data-testid="stHeader"] { background:rgba(255,248,233,.9); }
h1,h2,h3 { font-family:'DM Serif Display', Georgia, serif !important; color:#a9151d !important; }
p, label, div, span { font-family:'Nunito', sans-serif; }
.hero { background:linear-gradient(110deg,#d8ed19 0%,#fff5df 52%,#f6df9d 100%); border:4px solid #171717; border-radius:22px; padding:18px 22px; box-shadow:5px 5px 0 #e51d24; }
.hero p { font-size:1.12rem; font-weight:900; margin:.35rem 0 0; color:#17652d; text-align:center; }
.ribbon { background:#79b82a; color:#17120f; border:3px solid #171717; border-radius:14px; padding:9px 16px; text-align:center; font-family:'DM Serif Display',Georgia,serif; font-size:1.2rem; margin:12px 0; }
.card { background:#fffaf0; border:2px solid #171717; border-radius:16px; padding:16px; box-shadow:4px 4px 0 #d8ed19; margin-bottom:12px; }
.small-muted { color:#5b5b4e; font-size:.88rem; }
.scoreboard { background:#fffaf0; border:2px solid #171717; border-radius:16px; padding:10px 12px; }
.score-team { font-weight:900; margin:4px 0 2px; }
.score-track { height:13px; display:flex; overflow:hidden; border:1px solid #222; border-radius:20px; background:#eee; }
.score-seg { height:100%; }
.team-pill { display:inline-block; border:2px solid #222; border-radius:999px; padding:6px 11px; margin:3px; background:#fffaf0; font-weight:900; }
.team-active { background:#d8ed19; box-shadow:0 0 0 3px #e51d24; }
.game-tile { border:2px solid #1b1b1b; border-radius:14px; background:#75b52c; color:#111; font-weight:900; text-align:center; padding:15px 4px; }
.question-box { background:#fffaf0; border:4px solid #75b52c; border-radius:20px; padding:22px; font-family:'DM Serif Display',Georgia,serif; font-size:1.45rem; text-align:center; box-shadow:5px 5px 0 #e51d24; }
button[kind="primary"] { background:#e51d24 !important; border:2px solid #171717 !important; color:white !important; font-weight:900 !important; border-radius:12px !important; }
button[kind="secondary"] { border:2px solid #222 !important; border-radius:12px !important; font-weight:800 !important; }
[data-testid="stSidebar"] { background:#eef5d8; border-right:3px solid #e51d24; }
[data-testid="stSidebar"] img { margin:0 auto 10px auto; display:block; }
hr { border-color:#d9c9a8 !important; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------------------- GAME CONTENT --------------------------------
JEOPARDY = {
    "Music": [
        (100, "This Vallejo rapper is famous for his inventive slang and the hit 'Tell Me When to Go'.", "E-40"),
        (200, "Ice Cube was an original member of this influential Los Angeles rap group.", "N.W.A."),
        (300, "This R&B group featuring Sisqó released the 1996 hit 'In My Bed'.", "Dru Hill"),
        (400, "Oakland-born singer Kehlani released this 2017 debut studio album.", "SweetSexySavage"),
        (500, "This Vallejo rap group appeared on the 'Black Panther' soundtrack with 'Paramedic!'.", "SOB x RBE"),
    ],
    "Sitcoms": [
        (100, "Martin Lawrence played radio host Martin Payne in this sitcom.", "Martin"),
        (200, "Damon Wayans played Michael Kyle, the dad at the center of this family sitcom.", "My Wife and Kids"),
        (300, "This sketch-comedy series launched the careers of the Wayans family, Jim Carrey, and Jamie Foxx.", "In Living Color"),
        (400, "Marlon and Shawn Williams played brothers living in Harlem in this sitcom.", "The Wayans Bros."),
        (500, "Queen Latifah played Khadijah James, a magazine publisher, in this sitcom about four Brooklyn friends.", "Living Single"),
    ],
    "Movies": [
        (100, "Ice Cube and Chris Tucker star in this 1995 comedy set over one Friday in South Central Los Angeles.", "Friday"),
        (200, "Eddie Murphy plays Prince Akeem, who travels to Queens, in this 1988 comedy.", "Coming to America"),
        (300, "Eddie Murphy plays multiple members of the Klump family in this comedy franchise installment.", "The Nutty Professor"),
        (400, "This 1990 teen comedy stars Kid 'n Play and centers on a house party that gets out of hand.", "House Party"),
        (500, "This 1998 comedy-drama written and directed by Ice Cube centers on dancers at a Los Angeles club.", "The Players Club"),
    ],
    "Sports": [
        (100, "The Warriors play their home games in this Bay Area city.", "San Francisco"),
        (200, "The 49ers play their home games at Levi's Stadium in this South Bay city.", "Santa Clara"),
        (300, "This Bay Area baseball team won three World Series titles in 2010, 2012, and 2014.", "San Francisco Giants"),
        (400, "This Bay Area football team became famous for the 'Commitment to Excellence' slogan before relocating to Las Vegas.", "Oakland Raiders"),
        (500, "This Warriors guard became the first unanimous NBA MVP after the 2015–16 season.", "Stephen Curry"),
    ],
    "Food & Bay Area Eats": [
        (100, "This San Francisco staple is a crusty, tangy loaf with a chewy interior.", "Sourdough bread"),
        (200, "A Mission-style burrito is famously wrapped in this.", "A large flour tortilla"),
        (300, "This classic cookout side combines elbow pasta and a creamy dressing.", "Macaroni salad"),
        (400, "This soul-food side is made from leafy greens often simmered with smoked meat or seasonings.", "Collard greens"),
        (500, "This beloved dessert layers bananas, vanilla pudding or custard, and wafers.", "Banana pudding"),
    ],
    "Christmas & Who-ville": [
        (100, "The Grinch's loyal dog is named this.", "Max"),
        (200, "Cindy Lou Who lives in this colorful town.", "Who-ville"),
        (300, "The Grinch lives on this mountain above Who-ville.", "Mount Crumpit"),
        (400, "This actor narrates and voices the Grinch in the 1966 animated special.", "Boris Karloff"),
        (500, "The Grinch's heart grows by this many sizes.", "Three"),
    ],
}

# Family Feud-style ranked survey answers. Host-created party points (not a scientific/public survey); points descend by rank.
FEUD_BANK = [
    ("Name something people decorate for Christmas.", [("Christmas tree", 35), ("House", 25), ("Front yard", 18), ("Mantel", 12), ("Staircase", 10)]),
    ("Name a food people leave out for Santa.", [("Cookies", 42), ("Milk", 30), ("Carrots", 14), ("Brownies", 9), ("Candy", 5)]),
    ("Name something you might find on the Grinch's Christmas list.", [("Presents", 30), ("Roast beast", 25), ("Sleigh", 18), ("Christmas tree", 15), ("Max", 12)]),
    ("Name a popular Christmas movie.", [("Home Alone", 34), ("Elf", 26), ("The Grinch", 22), ("A Christmas Story", 12), ("National Lampoon's Christmas Vacation", 6)]),
    ("Name a reason someone might be late to a holiday party.", [("Traffic", 34), ("Getting dressed", 23), ("Cooking", 20), ("Finding parking", 13), ("Forgot the gift", 10)]),
    ("Name something people put in a stocking.", [("Candy", 32), ("Gift cards", 25), ("Socks", 18), ("Small toys", 15), ("Oranges", 10)]),
    ("Name a popular holiday drink.", [("Hot chocolate", 30), ("Eggnog", 27), ("Apple cider", 22), ("Peppermint mocha", 13), ("Mulled wine", 8)]),
    ("Name something you might see in Who-ville.", [("Whos", 32), ("Christmas lights", 24), ("Candy canes", 18), ("Snow", 15), ("Who-houses", 11)]),
    ("Name a Christmas song almost everyone knows.", [("Jingle Bells", 30), ("All I Want for Christmas Is You", 25), ("Last Christmas", 20), ("Silent Night", 15), ("Feliz Navidad", 10)]),
    ("Name something people forget when hosting a party.", [("Ice", 29), ("Napkins", 24), ("Extra chairs", 20), ("Serving utensils", 15), ("Trash bags", 12)]),
    ("Name a place people shop for last-minute gifts.", [("Target", 30), ("Walmart", 25), ("Amazon", 20), ("Mall", 15), ("Gas station", 10)]),
    ("Name an animal associated with Christmas.", [("Reindeer", 45), ("Polar bear", 20), ("Penguin", 15), ("Dove", 12), ("Robin", 8)]),
    ("Name something that can ruin a Christmas morning.", [("Dead batteries", 30), ("Burnt breakfast", 24), ("Missing presents", 20), ("Family argument", 16), ("Power outage", 10)]),
    ("Name a topping for a holiday dessert.", [("Whipped cream", 30), ("Sprinkles", 25), ("Chocolate", 20), ("Candy cane", 15), ("Caramel", 10)]),
    ("Name something the Grinch might steal.", [("Presents", 35), ("Christmas tree", 25), ("Food", 18), ("Decorations", 13), ("Lights", 9)]),
    ("Name a common New Year's resolution.", [("Exercise more", 30), ("Eat healthier", 25), ("Save money", 20), ("Travel", 15), ("Learn something", 10)]),
    ("Name something people do while waiting for Christmas dinner.", [("Snack", 30), ("Watch TV", 24), ("Talk", 20), ("Play games", 16), ("Take photos", 10)]),
    ("Name a classic Christmas decoration.", [("Wreath", 28), ("Garland", 24), ("Ornaments", 22), ("Nativity scene", 14), ("Mistletoe", 12)]),
    ("Name something you would pack for a snowy holiday trip.", [("Coat", 30), ("Boots", 25), ("Gloves", 20), ("Hat", 15), ("Scarf", 10)]),
    ("Name a reason the Grinch might be grumpy.", [("Too much noise", 30), ("Christmas cheer", 25), ("No presents", 20), ("Crowds", 15), ("Bad mood", 10)]),
    ("Name a dish often served at a holiday gathering.", [("Ham", 30), ("Turkey", 25), ("Mashed potatoes", 20), ("Stuffing", 15), ("Mac and cheese", 10)]),
    ("Name something people do after opening presents.", [("Eat breakfast", 28), ("Clean up", 24), ("Play with gifts", 22), ("Call family", 14), ("Take a nap", 12)]),
    ("Name a character from the classic Grinch story.", [("The Grinch", 35), ("Max", 25), ("Cindy Lou Who", 20), ("Mayor of Who-ville", 12), ("The Whos", 8)]),
    ("Name something that makes a house smell like Christmas.", [("Pine tree", 30), ("Cookies", 25), ("Cinnamon", 20), ("Cranberries", 15), ("Peppermint", 10)]),
    ("Name a holiday activity for a group of adults.", [("Gift exchange", 30), ("Trivia", 25), ("Karaoke", 20), ("Board games", 15), ("Cookie decorating", 10)]),
    ("Name something you might find on a holiday buffet.", [("Appetizers", 28), ("Desserts", 25), ("Salad", 18), ("Main dish", 17), ("Dinner rolls", 12)]),
    ("Name a reason someone might visit Who-ville.", [("Christmas", 35), ("See the Whos", 25), ("Meet Cindy Lou", 18), ("Visit the Grinch", 12), ("See the lights", 10)]),
    ("Name something people do when the Christmas lights go up.", [("Take pictures", 28), ("Drive around", 25), ("Decorate", 22), ("Have a party", 15), ("Turn them on", 10)]),
    ("Name a popular flavor of Christmas candy.", [("Peppermint", 35), ("Chocolate", 25), ("Cinnamon", 18), ("Gingerbread", 12), ("Caramel", 10)]),
    ("Name something that could be in Max's dog bowl.", [("Dog food", 45), ("Treats", 25), ("Water", 18), ("Leftovers", 12)]),
    ("Name a Bay Area rapper or hip-hop artist people might put on at a party.", [("E-40", 30), ("Too $hort", 24), ("Mac Dre", 20), ("SOB x RBE", 14), ("Mistah F.A.B.", 12)]),
    ("Name an R&B group or singer people remember from the 1990s or 2000s.", [("TLC", 26), ("Dru Hill", 22), ("Boyz II Men", 20), ("Joe", 17), ("112", 15)]),
    ("Name a song or artist that gets people singing along at a family function.", [("Old-school R&B", 28), ("Hip-hop classics", 26), ("Line-dance songs", 20), ("Motown", 14), ("Current hits", 12)]),
    ("Name something people associate with a Bay Area summer.", [("Hyphy music", 26), ("Lake or beach day", 22), ("Fog", 20), ("BBQ", 18), ("A Giants or A's game", 14)]),
    ("Name a dish you hope to see at a big family holiday gathering.", [("Mac and cheese", 28), ("Fried chicken", 22), ("Collard greens", 18), ("Candied yams", 17), ("Banana pudding", 15)]),
    ("Name a popular way adults settle who is the most competitive at a party.", [("Trivia", 25), ("Spades or dominoes", 24), ("Karaoke", 20), ("Dancing", 17), ("Video games", 14)]),
    ("Name a Bay Area sports team people might root for.", [("49ers", 30), ("Warriors", 28), ("Giants", 20), ("Raiders", 14), ("Athletics", 8)]),
    ("Name a sitcom people in the family might quote from memory.", [("Martin", 30), ("The Fresh Prince of Bel-Air", 24), ("My Wife and Kids", 20), ("The Wayans Bros.", 15), ("Living Single", 11)]),
    ("Name a sketch-comedy show with a cast that could make you laugh without saying a word.", [("In Living Color", 36), ("Saturday Night Live", 25), ("Chappelle's Show", 18), ("MADtv", 12), ("Key & Peele", 9)]),
    ("Name an Eddie Murphy movie people quote at family gatherings.", [("Coming to America", 32), ("The Nutty Professor", 25), ("Norbit", 18), ("Beverly Hills Cop", 15), ("Boomerang", 10)]),
    ("Name a movie from the 1990s that people can watch over and over.", [("Friday", 32), ("Coming to America", 24), ("The Players Club", 18), ("House Party", 15), ("Boyz n the Hood", 11)]),
    ("Name a Bay Area artist you might hear at a family function.", [("E-40", 28), ("Too $hort", 24), ("Mac Dre", 22), ("Kehlani", 15), ("SOB x RBE", 11)]),
    ("Name an R&B singer or group that brings back memories.", [("Dru Hill", 25), ("Joe", 23), ("TLC", 20), ("Boyz II Men", 18), ("112", 14)]),
    ("Name a song or music style that gets a family party moving.", [("Hyphy / Bay Area rap", 26), ("Line dances", 24), ("90s R&B", 21), ("Old-school hip-hop", 17), ("Afrobeats", 12)]),
    ("Name something you might see at a Bay Area cookout.", [("BBQ grill", 26), ("Music playing", 24), ("Cards or dominoes", 20), ("Mac and cheese", 17), ("Cooler full of drinks", 13)]),
    ("Name a Bay Area city or place people rep with pride.", [("Oakland", 27), ("San Francisco", 24), ("Vallejo", 20), ("Richmond", 16), ("San Jose", 13)]),
    ("Name a classic family-function activity besides eating.", [("Dancing", 27), ("Spades", 25), ("Dominoes", 20), ("Talking / catching up", 16), ("Karaoke", 12)]),
    ("Name a 2000s R&B artist you might add to a slow-jam playlist.", [("Joe", 26), ("Usher", 24), ("Ashanti", 20), ("Mario", 17), ("Alicia Keys", 13)]),
    ("Name a current artist younger cousins might put on the aux.", [("Kehlani", 25), ("SZA", 24), ("Kendrick Lamar", 21), ("Drake", 17), ("Doja Cat", 13)]),
]

SONGS = [
    # 2010s: Bay Area rap, contemporary R&B, and big singalong hits.
    {"decade":"2010s", "title":"Gangsta", "artist":"Kehlani", "hint":"An Oakland-born R&B singer contributed this moody track to the Suicide Squad soundtrack."},
    {"decade":"2010s", "title":"Distraction", "artist":"Kehlani", "hint":"A smooth single from Kehlani's 2017 debut studio album."},
    {"decade":"2010s", "title":"Boo'd Up", "artist":"Ella Mai", "hint":"A romantic R&B hit that became a summer singalong in 2018."},
    {"decade":"2010s", "title":"The Way", "artist":"SOB x RBE", "hint":"A track by the Vallejo rap group known for its melodic Bay Area sound."},
    {"decade":"2010s", "title":"HUMBLE.", "artist":"Kendrick Lamar", "hint":"A 2017 chart-topping track whose title is a one-word reminder to stay grounded."},
    {"decade":"2010s", "title":"Hotline Bling", "artist":"Drake", "hint":"A 2015 hit with a memorable video featuring colorful rooms and distinctive dance moves."},
    {"decade":"2010s", "title":"Love on the Brain", "artist":"Rihanna", "hint":"A soulful 2016 ballad from the album Anti."},
    {"decade":"2010s", "title":"Uptown Funk", "artist":"Mark Ronson featuring Bruno Mars", "hint":"A high-energy funk-pop hit that ruled parties and dance floors in 2015."},
    {"decade":"2010s", "title":"No Role Modelz", "artist":"J. Cole", "hint":"A 2014 hip-hop track from the album 2014 Forest Hills Drive."},
    {"decade":"2010s", "title":"Bodak Yellow", "artist":"Cardi B", "hint":"Cardi B's 2017 breakout single made her a chart-topping star."},
    {"decade":"2010s", "title":"All the Way Up", "artist":"Fat Joe and Remy Ma featuring French Montana", "hint":"A 2016 rap anthem whose title describes reaching the highest level."},
    {"decade":"2010s", "title":"Swimming Pools (Drank)", "artist":"Kendrick Lamar", "hint":"A 2012 track that uses a pool-party setting to explore peer pressure and drinking."},
    # 1990s: Bay Area rap, West Coast hip-hop, and classic R&B.
    {"decade":"1990s", "title":"Sprinkle Me", "artist":"E-40", "hint":"A 1995 Bay Area rap hit by the artist known for his inventive slang and unmistakable flow."},
    {"decade":"1990s", "title":"It Was a Good Day", "artist":"Ice Cube", "hint":"A laid-back 1992 West Coast rap classic imagining a day when everything goes right."},
    {"decade":"1990s", "title":"In My Bed", "artist":"Dru Hill", "hint":"A 1996 R&B hit by the Baltimore group known for its harmonies and Sisqó."},
    {"decade":"1990s", "title":"All the Things (Your Man Won't Do)", "artist":"Joe", "hint":"A smooth 1996 R&B slow jam by the singer simply known by his first name."},
    {"decade":"1990s", "title":"No Scrubs", "artist":"TLC", "hint":"A trio's R&B hit about refusing to entertain an unwanted admirer."},
    {"decade":"1990s", "title":"California Love", "artist":"2Pac featuring Dr. Dre", "hint":"A West Coast anthem with a famous video featuring a desert landscape and a futuristic party."},
    {"decade":"1990s", "title":"Poison", "artist":"Bell Biv DeVoe", "hint":"A New Edition offshoot scored this dance-floor hit with a warning in its title."},
    {"decade":"1990s", "title":"Fantasy", "artist":"Mariah Carey", "hint":"A feel-good pop/R&B hit built around a sample from Tom Tom Club."},
    {"decade":"1990s", "title":"The Ghetto", "artist":"Too $hort", "hint":"A Bay Area rap classic from an Oakland pioneer; its title names an often-overlooked neighborhood."},
    {"decade":"1990s", "title":"I Got 5 on It", "artist":"Luniz", "hint":"A 1995 Bay Area rap hit about everybody pitching in."},
    {"decade":"1990s", "title":"Back & Forth", "artist":"Aaliyah", "hint":"A 1994 debut single from the young R&B star, with a dance-floor groove."},
    {"decade":"1990s", "title":"You're Makin' Me High", "artist":"Toni Braxton", "hint":"A sultry 1996 R&B hit by a singer with a rich, low voice."},
    {"decade":"1990s", "title":"If You Love Me", "artist":"Brownstone", "hint":"A harmony-rich 1994 R&B hit from a trio asking for honesty in love."},
    # Early 2000s: radio, club, R&B, hip-hop, and singalong favorites.
    {"decade":"Early 2000s", "title":"Hey Ya!", "artist":"Outkast", "hint":"An energetic, genre-blending party hit with a memorable dance instruction in its video."},
    {"decade":"Early 2000s", "title":"Crazy in Love", "artist":"Beyonce", "hint":"A solo breakout hit featuring a bold brass hook and Jay-Z."},
    {"decade":"Early 2000s", "title":"Dilemma", "artist":"Nelly featuring Kelly Rowland", "hint":"A melodic rap and R&B duet about being caught up in a relationship."},
    {"decade":"Early 2000s", "title":"Let Me Love You", "artist":"Mario", "hint":"A 2004 R&B hit asking someone to let a new person treat them better."},
    {"decade":"Early 2000s", "title":"In Da Club", "artist":"50 Cent", "hint":"A 2003 club anthem whose opening celebrates a birthday."},
    {"decade":"Early 2000s", "title":"Mr. Brightside", "artist":"The Killers", "hint":"A Las Vegas band's debut single that became a long-running singalong favorite."},
    {"decade":"Early 2000s", "title":"Since U Been Gone", "artist":"Kelly Clarkson", "hint":"A powerhouse pop-rock breakup anthem from the first American Idol winner."},
    {"decade":"Early 2000s", "title":"Into You", "artist":"Fabolous featuring Tamia", "hint":"A smooth rap/R&B collaboration built around a dreamy vocal hook."},
    {"decade":"Early 2000s", "title":"Foolish", "artist":"Ashanti", "hint":"A 2002 R&B smash from a singer whose debut album shared her name."},
    {"decade":"Early 2000s", "title":"U Don't Have to Call", "artist":"Usher", "hint":"A breezy 2001 hit from the 8701 album."},
    {"decade":"Early 2000s", "title":"Mesmerize", "artist":"Ja Rule featuring Ashanti", "hint":"A rap and R&B duet with a catchy hook from two Murder Inc. stars."},
    {"decade":"Early 2000s", "title":"Get Low", "artist":"Lil Jon & The East Side Boyz featuring Ying Yang Twins", "hint":"A crunk-era club anthem famous for getting the whole dance floor moving."},
    {"decade":"Early 2000s", "title":"Thizzle Dance", "artist":"Mac Dre", "hint":"A Bay Area hyphy anthem that doubles as a dance instruction."},
    {"decade":"Early 2000s", "title":"Blow the Whistle", "artist":"Too $hort", "hint":"An Oakland rap veteran's 2006 club hit with a title that sounds like a referee's job."},
    # Today's hits: 2010s through current, including Bay Area and contemporary R&B/rap.
    {"decade":"2020s & Today", "title":"Good Days", "artist":"SZA", "hint":"A dreamy R&B single about hoping for brighter days and a clearer mind."},
    {"decade":"2020s & Today", "title":"Not Like Us", "artist":"Kendrick Lamar", "hint":"A 2024 West Coast rap hit that became a major cultural moment."},
    {"decade":"2020s & Today", "title":"Leave the Door Open", "artist":"Silk Sonic", "hint":"A smooth retro-soul duet by Bruno Mars and Anderson .Paak."},
    {"decade":"2020s & Today", "title":"Essence", "artist":"Wizkid featuring Tems", "hint":"An Afrobeats crossover hit with a laid-back, romantic feel."},
    {"decade":"2020s & Today", "title":"Snooze", "artist":"SZA", "hint":"A slow-burn R&B hit from the album SOS."},
    {"decade":"2020s & Today", "title":"First Class", "artist":"Jack Harlow", "hint":"A 2022 rap hit built around a familiar early-2000s pop sample."},
    {"decade":"2020s & Today", "title":"Back to the Streets", "artist":"Saweetie featuring Jhené Aiko", "hint":"A Bay Area rapper teamed up with a smooth R&B singer for this 2020 track."},
    {"decade":"2020s & Today", "title":"The Box", "artist":"Roddy Ricch", "hint":"A Compton rapper's 2020 hit became famous for its unusual vocal sound effect."},
    {"decade":"2020s & Today", "title":"Heartbreak Anniversary", "artist":"Giveon", "hint":"A deep-voiced R&B singer reflects on a date that brings back memories."},
    {"decade":"2020s & Today", "title":"Persuasive", "artist":"Doechii", "hint":"A Florida rapper and singer released this hypnotic 2022 track."},
]

# ----------------------------- STATE ----------------------------------------
def clean_text(value):
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()

def similarity(a, b):
    return fuzzy_ratio(clean_text(a), clean_text(b))

def init_state():
    defaults = {
        "configured": False, "team_count": 4, "team_names": [], "scores": {},
        "geo_used": set(), "geo_turn": 0, "geo_active": None, "geo_done": False,
        "feud_questions": {}, "feud_answers": {}, "feud_round": 0, "feud_team": 0, "feud_progress": {}, "feud_done": False,
        "song_assignments": {}, "song_round": 0, "song_team": 0, "song_done": False, "song_results": {},
        "tie_winners": {}, "tie_started": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

def setup_teams(names):
    st.session_state.team_names = names
    st.session_state.scores = {n: {"geo": 0, "feud": 0, "song": 0} for n in names}
    st.session_state.configured = True
    st.session_state.geo_used = set()
    st.session_state.geo_turn = 0
    st.session_state.geo_active = None
    st.session_state.geo_done = False
    st.session_state.feud_questions = {}
    st.session_state.feud_answers = {}
    st.session_state.feud_round = 0
    st.session_state.feud_team = 0
    st.session_state.feud_progress = {n: [0, 0] for n in names}
    st.session_state.feud_done = False
    st.session_state.song_assignments = {}
    st.session_state.song_round = 0
    st.session_state.song_team = 0
    st.session_state.song_done = False
    st.session_state.song_results = {}
    st.session_state.tie_winners = {}
    st.session_state.tie_started = {}
    # Each team receives its own six-question Fast Money set, used by both speakers/rounds.
    for name in names:
        st.session_state.feud_questions[name] = random.sample(range(len(FEUD_BANK)), 6)
        eras = list(dict.fromkeys(song["decade"] for song in SONGS))
        chosen_eras = random.sample(eras, 3)
        picks = []
        for era in chosen_eras:
            era_indices = [i for i, song in enumerate(SONGS) if song["decade"] == era]
            picks.append(random.choice(era_indices))
        random.shuffle(picks)
        st.session_state.song_assignments[name] = picks
        st.session_state.song_results[name] = [None, None, None]


def reset_one_game(game):
    """Reset one game's progress and scores without affecting the other games."""
    for team in st.session_state.team_names:
        st.session_state.scores[team][game] = 0
    if game == "geo":
        st.session_state.geo_used = set()
        st.session_state.geo_turn = 0
        st.session_state.geo_active = None
        st.session_state.geo_done = False
        st.session_state.tie_winners.pop("geo", None)
        st.session_state.tie_started.pop("geo", None)
    elif game == "feud":
        for key in list(st.session_state.keys()):
            if key.startswith("feud_mc_choice_"):
                del st.session_state[key]
        st.session_state.feud_answers = {}
        st.session_state.feud_round = 0
        st.session_state.feud_team = 0
        st.session_state.feud_progress = {n: [0, 0] for n in st.session_state.team_names}
        st.session_state.feud_done = False
        for name in st.session_state.team_names:
            st.session_state.feud_questions[name] = random.sample(range(len(FEUD_BANK)), 6)
        st.session_state.tie_winners.pop("feud", None)
        st.session_state.tie_started.pop("feud", None)
    elif game == "song":
        st.session_state.song_round = 0
        st.session_state.song_team = 0
        st.session_state.song_done = False
        st.session_state.song_results = {n: [None, None, None] for n in st.session_state.team_names}
        for name in st.session_state.team_names:
            eras = list(dict.fromkeys(song["decade"] for song in SONGS))
            chosen_eras = random.sample(eras, 3)
            picks = [random.choice([i for i, song in enumerate(SONGS) if song["decade"] == era]) for era in chosen_eras]
            random.shuffle(picks)
            st.session_state.song_assignments[name] = picks
        st.session_state.tie_winners.pop("song", None)
        st.session_state.tie_started.pop("song", None)


def total_score(team):
    s = st.session_state.scores[team]
    return s["geo"] + s["feud"] + s["song"]

def current_leaders(game=None):
    names = st.session_state.team_names
    if not names:
        return []
    def score(n):
        return st.session_state.scores[n][game] if game else total_score(n)
    high = max(score(n) for n in names)
    return [n for n in names if score(n) == high]

def show_team_turn(active_idx):
    names = st.session_state.team_names
    cols = st.columns(len(names))
    for i, name in enumerate(names):
        active = i == active_idx
        with cols[i]:
            st.markdown(f"<div class='team-pill {'team-active' if active else ''}' style='text-align:center;width:100%'>{'➤ ' if active else ''}{html.escape(name)}</div>", unsafe_allow_html=True)

def show_scoreboard():
    if not st.session_state.configured:
        return
    names = st.session_state.team_names
    show_asset(LEADERBOARD_LOGO)
    st.markdown("<div class='scoreboard'>", unsafe_allow_html=True)
    max_total = max(1, max(total_score(n) for n in names))
    for name in names:
        s = st.session_state.scores[name]
        total = total_score(name)
        widths = [100 * s[k] / max_total for k in ("geo", "feud", "song")]
        st.markdown(
            f"<div class='score-team'>{html.escape(name)} <span style='float:right'>{total} pts</span></div>"
            f"<div class='score-track'><div class='score-seg' title='Geopardy' style='width:{widths[0]}%;background:#70b52d'></div>"
            f"<div class='score-seg' title='Frumpy Feud' style='width:{widths[1]}%;background:#f2c52b'></div>"
            f"<div class='score-seg' title='Name That T-Who-n' style='width:{widths[2]}%;background:#1688d4'></div></div>",
            unsafe_allow_html=True,
        )
    st.markdown("<div class='small-muted'>Geopardy · Frumpy Feud · Name That T-Who-n</div></div>", unsafe_allow_html=True)

def page_header(title, subtitle, game_color="#75b52c", logo_key=None):
    left, right = st.columns([2.25, 1])
    with left:
        if logo_key and GAME_LOGOS.get(logo_key):
            show_asset(GAME_LOGOS[logo_key])
        st.markdown(f"<div class='ribbon' style='background:{game_color}'>{subtitle}</div>", unsafe_allow_html=True)
    with right:
        show_scoreboard()

def fuzzy_answer_points(answer, answer_bank):
    best = (0, None, 0)
    for accepted, points in answer_bank:
        score = similarity(answer, accepted)
        if score > best[0]:
            best = (score, accepted, points)
    if best[0] >= 80:
        return best[2], best[1], best[0]
    return 0, None, best[0]

def tied_teams_for_game(game):
    vals = {n: st.session_state.scores[n][game] for n in st.session_state.team_names}
    high = max(vals.values())
    return [n for n, v in vals.items() if v == high]

def tie_breaker(game, prompt, hint):
    tied = tied_teams_for_game(game)
    if len(tied) < 2:
        winner = tied[0] if tied else None
        if winner:
            st.success(f"🏆 {winner} wins this game!")
        return
    st.markdown("<div class='ribbon' style='background:#f6b2d0'>🎯 SUDDEN-DEATH TIEBREAKER</div>", unsafe_allow_html=True)
    st.write(f"**Tied teams:** {', '.join(tied)}")
    st.markdown(f"<div class='question-box'>{prompt}</div>", unsafe_allow_html=True)
    st.caption(hint)
    winner = st.selectbox("After the tiebreaker, award the win to:", tied, key=f"tie_{game}")
    if st.button("🏆 Confirm game winner", key=f"tie_confirm_{game}", type="primary"):
        st.session_state.tie_winners[game] = winner
        st.success(f"{winner} wins the tiebreaker!")

# ----------------------------- SIDEBAR -------------------------------------
with st.sidebar:
    show_asset(SIDEBAR_LOGO)
    if st.session_state.configured:
        nav = st.radio("Choose a Game", ["Home", "Geopardy", "Frumpy Feud", "Name That T-Who-n"], key="nav")
    else:
        nav = "Home"

    st.divider()
    st.caption("Individual Game Resets")
    st.caption("Each reset affects only that game.")
    for game_label, game_key in [("Geopardy", "geo"), ("Frumpy Feud", "feud"), ("Name That T-Who-n", "song")]:
        if st.button(
            f"↻  Reset {game_label}",
            key=f"sidebar_reset_{game_key}",
            use_container_width=True,
            disabled=not st.session_state.configured,
            help=f"Reset only {game_label}; other game scores stay unchanged."
        ):
            reset_one_game(game_key)
            st.rerun()
        st.write("")  # extra separation prevents accidental clicks

    if st.session_state.configured:
        st.divider()
        st.write("**Teams**")
        for n in st.session_state.team_names:
            st.write(f"• {n}")
        if st.button("Reset all games", help="Clears scores and reshuffles all game content"):
            current_names = st.session_state.team_names[:]
            setup_teams(current_names)
            st.rerun()
    st.divider()
    st.caption("Host tip: keep this app open on the party laptop. The host controls scoring and advances turns.")

# ----------------------------- HOME ----------------------------------------
if nav == "Home":
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    logo_left, logo_center, logo_right = st.columns([0.6, 2.8, 0.6])
    with logo_center:
        show_asset(HOME_LOGO, width=680)
    st.markdown("<div class='hero'><p>What, where, and WHO do you know?</p></div>", unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("### Games")
        # Each game logo sits ABOVE its rules card for clear, visible branding.
        for logo_key, card_html in [
            ("geo", "<div class='card'>One board • Six categories<br>Bay Area music, classic sitcoms, quotable comedies, sports, food, and Who-ville Christmas trivia. Teams take turns choosing clues; correct answers add the clue value.</div>"),
            ("feud", "<div class='card'>Two rounds of six questions • One spokesperson per team per round<br>Family-function debates, Bay Area culture, music, movies, TV, food, and holiday prompts. Choose from multiple-choice survey answers; point values stay hidden until a choice is selected, then reveal automatically.</div>"),
            ("song", "<div class='card'>Three rounds per team<br>Each team gets three randomly selected eras from the 2010s, 1990s, early 2000s, and 2020s/today. Every music clue is multiple choice with four options. Choose the correct song title to earn a point.</div>"),
        ]:
            logo_left, logo_center, logo_right = st.columns([1, 2, 1])
            with logo_center:
                show_asset(GAME_LOGOS[logo_key], width=300)
            st.markdown(card_html, unsafe_allow_html=True)
    with right:
        st.markdown("### Leaderboard")
        if st.session_state.configured:
            show_scoreboard()
        else:
            st.info("Set up your teams below to activate the leaderboard and games.")
    st.divider()
    st.markdown("### Team Setup")
    default_count = st.session_state.team_count
    count = st.number_input("How many teams are playing?", min_value=2, max_value=12, value=int(default_count), step=1)
    st.session_state.team_count = int(count)
    default_names = st.session_state.team_names if st.session_state.configured and len(st.session_state.team_names) == count else [f"Team {i+1}" for i in range(int(count))]
    with st.form("team_setup"):
        names = []
        cols = st.columns(2)
        for i in range(int(count)):
            with cols[i % 2]:
                names.append(st.text_input(f"Team {i+1} name", value=default_names[i], key=f"team_name_{i}"))
        submitted = st.form_submit_button("Game On!", type="primary", use_container_width=True)
    if submitted:
        cleaned = [n.strip() or f"Team {i+1}" for i, n in enumerate(names)]
        if len({n.lower() for n in cleaned}) != len(cleaned):
            st.error("Please give every team a unique name.")
        else:
            setup_teams(cleaned)
            st.success("Teams are ready! Head to the sidebar and choose your first game.")
            st.rerun()

# ----------------------------- GEOPARDY ------------------------------------
elif nav == "Geopardy":
    if not st.session_state.configured:
        st.warning("Set up teams on the Home page first.")
    else:
        page_header("GEOPARDY", "Choose a category and dollar value. Clear the board to finish the game.", "#79b82a", "geo")
        names = st.session_state.team_names
        if st.session_state.geo_done:
            st.success("The Geopardy board is clear!")
            tie_breaker("geo", "In what year did the classic animated Grinch special first premiere?", "Host-checked answer: 1966. Decide which tied team got it first.")
        else:
            active_idx = st.session_state.geo_turn % len(names)
            st.markdown(f"**It's {names[active_idx]}'s turn!**")
            show_team_turn(active_idx)
            st.write("")
            if st.session_state.geo_active is None:
                header_cols = st.columns(6)
                for j, category in enumerate(JEOPARDY.keys()):
                    with header_cols[j]:
                        st.markdown(f"<div class='game-tile' style='background:#ed8fbd'>{category}</div>", unsafe_allow_html=True)
                for row in range(5):
                    cols = st.columns(6)
                    for j, category in enumerate(JEOPARDY.keys()):
                        value, question, answer = JEOPARDY[category][row]
                        key = f"{category}_{value}"
                        with cols[j]:
                            if key in st.session_state.geo_used:
                                st.button("✓", key=f"used_{key}", disabled=True, use_container_width=True)
                            elif st.button(f"${value}", key=f"tile_{key}", use_container_width=True):
                                st.session_state.geo_active = {"key":key,"category":category,"value":value,"question":question,"answer":answer}
                                st.rerun()
            else:
                q = st.session_state.geo_active
                st.markdown(f"**{q['category']} for ${q['value']}**")
                st.markdown(f"<div class='question-box'>{q['question']}</div>", unsafe_allow_html=True)
                with st.expander("Host answer (keep hidden from players)"):
                    st.write(q["answer"])
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Correct! Add points", type="primary", use_container_width=True):
                        st.session_state.scores[names[active_idx]]["geo"] += q["value"]
                        st.session_state.geo_used.add(q["key"])
                        st.session_state.geo_active = None
                        st.session_state.geo_turn += 1
                        if len(st.session_state.geo_used) == 30:
                            st.session_state.geo_done = True
                        st.rerun()
                with c2:
                    if st.button("❌ Incorrect — no points", use_container_width=True):
                        st.session_state.geo_used.add(q["key"])
                        st.session_state.geo_active = None
                        st.session_state.geo_turn += 1
                        if len(st.session_state.geo_used) == 30:
                            st.session_state.geo_done = True
                        st.rerun()
                if st.button("↩ Back to board (don't use clue)"):
                    st.session_state.geo_active = None
                    st.rerun()
        st.divider()
        st.markdown("**Current Geopardy scores**")
        st.dataframe([{"Team":n,"Geopardy points":st.session_state.scores[n]["geo"]} for n in names], use_container_width=True, hide_index=True)

# ----------------------------- FRUMPY FEUD ---------------------------------
elif nav == "Frumpy Feud":
    if not st.session_state.configured:
        st.warning("Set up teams on the Home page first.")
    else:
        page_header("FRUMPY FEUD: FAST MONEY", "Two spokesperson rounds. Six questions per team. Choose one survey answer; its hidden point value is revealed when selected. Round two cannot reuse that team's Round 1 answer.", "#f5c62c", "feud")
        names = st.session_state.team_names
        if st.session_state.feud_done:
            st.success("Fast Money is complete for every team!")
            tie_breaker("feud", "Name a holiday treat that people often bake at home.", "Host-judged sudden death: first tied team with a valid answer wins.")
        else:
            team_idx = st.session_state.feud_team
            round_idx = st.session_state.feud_round
            team = names[team_idx]
            progress = st.session_state.feud_progress[team][round_idx]
            st.markdown(f"**Round {round_idx+1} of 2 · {team}'s spokesperson is up!**")
            show_team_turn(team_idx)
            if progress >= 6:
                st.success(f"{team} has completed Round {round_idx+1}!")
                if st.button("➡️ Next team", type="primary"):
                    if team_idx < len(names)-1:
                        st.session_state.feud_team += 1
                    else:
                        if round_idx == 0:
                            st.session_state.feud_round = 1
                            st.session_state.feud_team = 0
                        else:
                            st.session_state.feud_done = True
                    st.rerun()
            else:
                qid = st.session_state.feud_questions[team][progress]
                question, answer_bank = FEUD_BANK[qid]
                st.markdown(f"<div class='question-box'>{question}</div>", unsafe_allow_html=True)
                st.caption(f"Question {progress+1} of 6 · Round {round_idx+1}")
                prior = st.session_state.feud_answers.get((team, 0, qid), {}) if round_idx == 1 else {}
                if prior:
                    st.info(f"Round 1 answer already used: **{prior['answer']}**. Choose a different survey answer.")
                available_answers = [(ans, pts) for ans, pts in answer_bank if not (prior and clean_text(ans) == clean_text(prior.get("answer", "")))]
                choice_labels = [ans for ans, _ in available_answers]
                choice_key = f"feud_mc_choice_{team_idx}_{round_idx}_{progress}"
                selected_answer = st.radio("Choose the answer that you think is on the survey board:", choice_labels, index=None, key=choice_key)
                if selected_answer:
                    selected_points = next(pts for ans, pts in available_answers if ans == selected_answer)
                    st.markdown(f"<div class='ribbon' style='background:#d8ed19'>Selected answer: {html.escape(selected_answer)} · <b>{selected_points} points</b></div>", unsafe_allow_html=True)
                if st.button("Lock in answer", type="primary", use_container_width=True, key=f"feud_lock_{team_idx}_{round_idx}_{progress}", disabled=selected_answer is None):
                    points = next(pts for ans, pts in available_answers if ans == selected_answer)
                    st.session_state.scores[team]["feud"] += points
                    st.session_state.feud_answers[(team, round_idx, qid)] = {"answer": selected_answer, "points": points, "matched": selected_answer}
                    st.session_state.feud_progress[team][round_idx] += 1
                    st.success(f"Locked in: **{selected_answer}** · +{points} points")
                    st.rerun()
                with st.expander("Host view: survey board and point values"):
                    for rank, (ans, pts) in enumerate(answer_bank, start=1):
                        st.write(f"{rank}. {ans} — {pts} pts")
        st.divider()
        st.markdown("**Frumpy Feud scores**")
        st.dataframe([{"Team":n,"Frumpy Feud points":st.session_state.scores[n]["feud"]} for n in names], use_container_width=True, hide_index=True)

# ----------------------------- NAME THAT T-WHO-N ----------------------------
elif nav == "Name That T-Who-n":
    if not st.session_state.configured:
        st.warning("Set up teams on the Home page first.")
    else:
        page_header(
            "NAME THAT T-WHO-N",
            "Three rounds per team. Read the music clue and choose the correct song from four options. ",
            "#e51d24",
            "song",
        )
        names = st.session_state.team_names
        if st.session_state.song_done:
            st.success("All teams have completed their three multiple-choice rounds!")
            tie_breaker(
                "song",
                "Bonus question: Which group released the holiday hit 'Last Christmas'?",
                "Multiple-choice tiebreaker: A) Wham!  B) Duran Duran  C) Culture Club  D) Tears for Fears. Correct answer: A) Wham! Award the win to the tied team that answered first.",
            )
        else:
            team_idx = st.session_state.song_team
            round_idx = st.session_state.song_round
            team = names[team_idx]
            song_idx = st.session_state.song_assignments[team][round_idx]
            song = SONGS[song_idx]
            st.markdown(f"**Round {round_idx+1} of 3 · {team}'s turn!**")
            show_team_turn(team_idx)

            # Keep the same four options for this question on every Streamlit rerun.
            decoys = [item["title"] for i, item in enumerate(SONGS) if i != song_idx]
            rng = random.Random(song_idx + 8675309)
            choices = [song["title"]] + rng.sample(decoys, 3)
            rng.shuffle(choices)
            letters = ["A", "B", "C", "D"]
            option_map = {f"{letter}. {choice}": choice for letter, choice in zip(letters, choices)}

            st.markdown(
                f"<div class='question-box'><span style='font-size:1rem;color:#1688d4;font-family:Nunito;font-weight:900'>{html.escape(song['decade'].upper())}</span><br>{html.escape(song['hint'])}<br><br><span style='font-size:1rem'>Which song is being described?</span></div>",
                unsafe_allow_html=True,
            )
            with st.form(f"song_mc_form_{team_idx}_{round_idx}"):
                selected_option = st.radio(
                    "Choose one answer:",
                    list(option_map.keys()),
                    index=None,
                    key=f"song_mc_choice_{team_idx}_{round_idx}",
                )
                submit_song = st.form_submit_button(
                    "Lock in answer",
                    type="primary",
                    use_container_width=True,
                )

            if submit_song:
                if selected_option is None:
                    st.error("Choose an answer before submitting.")
                else:
                    selected_title = option_map[selected_option]
                    correct = selected_title == song["title"]
                    if correct:
                        st.session_state.scores[team]["song"] += 1
                        st.session_state.song_results[team][round_idx] = True
                        st.success(f"Correct! {song['title']} — {song['artist']} (+1 point)")
                    else:
                        st.session_state.song_results[team][round_idx] = False
                        st.warning(f"Not quite! The correct answer was **{song['title']} — {song['artist']}**. No points awarded.")

                    if team_idx < len(names)-1:
                        st.session_state.song_team += 1
                    else:
                        if round_idx < 2:
                            st.session_state.song_round += 1
                            st.session_state.song_team = 0
                        else:
                            st.session_state.song_done = True
                    st.rerun()

        st.divider()
        st.markdown("**Name That T-Who-n scores**")
        st.dataframe(
            [
                {
                    "Team": n,
                    "Correct answers": st.session_state.scores[n]["song"],
                    "Rounds completed": sum(x is not None for x in st.session_state.song_results[n]),
                }
                for n in names
            ],
            use_container_width=True,
            hide_index=True,
        )

# ----------------------------- FOOTER --------------------------------------
st.markdown("<hr><div style='text-align:center;color:#55704a;font-weight:800'>MADE WITH CHRISTMAS CHEER IN WHO-VILLE · Host-controlled party edition</div>", unsafe_allow_html=True)
