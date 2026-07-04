"""
Marketing content plan for Priceline Pharmacy Pacific Fair.

Edit this file to change the schedule. Each task is a dict; the dashboard
(marketing_app.py) reads TASKS and PLAYBOOK from here.

Plan window: Mon 6 Jul 2026 - Sun 30 Aug 2026 (8 weeks, winter -> spring).
"""
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Channels & colours
# ---------------------------------------------------------------------------
IG = "Instagram"
GBP = "Google Business"
REV = "Reviews"
SEO = "SEO"
PHOTO = "Photos"
SALE = "Sale"

CHANNEL_COLORS = {
    IG: "#E1306C",
    GBP: "#34A853",
    REV: "#FBBC05",
    SEO: "#00B4D8",
    PHOTO: "#9B5DE5",
    SALE: "#FF5252",
}

# Hashtag sets (used inside captions)
TAGS_CORE = "#PricelinePharmacy #PacificFair #Broadbeach #GoldCoast #YourLocalPharmacy"
TAGS_BEAUTY = "#BeautyAustralia #MakeupAddict #SkincareAustralia #BeautyOnABudget #Sisterclub"
TAGS_WELL = "#WinterWellness #HealthAndWellbeing #ColdAndFluSeason #WellnessAustralia"

AI_STYLE = ("Bright, clean Australian retail photography style, soft natural daylight, "
            "white surface with hot-pink (#E6007E) accent props, glossy magazine finish, "
            "high detail, no text, no logos, no people's faces, 4:5 portrait.")


def T(tid, d, channel, ctype, pillar, title, best="", mins=10, content="",
      image_prompt="", video_prompt="", photo_brief="", notes=""):
    return {
        "id": tid, "date": d, "channel": channel, "type": ctype,
        "pillar": pillar, "title": title, "best_time": best, "mins": mins,
        "content": content, "image_prompt": image_prompt,
        "video_prompt": video_prompt, "photo_brief": photo_brief, "notes": notes,
    }


# ---------------------------------------------------------------------------
# Weeks (Monday start dates) + recurring content that varies per week
# ---------------------------------------------------------------------------
WEEKS = [
    {"num": 1, "start": date(2026, 7, 6), "theme": "Winter Wellness Reset",
     "tue_story": ("Poll: winter check-in",
                   "Frame 1 - Poll sticker: \"Winter check-in: how are we holding up?\" "
                   "Options: Thriving [sun emoji] / Surviving [sneeze emoji].\n"
                   "Frame 2 - \"Whatever you voted... our winter wellness bay has your back. "
                   "Come see us at Pacific Fair.\""),
     "fri_story": ("Weekend at Pac Fair - new in",
                   "Frame 1 - Boomerang or photo of a new arrival: \"NEW IN [sparkle emoji]\".\n"
                   "Frame 2 - \"Weekend plans: Pacific Fair. Come say hi - open late.\" "
                   "Add location sticker: Pacific Fair."),
     "gbp_photos": "This week: winter wellness end-cap, storefront from mall walkway, one team candid at the counter.",
     "seo": ("GBP audit - the foundation",
             "Open business.google.com and check, in order:\n"
             "1. Primary category = Pharmacy. Add secondary: Beauty Supply Store, Vitamin & Supplements Store.\n"
             "2. Services list includes: Prescriptions, Flu Vaccinations, Blood Pressure Checks, "
             "Webster-pak / DAA packing, NDSS Access Point, Beauty & Cosmetics.\n"
             "3. Hours correct (incl. upcoming public holidays).\n"
             "4. Attributes: wheelchair accessible, in-store pickup, LGBTQ+ friendly (as applicable).\n"
             "5. Phone + website point to your Priceline store page.\n"
             "Fix anything missing - this is the single highest-leverage local SEO job."),
     "gbp_mon": ("Winter Wellness Week in-store",
                 "It's Winter Wellness Week at Priceline Pharmacy Pacific Fair! Immunity support, "
                 "cold & flu relief and friendly advice from our pharmacist team. Flu vaccinations "
                 "available in-store - walk-ins welcome. Find us in Pacific Fair, Broadbeach.\n\n"
                 "Button: Learn more -> your Priceline store page.")},

    {"num": 2, "start": date(2026, 7, 13), "theme": "Winter Skin SOS",
     "tue_story": ("This-or-that: moisturiser edition",
                   "Frame 1 - Poll: \"Winter skin, pick your fighter:\" Rich cream [cream emoji] vs "
                   "Gel moisturiser [droplet emoji].\n"
                   "Frame 2 - \"Team can't decide either. Both live on our skincare wall - "
                   "come swatch them IRL.\""),
     "fri_story": ("Skin SOS weekend",
                   "Frame 1 - Shelfie of serums: \"Hydration station [droplet emoji]\".\n"
                   "Frame 2 - \"Dry-skin rescue kits sorted. We're here all weekend.\" Location sticker."),
     "gbp_photos": "This week: skincare wall wide shot, close-up of a hero serum display, consult room door (privacy-safe).",
     "seo": ("Seed Google Q&A",
             "On your Google Business Profile, use the Q&A section to ask AND answer 3 real questions "
             "customers have (from your own account is fine and normal):\n"
             "1. \"Do I need a booking for a flu vaccination?\" -> answer with walk-in/booking info.\n"
             "2. \"Do you make Webster-paks / medication packs?\" -> yes + how to start.\n"
             "3. \"Where are you located inside Pacific Fair?\" -> level/nearest entrance + parking tip.\n"
             "Keyword-rich answers here show up in local search."),
     "gbp_mon": ("Winter Skin SOS week",
                 "Dry, tight, flaky winter skin? This week we're all about skin rescue - hydrating "
                 "cleansers, serums and rich moisturisers, with free friendly advice at the beauty "
                 "counter. Sisterclub members earn points on every purchase. Priceline Pharmacy "
                 "Pacific Fair, Broadbeach.\n\nButton: Learn more.")},

    {"num": 3, "start": date(2026, 7, 20), "theme": "Beauty Week",
     "tue_story": ("Quiz: guess the bestseller",
                   "Frame 1 - Quiz sticker: \"Guess our #1 selling mascara this month\" with 3 options "
                   "from your actual top sellers.\n"
                   "Frame 2 - Reveal with a shelfie of the winner: \"The people have spoken [crown emoji]\"."),
     "fri_story": ("Payday weekend",
                   "Frame 1 - \"It's payday weekend and the beauty wall knows it [nail-polish emoji]\".\n"
                   "Frame 2 - Quick pan of new arrivals. \"Open late tonight - treat yourself.\""),
     "gbp_photos": "This week: beauty wall hero shot, new-arrivals end cap, a staff member restocking (candid, from behind/side).",
     "seo": ("Citation / NAP consistency check",
             "Search your pharmacy on each of these and confirm Name, Address, Phone are IDENTICAL "
             "to your Google listing (fix or claim where wrong):\n"
             "1. Apple Maps  2. Bing Places  3. Yellow Pages  4. Localsearch  5. True Local  "
             "6. Priceline store locator page.\n"
             "Inconsistent NAP quietly hurts local rankings. Keep a note of logins as you go."),
     "gbp_mon": ("Beauty Week - new arrivals",
                 "Beauty Week at Priceline Pharmacy Pacific Fair! New arrivals across makeup and "
                 "skincare, plus the classics you love. Ask our beauty team for a shade match while "
                 "you're in. Sisterclub members: points on everything. Pacific Fair, Broadbeach.\n\n"
                 "Button: Learn more.")},

    {"num": 4, "start": date(2026, 7, 27), "theme": "Services Spotlight",
     "tue_story": ("Ask our pharmacist",
                   "Frame 1 - Question sticker: \"Ask us anything - winter wellness edition. "
                   "(General advice only - we'll keep it broad!)\"\n"
                   "Frame 2+ - Answer 2-3 of the best questions tomorrow as text frames.\n"
                   "COMPLIANCE: keep answers general wellbeing only - no specific medicines, "
                   "no diagnosis. \"Come in and chat to us\" is the CTA."),
     "fri_story": ("Weekend hours + tease",
                   "Frame 1 - \"Weekend, sorted: scripts in, flu shot done, beauty browse earned.\"\n"
                   "Frame 2 - Weekend trading hours graphic. Location sticker."),
     "gbp_photos": "This week: dispensary counter (NO scripts/patient info visible), blood pressure machine, Webster-pak display (empty/demo pack only).",
     "seo": ("GBP services deep-dive",
             "In Google Business Profile > Services: give every service a 2-3 sentence description "
             "using natural keywords, e.g. \"Flu vaccinations at Pacific Fair - walk in or book; "
             "administered in our private consult room by trained pharmacists.\" Do the same for "
             "Webster-paks, blood pressure checks, NDSS. Then check your store's page on "
             "priceline.com.au lists the same services."),
     "gbp_mon": ("More than prescriptions",
                 "Did you know? At Priceline Pharmacy Pacific Fair we offer flu vaccinations "
                 "(walk-ins welcome), free blood pressure checks, Webster-pak medication packing and "
                 "friendly advice - alongside your scripts. Drop in and ask the team. Pacific Fair, "
                 "Broadbeach.\n\nButton: Learn more.")},

    {"num": 5, "start": date(2026, 8, 3), "theme": "Vitamins & Energy",
     "tue_story": ("Poll: 3pm slump",
                   "Frame 1 - Poll: \"The 3pm winter slump hits. You reach for:\" Coffee [coffee emoji] "
                   "/ Power nap [sleep emoji].\n"
                   "Frame 2 - \"Either way - sleep, movement and a balanced diet do the heavy lifting. "
                   "Our vitamin aisle can back the basics up. Come chat.\""),
     "fri_story": ("Sunday self-care prep",
                   "Frame 1 - Flat-lay boomerang: bath salts, sheet mask, candle. \"Sunday reset "
                   "loading...\"\n"
                   "Frame 2 - \"Everything for your self-care Sunday is in store now.\""),
     "gbp_photos": "This week: vitamin aisle wide shot, self-care/bath display, Sisterclub signage.",
     "seo": ("Read your GBP insights",
             "Google Business Profile > Performance: note down (1) how many calls, direction requests "
             "and website clicks last month, (2) the top search queries people used to find you. "
             "Add the top 2 queries naturally into next week's GBP post wording. Save the numbers - "
             "we compare month-on-month in the Week 8 review."),
     "gbp_mon": ("Winter energy basics",
                 "Fighting the winter slump? Sleep, movement and good food come first - and our "
                 "vitamin and supplement range can support your daily routine. Ask our team for help "
                 "choosing. Priceline Pharmacy Pacific Fair, Broadbeach.\n\nButton: Learn more.\n\n"
                 "COMPLIANCE: keep wording to 'support general wellbeing' - no therapeutic claims.")},

    {"num": 6, "start": date(2026, 8, 10), "theme": "Skincare Science",
     "tue_story": ("True or false: SPF",
                   "Frame 1 - Poll styled as True/False: \"You can skip SPF in winter.\"\n"
                   "Frame 2 - \"FALSE. Queensland UV doesn't take winter off. Daily SPF, "
                   "365 days a year. Your future skin says thanks.\""),
     "fri_story": ("Ingredient of the week: ceramides",
                   "Frame 1 - Text frame: \"Ingredient of the week: CERAMIDES - the mortar between "
                   "your skin-barrier bricks.\"\n"
                   "Frame 2 - Shelfie of 2-3 ceramide products: \"Find them on our skincare wall.\""),
     "gbp_photos": "This week: SPF display, skincare science shelf close-ups, storefront at golden hour.",
     "seo": ("Competitor scan",
             "Open the Google Business Profiles of 2 nearby competitor pharmacies. Note: their review "
             "count + rating vs yours, how often they post, what photos they lead with, services "
             "listed that you haven't. Write down 2 gaps to close and add them as tasks (or tell "
             "Claude to schedule them)."),
     "gbp_mon": ("Skincare that makes sense",
                 "Hyaluronic acid? Niacinamide? Ceramides? This week we're decoding skincare "
                 "ingredients - and our beauty team is ready to build you a simple routine that "
                 "works. Priceline Pharmacy Pacific Fair, Broadbeach.\n\nButton: Learn more.")},

    {"num": 7, "start": date(2026, 8, 17), "theme": "Community & Team",
     "tue_story": ("Team favourites",
                   "Frame 1 - \"TEAM FAVES THIS WEEK [star emoji]\" cover.\n"
                   "Frames 2-4 - One product each from 3 team members: photo of them holding it "
                   "(or just the product) + one-line why-they-love-it."),
     "fri_story": ("Weekend - come say hi",
                   "Frame 1 - Team wave at the counter (boomerang). \"WEEKEND! Come say hi [wave emoji]\"\n"
                   "Frame 2 - \"Scripts, beauty, advice - we're here all weekend.\" Location sticker."),
     "gbp_photos": "This week: team group photo (with consent), individual staff at their stations, Pacific Fair entrance nearest you.",
     "seo": ("Launch the review drive",
             "1. Get your Google review link: GBP > 'Ask for reviews' - copy the short URL.\n"
             "2. Make a small QR-code card for the counter (Canva, 10 min): \"Loved your visit? "
             "Tell Google - it takes 30 seconds.\"\n"
             "3. Brief the team: after a great interaction, hand the card over. Target: 3-5 new "
             "reviews/month. NEVER incentivise reviews (against Google policy) - just ask."),
     "gbp_mon": ("Meet the team behind the counter",
                 "The best part of Priceline Pharmacy Pacific Fair? The 25+ locals who run it. "
                 "Pharmacists, beauty advisors and retail legends - here to help every day of the "
                 "week. Come say hi. Pacific Fair, Broadbeach.\n\nButton: Learn more.")},

    {"num": 8, "start": date(2026, 8, 24), "theme": "Spring Prep",
     "tue_story": ("Countdown to spring",
                   "Frame 1 - Countdown sticker to Sep 1: \"SPRING LOADING [flower emoji]\"\n"
                   "Frame 2 - \"New season, new skin routine. Spring arrivals landing now.\""),
     "fri_story": ("Spring displays are in",
                   "Frame 1 - Pan of spring display: \"IT'S HAPPENING [cherry-blossom emoji]\"\n"
                   "Frame 2 - \"First look at spring beauty - in store now.\""),
     "gbp_photos": "This week: spring displays, fresh storefront shot, new-season end caps.",
     "seo": ("Month-in-review ritual",
             "30 minutes, coffee in hand:\n"
             "1. IG Insights: top 3 posts by reach + saves. What do they have in common?\n"
             "2. GBP Performance: calls/directions/clicks vs the Week 5 numbers.\n"
             "3. Review count: on track for 3-5 new this month?\n"
             "4. Write next month's 4 weekly themes (September = Festival of Beauty season - "
             "plan for it!). Ask Claude to generate the next 4-week block from these notes."),
     "gbp_mon": ("Spring arrivals are landing",
                 "Spring is almost here and new-season beauty is already landing at Priceline "
                 "Pharmacy Pacific Fair. Fresh skincare, new makeup and everything for the season "
                 "switch-over. Sisterclub members earn points on it all. Pacific Fair, Broadbeach.\n\n"
                 "Button: Learn more.")},
]

# ---------------------------------------------------------------------------
# Explicit content tasks (feed posts, reels, catalogue uploads, photo shoots)
# ---------------------------------------------------------------------------
CONTENT_TASKS = [

    # ============================ WEEK 1 ============================
    T("w1-mon-post", date(2026, 7, 6), IG, "Feed Post", "Winter Wellness",
      "Winter wellness reset - cold & flu shelf essentials", best="7:00 PM", mins=20,
      content=("Feeling winter creeping in, Gold Coast? \U0001F927 Consider this your sign to restock "
               "the winter shelf BEFORE the sniffles hit the house.\n\n"
               "Tissues, throat soothers, vitamin C, a decent thermometer - and a pharmacist team "
               "who'll point you to what actually suits you. That's the Winter Wellness Reset, "
               "aisle one, Pacific Fair. \U0001F3E5✨\n\n"
               "Flu vaccinations are available in-store too - walk-ins welcome.\n\n"
               f"{TAGS_CORE} {TAGS_WELL}"),
      image_prompt=("Top-down flat lay of a 'winter comfort kit': tissue box, jar of honey, fresh "
                    "lemon halves, digital thermometer, generic white vitamin bottle, cosy knitted "
                    f"scarf corner. {AI_STYLE}"),
      photo_brief=("Better than AI here: style your actual cold & flu end-cap. 3 shots - straight-on "
                   "wide, 45-degree angle, one close-up of the bestseller. Portrait orientation, "
                   "clean the shelf edges first, shoot before opening for no crowds."),
      notes="Cross-post to Facebook. Pin this to your grid for the week."),

    T("w1-wed-reel", date(2026, 7, 8), IG, "Reel", "Winter Wellness",
      "Reel: 5 winter rescue buys under $20", best="7:30 PM", mins=30,
      content=("On-screen text hook (first 1.5s): \"5 winter rescue buys under $20 \U0001F976\"\n\n"
               "Caption: Winter maintenance, sorted for under a twenty. \U0001F9E4 Which one's "
               "already in your basket? Save this for your next Pac Fair run.\n\n"
               f"{TAGS_CORE} {TAGS_WELL}"),
      video_prompt=("AI option (Higgsfield/Runway): fast-paced macro retail montage, 5 quick cuts, "
                    "a hand picking a product from a bright pharmacy shelf, hot-pink price tag "
                    "overlays, soft daylight, energetic but clean, vertical 9:16, 15 seconds."),
      photo_brief=("Phone-shot version (better engagement): 5 clips x 2s - hand grabs each product "
                   "off the shelf, snap zoom on each. Final clip: team member smiling at counter "
                   "holding the basket. Add price text overlays in the IG editor + trending audio "
                   "(check what's rising in Reels > Audio today)."),
      notes="Reels get ~2-3x the reach of feed posts right now. Post between 7 and 8 PM."),

    T("w1-thu-post", date(2026, 7, 9), IG, "Feed Post", "Winter Wellness",
      "Staff pick: the pharmacist's winter non-negotiable", best="7:00 PM", mins=15,
      content=("STAFF PICK \U0001F3C6 We asked our pharmacist the one thing they personally never "
               "run out of in winter - and the answer was instant.\n\n"
               "[Product] - \"[one-line quote from the team member: why they rate it]\"\n\n"
               "Come ask us for our picks in person. We have opinions. \U0001F60F\n\n"
               f"{TAGS_CORE} {TAGS_WELL}"),
      photo_brief=("Team member in uniform at the counter holding the product at chest height, "
                   "genuine smile, shot from waist up. IMPORTANT: no prescriptions, scripts or "
                   "patient info anywhere in frame. Portrait, natural light from the mall if possible."),
      notes="COMPLIANCE: pick a front-shop product (not a Pharmacist Only/S3 medicine). "
            "General wellbeing wording only."),

    T("w1-thu-sale", date(2026, 7, 9), SALE, "Sale Upload", "Catalogue",
      "Catalogue launch - upload sale content everywhere", best="9:00 AM", mins=25,
      content=("New Priceline catalogue drops today. Three quick uploads:\n\n"
               "1) IG STORY SET (3 frames):\n"
               "   - Frame 1: \"NEW CATALOGUE IS LIVE \U0001F6A8\" over a hero deal photo\n"
               "   - Frames 2-3: one hero deal each, price sticker style, \"in store now\"\n"
               "2) GBP OFFER POST: \"Catalogue sale now on at Priceline Pacific Fair - [hero deal] "
               "and more, ends [end date].\" Set post type = Offer with the end date.\n"
               "3) FACEBOOK POST: 2-3 hero deals, link to catalogue, tag Pacific Fair.\n\n"
               "Grab the hero deals from the priceline.com.au homepage carousel / catalogue on your "
               "machine and drop the top 3 into the templates above."),
      notes="The Priceline site blocks cloud access, so pull the carousel deals from your own "
            "browser. Adjust the date if the catalogue cycle differs - they usually run "
            "fortnightly from Thursday."),

    T("w1-sat-post", date(2026, 7, 11), IG, "Feed Post", "Beauty",
      "Winter glow - hydrating beauty picks", best="9:00 AM", mins=15,
      content=("Winter glow is a scam, they said. ❄️ Not with the right base, we said.\n\n"
               "Hydrating primers, dewy foundations and a lip that doesn't crack by lunch - the "
               "beauty wall is fully stocked for glow season (yes, even in July).\n\n"
               "In store now at Pacific Fair. Your skin will feel the difference. ✨\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      image_prompt=("Dewy-finish makeup products arranged on a mirrored tray - foundation bottle, "
                    f"lip balm, primer tube - with water droplets on the mirror. {AI_STYLE}"),
      photo_brief="Or: shelfie of the hydrating-base section of your beauty wall, straight-on, portrait.",
      notes="Saturday 9 AM catches weekend Pac Fair shoppers planning their trip."),

    # ============================ WEEK 2 ============================
    T("w2-mon-post", date(2026, 7, 13), IG, "Feed Post", "Skincare",
      "Dry winter skin? The 3-step rescue routine", best="7:00 PM", mins=20,
      content=("Tight, flaky, angry winter skin - let's fix the routine, not just the symptoms. "
               "\U0001F9F4\n\n"
               "THE 3-STEP WINTER RESCUE:\n"
               "1️⃣ Swap foaming cleanser for a cream/oil cleanser\n"
               "2️⃣ Layer a hyaluronic serum on DAMP skin\n"
               "3️⃣ Seal with a richer moisturiser than your summer one\n"
               "(And SPF every morning. This is Queensland. ☀️)\n\n"
               "Our beauty team will build the routine with you - just ask.\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      image_prompt=("Three skincare products in a neat row on white marble - cream cleanser tube, "
                    "serum dropper bottle, rich moisturiser jar - numbered shadows 1 2 3 cast "
                    f"softly behind them. {AI_STYLE}"),
      photo_brief="Or: 3 products from your shelf lined up on the beauty counter, phone portrait mode.",
      notes="Carousel option: 1 cover + 1 slide per step performs well for saves."),

    T("w2-wed-reel", date(2026, 7, 15), IG, "Reel", "Skincare",
      "Reel: 30-second winter AM routine", best="7:30 PM", mins=30,
      content=("On-screen hook: \"Your winter morning routine in 30 seconds ⏱️\"\n\n"
               "Caption: No 12 steps. No fuss. Cleanse → hydrate → protect, and out the "
               "door. Every product is on our shelves at Pacific Fair right now. Save for your "
               "next restock. \U0001F9F4✨\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      video_prompt=("AI option: elegant vertical macro video - cream cleanser swirl, serum drop "
                    "falling in slow motion, moisturiser texture swipe, SPF bottle turn - bright "
                    "bathroom light, white and pink palette, 9:16, 20 seconds, no faces."),
      photo_brief=("Phone version: film on the back of a hand - cleanser lather (3s), serum drops "
                   "(3s), moisturiser smooth (3s), SPF dot dab (3s). Speed ramp in the editor, "
                   "text label per step."),
      notes=""),

    T("w2-thu-post", date(2026, 7, 16), IG, "Feed Post", "Skincare",
      "Product spotlight: the hydration duo", best="7:00 PM", mins=15,
      content=("The duo doing overtime this winter: a hyaluronic serum + a lip rescue balm. "
               "\U0001F4A7\U0001F48B\n\n"
               "One holds the moisture in your skin, the other saves your lips from the "
               "wind-tunnel that is a Gold Coast winter walk. Small basket, big difference.\n\n"
               "Both in store now - ask the beauty counter to point you to their favourites.\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      image_prompt=("Serum bottle and lip balm side by side on a white shelf edge, soft-focus "
                    f"pharmacy shelving bokeh behind, droplet details. {AI_STYLE}"),
      photo_brief="Or: the two products held in one hand in front of the beauty wall (blurred background).",
      notes=""),

    T("w2-sat-post", date(2026, 7, 18), IG, "Carousel", "Beauty",
      "Carousel: hydration heroes under $30", best="9:00 AM", mins=20,
      content=("HYDRATION HEROES, ALL UNDER $30 \U0001F4A7 - swipe through this week's "
               "team-approved line-up.\n\n"
               "Slide order: cover graphic → 4-5 products (one per slide, name + price + "
               "one-line why) → final slide \"All in store at Pacific Fair - Sisterclub "
               "points on everything\".\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      image_prompt=("Cover slide: single water droplet mid-splash over pastel pink background, "
                    "space for bold text above. Product slides: each product centred on white "
                    f"with soft shadow. {AI_STYLE}"),
      photo_brief="Real product shots beat AI for the product slides - white counter, window light, one per slide.",
      notes="Carousels are the best format for saves/shares - take the extra 10 minutes."),

    # ============================ WEEK 3 ============================
    T("w3-mon-post", date(2026, 7, 20), IG, "Carousel", "Beauty",
      "Beauty wall tour - what's hot right now", best="7:00 PM", mins=20,
      content=("Consider this your virtual lap of the beauty wall. \U0001F485✨ Swipe for "
               "what's flying off shelves at Pacific Fair this month.\n\n"
               "Slides: 1) \"BEAUTY WALL TOUR\" cover over wide wall shot → 2-5) a hot zone "
               "each (new arrivals / bestseller / staff fave / hidden gem) → 6) \"Come do "
               "the real lap - we'll shade match you while you're here.\"\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      photo_brief=("This one should be all real photos: wide of the wall, then 4 tight shots of "
                   "specific sections. Shoot in the morning before crowds, portrait, tidy shelves first."),
      notes=""),

    T("w3-wed-reel", date(2026, 7, 22), IG, "Reel", "Beauty",
      "Reel: 5-minute face with the team", best="7:30 PM", mins=35,
      content=("On-screen hook: \"The 5-minute face our beauty advisor actually wears ⏱️\"\n\n"
               "Caption: Real routine, real speed, products all from our own shelves. Which step "
               "are you stealing? Full list in store - ask [name] for a match. \U0001F485\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      video_prompt=("AI option (if no volunteer): vertical stop-motion of 5 makeup products "
                    "arranging themselves into a routine order on a pink vanity, playful, bright, "
                    "9:16, 15s, no faces."),
      photo_brief=("Much better real: a willing team member does their quick routine to camera - "
                   "5 clips x 3-4s, front camera is fine, ring light if you have one. Authentic "
                   "beats polished. Get their consent for posting (keep a note of it)."),
      notes=""),

    T("w3-thu-post", date(2026, 7, 23), IG, "Feed Post", "Beauty",
      "Staff pick: beauty edition", best="7:00 PM", mins=15,
      content=("STAFF PICK \U0001F3C6 Beauty edition. We asked [name] from our beauty counter "
               "the product they'd buy again with their own money, no hesitation.\n\n"
               "[Product] - \"[their one-liner]\"\n\n"
               "The team's picks rarely miss. Come argue with them about it in person. \U0001F60F\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      photo_brief="Team member holding the product in front of the beauty wall, waist-up, genuine smile, portrait.",
      notes=""),

    T("w3-thu-sale", date(2026, 7, 23), SALE, "Sale Upload", "Catalogue",
      "Catalogue launch - upload sale content everywhere", best="9:00 AM", mins=25,
      content=("Same drill as last cycle:\n"
               "1) IG story set (3 frames) with hero deals\n"
               "2) GBP Offer post with end date\n"
               "3) Facebook post with 2-3 hero deals\n\n"
               "Pull the hero deals from the priceline.com.au carousel/catalogue on your machine."),
      notes="Adjust date to the real catalogue cycle if needed."),

    T("w3-sat-post", date(2026, 7, 25), IG, "Feed Post", "Loyalty",
      "Sisterclub perks - are you actually using them?", best="9:00 AM", mins=15,
      content=("PSA: if you're shopping here without scanning your Sisterclub card, you're leaving "
               "points on the table. \U0001F4B8\n\n"
               "Points on every shop • member-only pricing • birthday treats • "
               "exclusive early access. It's free to join and takes 2 minutes at the counter.\n\n"
               "Ask us next time you're in - we'll set you up on the spot. \U0001F4AF\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      image_prompt=("A hot-pink loyalty card popping out of a small paper shopping bag, confetti "
                    f"pieces mid-air, clean white background. {AI_STYLE}"),
      photo_brief="Or: Sisterclub signage/card at your counter, tight shot.",
      notes=""),

    # ============================ WEEK 4 ============================
    T("w4-mon-post", date(2026, 7, 27), IG, "Carousel", "Services",
      "5 things your pharmacy does (that you didn't know)", best="7:00 PM", mins=20,
      content=("We're not just scripts and shampoo. \U0001F3E5 Swipe for 5 things you can walk in "
               "and get at Priceline Pharmacy Pacific Fair:\n\n"
               "1️⃣ Flu vaccinations - walk-ins welcome\n"
               "2️⃣ Free blood pressure checks\n"
               "3️⃣ Webster-paks - your meds sorted by day and time\n"
               "4️⃣ NDSS access point for diabetes supplies\n"
               "5️⃣ Free advice from pharmacists who know you\n\n"
               "Save this for the family group chat. \U0001F4CC\n\n"
               f"{TAGS_CORE} {TAGS_WELL}"),
      image_prompt=("Cover: friendly modern pharmacy counter scene, soft focus, warm light, "
                    f"hot-pink number '5' as a prop. Slides: one simple icon-style scene per service. {AI_STYLE}"),
      photo_brief="Real versions: consult room door, BP machine, demo Webster-pak (empty), NDSS sign, team at counter.",
      notes="COMPLIANCE: services are fine to promote. No medicine brands/prices in any slide."),

    T("w4-wed-reel", date(2026, 7, 29), IG, "Reel", "Services",
      "Reel: how a Webster-pak comes together", best="7:30 PM", mins=30,
      content=("On-screen hook: \"Ever wondered how a Webster-pak is made? \U0001F48A\"\n\n"
               "Caption: For anyone juggling multiple medications (or helping a parent who is) - "
               "this little pack is a game changer. Sorted by day and dose, checked by your "
               "pharmacist, ready weekly. Ask us how to get started.\n\n"
               f"{TAGS_CORE} {TAGS_WELL}"),
      video_prompt=("AI option: overhead time-lapse style animation of an empty weekly pill "
                    "organiser being filled cell by cell with colourful generic tablets, clean "
                    "clinical white bench, 9:16, 15s. Generic tablets only, no branding."),
      photo_brief=("Real version: overhead phone clip of a DEMO pack being filled with vitamins/"
                   "placebo - NEVER film real patient medication or labels. Hands only, "
                   "clean bench, time-lapse mode."),
      notes="PRIVACY: no patient names, scripts, or real medication labels in frame. Demo pack only."),

    T("w4-thu-post", date(2026, 7, 30), IG, "Feed Post", "Services",
      "Flu season peak - vaccinations available", best="7:00 PM", mins=15,
      content=("Winter's peak is here, Gold Coast. \U0001F927 If the flu shot has been on your "
               "to-do list since May - this is the nudge.\n\n"
               "Flu vaccinations are available in-store at Priceline Pharmacy Pacific Fair. "
               "Walk-ins welcome, private consult room, done in minutes by our trained pharmacist "
               "team. Get it done on your next shop. ✅\n\n"
               f"{TAGS_CORE} {TAGS_WELL}"),
      image_prompt=("A neat cotton ball and small beige plaster on a clean white tray next to a "
                    f"hot-pink 'done' tick prop, calm clinical-but-friendly feel. {AI_STYLE}"),
      photo_brief="Or: consult room door with 'Vaccinations available' signage, or team member with a thumbs up outside it.",
      notes="COMPLIANCE: promote the SERVICE (availability, walk-ins). No vaccine brand names."),

    T("w4-fri-shoot", date(2026, 7, 31), PHOTO, "Photo Shoot", "Content Bank",
      "Monthly photo shoot - 45 minutes, shot list ready", best="8:15 AM", mins=45,
      content=("Before opening, knock out the month's content bank. Shot list:\n\n"
               "1. Storefront from mall walkway (landscape + portrait)\n"
               "2. Beauty wall - wide, then 3 section close-ups\n"
               "3. Skincare bay + vitamin aisle wides\n"
               "4. Counter/team: 2 candids per rostered team member (consent first)\n"
               "5. Consult room (door open, empty, tidy)\n"
               "6. 10 product close-ups: current bestsellers, on white counter near window light\n"
               "7. Seasonal end-caps and any new displays\n\n"
               "Phone is fine. Portrait for most, a few landscape. Dump into a 'Content Bank - Aug' "
               "album. This feeds every post for the next month."),
      notes="No scripts/patient info in any frame. Get quick verbal consent from staff and note it."),

    T("w4-sat-post", date(2026, 8, 1), IG, "Feed Post", "Team",
      "Meet the team: [team member #1]", best="9:00 AM", mins=15,
      content=("MEET THE TEAM \U0001F44B Say hi to [name] - [role] at Priceline Pharmacy "
               "Pacific Fair.\n\n"
               "• Been with us: [x years]\n"
               "• Ask them about: [their specialty - skincare? vitamins? scripts?]\n"
               "• Off-duty: [one fun fact]\n\n"
               "Faces > logos. Come say hi at Pacific Fair - they're the friendly one. "
               "(They're all the friendly one.) \U0001F49B\n\n"
               f"{TAGS_CORE}"),
      photo_brief="Waist-up portrait at their station, natural smile, tidy background. Use the shoot-day photo.",
      notes="Team posts reliably outperform product posts for reach. Consent + let them approve the fun fact."),

    # ============================ WEEK 5 ============================
    T("w5-mon-post", date(2026, 8, 3), IG, "Feed Post", "Wellness",
      "Beat the winter slump - the basics that work", best="7:00 PM", mins=15,
      content=("August slump hitting? You're not imagining it. \U0001F634 Before anything fancy, "
               "nail the free stuff:\n\n"
               "• Sunlight before screens in the morning\n"
               "• A walk that gets your heart rate up\n"
               "• Protein at breakfast\n"
               "• A consistent bedtime (yes, really)\n\n"
               "Then, if your routine needs backup, our vitamin aisle and team are here to help "
               "you choose what suits. Supporting the basics - that's the job. \U0001F4AA\n\n"
               f"{TAGS_CORE} {TAGS_WELL}"),
      image_prompt=("Morning-energy flat lay: glass of water, running shoes corner, notebook, "
                    f"generic white supplement bottle, sunrise light streaks. {AI_STYLE}"),
      photo_brief="Or: your vitamin aisle wide shot from the shoot bank.",
      notes="COMPLIANCE: general wellbeing framing only - no 'boosts immunity/cures fatigue' claims."),

    T("w5-wed-reel", date(2026, 8, 5), IG, "Reel", "Wellness",
      "Reel: vitamin aisle 101 in 40 seconds", best="7:30 PM", mins=30,
      content=("On-screen hook: \"Vitamin aisle 101 - what's actually what \U0001F9D0\"\n\n"
               "Caption: Multis, B's, C, D, magnesium... the aisle can be a lot. 40-second lap of "
               "what each section is for - in plain English. For advice on what suits YOU, come "
               "chat to the team (that part's free).\n\n"
               f"{TAGS_CORE} {TAGS_WELL}"),
      video_prompt=("AI option: smooth vertical dolly along a bright, well-organised pharmacy "
                    "vitamin aisle, shelves gently glowing as sections highlight, clean modern "
                    "look, 9:16, 20s, no readable brand labels."),
      photo_brief=("Real: walking clip down your aisle, pausing at each section (multi/B/C/D/"
                   "magnesium), point at each. Text overlay per section: one plain-English line. "
                   "COMPLIANCE: keep overlays to 'commonly used to support...' wording."),
      notes=""),

    T("w5-thu-post", date(2026, 8, 6), IG, "Feed Post", "Wellness",
      "Staff pick: the multivitamin question", best="7:00 PM", mins=15,
      content=("The question we get most in the vitamin aisle: \"Do I actually need a multi?\" "
               "\U0001F914\n\n"
               "Honest answer: it depends on you - your diet, routine and life stage. That's why "
               "the real staff pick this week isn't a product... it's a chat with our team. Free, "
               "no bookings, no judgement. We'll help you figure out what (if anything) suits.\n\n"
               f"{TAGS_CORE} {TAGS_WELL}"),
      photo_brief="Team member mid-chat with a customer in the vitamin aisle (staged with a staff member as the 'customer').",
      notes="Positions you as advice-first, not sales-first - reliably earns trust + comments."),

    T("w5-thu-sale", date(2026, 8, 6), SALE, "Sale Upload", "Catalogue",
      "Catalogue launch - upload sale content everywhere", best="9:00 AM", mins=25,
      content=("Catalogue cycle 3:\n"
               "1) IG story set (3 frames) with hero deals\n"
               "2) GBP Offer post with end date\n"
               "3) Facebook post with 2-3 hero deals\n\n"
               "Hero deals from the priceline.com.au carousel/catalogue on your machine."),
      notes=""),

    T("w5-sat-post", date(2026, 8, 8), IG, "Feed Post", "Beauty",
      "Self-care Saturday - the pamper shelf", best="9:00 AM", mins=15,
      content=("Self-care Saturday plans: bath, mask, big robe, phone in another room. \U0001F6C1\n\n"
               "The pamper shelf is stocked - bath soaks, sheet masks, hair treatments and the "
               "good-smelling everything. Build your Sunday reset kit this weekend at Pacific "
               "Fair. You've earnt it. ✨\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      image_prompt=("Cosy pamper flat lay: sheet mask packet, bath salts jar spilling slightly, "
                    f"rolled white towel, small candle (unlit), pink accents. {AI_STYLE}"),
      photo_brief="Or: your bath/pamper display from the content bank.",
      notes=""),

    # ============================ WEEK 6 ============================
    T("w6-mon-post", date(2026, 8, 10), IG, "Carousel", "Skincare",
      "Hyaluronic vs Niacinamide - what actually does what", best="7:00 PM", mins=20,
      content=("The two ingredients on every label - decoded in one swipe. \U0001F9EA\n\n"
               "HYALURONIC ACID: a moisture magnet. Draws water into skin - use on damp skin, "
               "seal with moisturiser. Best for: dryness, dullness.\n\n"
               "NIACINAMIDE: the multitasker. Supports the skin barrier, helps with the look of "
               "pores and uneven tone. Plays nice with almost everything.\n\n"
               "Spoiler: you can use both. Come ask the beauty counter where each fits in YOUR "
               "routine. \U0001F9F4\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      image_prompt=("Split-composition image: left, a water droplet macro on glass (hyaluronic); "
                    f"right, a matte serum swatch swirl (niacinamide); pink dividing line. {AI_STYLE}"),
      photo_brief="Or: two serum bottles side by side with handwritten-style labels 'HA' and 'B3'.",
      notes="Educational carousels = highest save rate. Saves boost your reach for a week."),

    T("w6-wed-reel", date(2026, 8, 12), IG, "Reel", "Skincare",
      "Reel: decode a skincare label in 30 seconds", best="7:30 PM", mins=30,
      content=("On-screen hook: \"POV: you can finally read a skincare label \U0001F50D\"\n\n"
               "Caption: Ingredients list = ordered by amount, first 5 matter most. 'Fragrance-"
               "free' beats 'unscented' for sensitive skin. Percentages aren't everything. 30 "
               "seconds and you'll never shop skincare the same. Save this. \U0001F9E0\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      video_prompt=("AI option: extreme close-up pan across an elegant generic skincare bottle "
                    "label, key words highlighting in pink as the camera passes, clean studio "
                    "light, 9:16, 20s, fictional brand."),
      photo_brief="Real: film over your shoulder holding a product, finger tracing the label as you explain 3 quick tips to camera.",
      notes=""),

    T("w6-thu-post", date(2026, 8, 13), IG, "Feed Post", "Skincare",
      "SPF in winter. Yes, still. Yes, every day.", best="7:00 PM", mins=15,
      content=("Queensland UV does not check the calendar. ☀️\n\n"
               "Winter sun through the car window, on the school run, at Saturday sport - it all "
               "adds up. Daily SPF is the single best anti-ageing, skin-protecting habit there "
               "is, 365 days a year.\n\n"
               "Face SPFs that don't feel like sunscreen - the shelf is full of them. Come find "
               "yours at Pacific Fair. \U0001F9F4\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY} #SunSafety #SlipSlopSlap"),
      image_prompt=("SPF bottle casting a long winter-morning shadow on white, sun flare corner, "
                    f"'365' subtly formed by three small product shadows. {AI_STYLE}"),
      photo_brief="Or: your SPF display shot from the content bank, golden-hour light if you can.",
      notes=""),

    T("w6-sat-post", date(2026, 8, 15), IG, "Feed Post", "Skincare",
      "Night shift: intro to retinol (gently)", best="9:00 AM", mins=15,
      content=("Thinking about starting retinol? Read this first. \U0001F319\n\n"
               "• Start LOW (low strength, 2 nights/week)\n"
               "• Buffer with moisturiser if you're sensitive\n"
               "• Patch test first\n"
               "• SPF every single morning after (non-negotiable)\n\n"
               "Slow and steady wins glowing skin. Our beauty team can help you pick a gentle "
               "starting point - come chat. ✨\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      image_prompt=("Night-time vanity scene: retinol-style dropper bottle in moonlight blue "
                    f"tones with one warm lamp glow, calm and minimal. {AI_STYLE}"),
      photo_brief="Or: night-care shelf section, moody-ish shot (lower exposure).",
      notes=""),

    # ============================ WEEK 7 ============================
    T("w7-mon-post", date(2026, 8, 17), IG, "Feed Post", "Team",
      "Meet the team: [team member #2 - beauty advisor]", best="7:00 PM", mins=15,
      content=("MEET THE TEAM \U0001F44B This is [name], the reason half our regulars walk out "
               "with a perfect shade match.\n\n"
               "• Role: [role]\n"
               "• Superpower: [e.g. finding your exact foundation shade in 90 seconds]\n"
               "• Current obsession: [product/trend]\n\n"
               "Come get matched at Pacific Fair - and tell them we sent you. \U0001F49B\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      photo_brief="Portrait at the beauty wall, holding their current obsession product. From the shoot bank if possible.",
      notes=""),

    T("w7-wed-reel", date(2026, 8, 19), IG, "Reel", "Team",
      "Reel: a day at Priceline Pacific Fair", best="7:30 PM", mins=35,
      content=("On-screen hook: \"6:55 AM at your local Priceline ☀️\"\n\n"
               "Caption: Roller doors, first coffee, shelves faced, scripts checked, doors open, "
               "familiar faces all day, lights off. The unglamorous, kind of lovely rhythm of "
               "your local pharmacy. \U0001F3E5\U0001F49B Come be part of the middle bit.\n\n"
               f"{TAGS_CORE}"),
      video_prompt=("AI option: warm montage of a small pharmacy day-in-the-life - sunrise "
                    "storefront, shelves being straightened by hands, counter bell, sunset door "
                    "close - cosy film grain, 9:16, 20s, no identifiable faces or brands."),
      photo_brief=("Real (do this one for real - it's gold): 8-10 clips x 2s across one day - "
                   "roller door up, coffee, facing shelves, till opening, team laughing, door "
                   "close. Everyone loves a day-in-the-life. Consent from anyone in frame."),
      notes="Evergreen - re-usable content. Save the raw clips."),

    T("w7-thu-post", date(2026, 8, 20), IG, "Feed Post", "Community",
      "Local love - proud to be Pacific Fair locals", best="7:00 PM", mins=15,
      content=("Eight years... 25+ team members... a few thousand familiar faces. \U0001F49B\n\n"
               "Being the local pharmacy inside Pacific Fair means school-holiday rushes, "
               "Saturday-sport ice pack emergencies, and knowing half our Sisterclub members by "
               "name. Broadbeach, we love being yours.\n\n"
               "Tag someone who's always 'just quickly ducking into Priceline'. \U0001F602\n\n"
               f"{TAGS_CORE} #ShopLocal #GoldCoastLocal"),
      photo_brief="Storefront hero shot from the content bank, or team group photo.",
      notes="Adjust the years/numbers to your real story. Tag @pacificfair - they reshare local businesses."),

    T("w7-thu-sale", date(2026, 8, 20), SALE, "Sale Upload", "Catalogue",
      "Catalogue launch - upload sale content everywhere", best="9:00 AM", mins=25,
      content=("Catalogue cycle 4:\n"
               "1) IG story set (3 frames) with hero deals\n"
               "2) GBP Offer post with end date\n"
               "3) Facebook post with 2-3 hero deals\n\n"
               "Hero deals from the priceline.com.au carousel/catalogue on your machine."),
      notes=""),

    T("w7-sat-post", date(2026, 8, 22), IG, "Carousel", "Community",
      "Most-loved this month - your top 5", best="9:00 AM", mins=20,
      content=("YOU voted with your baskets - the 5 most-loved products at Priceline Pacific "
               "Fair this month. \U0001F3C6 Swipe to see if your fave made the cut.\n\n"
               "Slides: cover → #5 to #1 countdown (product photo + one line on why it's "
               "loved) → final: \"Disagree? Tell us your #1 in the comments \U0001F447\"\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      photo_brief="Pull your actual top 5 front-shop sellers from POS, shoot each on the counter. (Front-shop only - no medicines.)",
      notes="Ties your POS data into content - nobody local is doing this. Countdown format drives comments."),

    # ============================ WEEK 8 ============================
    T("w8-mon-post", date(2026, 8, 24), IG, "Feed Post", "Skincare",
      "Spring skin transition - 3 swaps to make now", best="7:00 PM", mins=15,
      content=("Spring is 8 days away, Gold Coast. \U0001F338 Your winter routine did its job - "
               "now three easy swaps for the season switch:\n\n"
               "1️⃣ Rich cream → lighter lotion or gel moisturiser\n"
               "2️⃣ Add gentle exfoliation back in (1-2x/week)\n"
               "3️⃣ Check your SPF expiry before the UV climbs\n\n"
               "All swappable in one lap of our skincare wall. See you this week? ✨\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      image_prompt=("Winter-to-spring transition scene: heavy cream jar on the left in cool blue "
                    "light transitioning to a light gel moisturiser on the right in warm spring "
                    f"light with tiny blossom petals. {AI_STYLE}"),
      photo_brief="Or: side-by-side of a rich cream and a gel moisturiser from your shelf.",
      notes=""),

    T("w8-wed-reel", date(2026, 8, 26), IG, "Reel", "Skincare",
      "Reel: winter -> spring routine swap", best="7:30 PM", mins=30,
      content=("On-screen hook: \"Swapping my routine for spring in 25 seconds \U0001F338\"\n\n"
               "Caption: Out: the heavy cream (thanks for your service). In: light hydration, "
               "gentle exfoliant, fresh SPF. Every swap is on our shelves now. What's the first "
               "thing YOU change for spring?\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      video_prompt=("AI option: satisfying vertical 'swap' transitions - winter product slides "
                    "off screen as spring product slides in, x3 pairs, pastel spring palette, "
                    "petals drift, 9:16, 15s."),
      photo_brief="Real: 3 quick swap shots - hand places winter product down, picks spring one up. Snap transitions in-editor.",
      notes=""),

    T("w8-thu-post", date(2026, 8, 27), IG, "Feed Post", "Beauty",
      "New season arrivals + something big is coming", best="7:00 PM", mins=15,
      content=("First spring arrivals are hitting shelves NOW. \U0001F338 New skincare, fresh "
               "makeup drops and the season's colours landing daily at Pacific Fair.\n\n"
               "And a little birdie says Priceline's biggest beauty event of the year isn't far "
               "away... \U0001F440 Sisterclub members will hear it here first - are you on the "
               "list? (Free to join, 2 minutes, at the counter.)\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      image_prompt=("New-season beauty arrangement bursting out of an open delivery box, spring "
                    f"florals tucked between products, bright and fresh. {AI_STYLE}"),
      photo_brief="Or: real unboxing shot of new-season stock on the counter (great authenticity).",
      notes="Festival of Beauty typically lands Sep/Oct - this tease sets up next month's plan."),

    T("w8-fri-shoot", date(2026, 8, 28), PHOTO, "Photo Shoot", "Content Bank",
      "Monthly photo shoot - spring edition", best="8:15 AM", mins=45,
      content=("September content bank, before doors open:\n\n"
               "1. Spring displays + new-season end caps (these are the priority)\n"
               "2. Fresh storefront shot (spring signage if up)\n"
               "3. Beauty wall re-shoot (it changes monthly)\n"
               "4. 10 product close-ups: incoming spring bestsellers\n"
               "5. Team candids - anyone not yet featured in Meet the Team\n"
               "6. Detail shots: hands swatching, basket with products, Sisterclub card at till\n\n"
               "Album: 'Content Bank - Sep'."),
      notes=""),

    T("w8-sat-post", date(2026, 8, 29), IG, "Feed Post", "Beauty",
      "Spring clean your beauty bag (the expiry check)", best="9:00 AM", mins=15,
      content=("Spring cleaning starts with the makeup bag. \U0001F9FC Quick expiry check:\n\n"
               "• Mascara: replace every 3 months (eye health!)\n"
               "• Liquid foundation: ~12 months once opened\n"
               "• Lipstick: ~18 months\n"
               "• SPF: check the date - old SPF = weak SPF\n"
               "• That gritty eyeliner from 2023: we both know. \U0001F5D1️\n\n"
               "Refill the gaps this weekend at Pacific Fair - we'll help you rebuild the kit. "
               "✨\n\n"
               f"{TAGS_CORE} {TAGS_BEAUTY}"),
      image_prompt=("Neatly organised open makeup bag, contents arranged in a tidy grid beside "
                    f"it 'knolling' style, one item in a small bin, playful. {AI_STYLE}"),
      photo_brief="Or: knolling shot on your counter using tester products.",
      notes="PSA-style posts get shared to group chats - great reach. Cross-post to Facebook."),
]


# ---------------------------------------------------------------------------
# Recurring tasks generated from WEEKS
# ---------------------------------------------------------------------------
def _recurring():
    tasks = []
    for w in WEEKS:
        n, mon = w["num"], w["start"]
        tue, fri = mon + timedelta(days=1), mon + timedelta(days=4)

        tasks.append(T(f"w{n}-mon-gbp", mon, GBP, "GBP Post", w["theme"],
                       f"GBP post: {w['gbp_mon'][0]}", best="8:30 AM", mins=10,
                       content=w["gbp_mon"][1],
                       notes="Google posts expire after ~7 days - one per week keeps the profile 'active' in Google's eyes."))

        tasks.append(T(f"w{n}-mon-seo", mon, SEO, "SEO Task", "Local SEO",
                       f"SEO: {w['seo'][0]}", best="", mins=20,
                       content=w["seo"][1]))

        tasks.append(T(f"w{n}-tue-story", tue, IG, "Story", w["theme"],
                       f"Story: {w['tue_story'][0]}", best="12:00 PM", mins=10,
                       content=w["tue_story"][1],
                       notes="Interactive stickers (polls/quizzes) tell the algorithm people engage with you - cheap wins."))

        tasks.append(T(f"w{n}-tue-reviews", tue, REV, "Review Replies", "Reputation",
                       "Reply to all new Google reviews", best="", mins=15,
                       content=("Open Google Business Profile > Reviews. Reply to EVERY new review "
                                "since last week - positive and negative.\n\n"
                                "Templates are in the Playbook tab (Review Reply Templates). "
                                "Golden rules: reply within 48h, use their name, never confirm "
                                "anyone is a patient or mention medicines/health details, take "
                                "complaints offline with a phone number."),
                       notes="100% response rate is a local-SEO ranking signal AND visible social proof.")),

        tasks.append(T(f"w{n}-fri-story", fri, IG, "Story", w["theme"],
                       f"Story: {w['fri_story'][0]}", best="3:00 PM", mins=10,
                       content=w["fri_story"][1]))

        tasks.append(T(f"w{n}-fri-gbp-photos", fri, GBP, "GBP Photos", "Local SEO",
                       "Upload 3-5 fresh photos to Google", best="", mins=10,
                       content=("Upload 3-5 photos to your Google Business Profile.\n\n"
                                f"Suggested this week: {w['gbp_photos']}\n\n"
                                "Profiles with regular photo uploads get significantly more "
                                "direction requests and calls. Use content-bank photos - "
                                "60 seconds of uploading."),
                       notes=""))
    return tasks


TASKS = sorted(CONTENT_TASKS + _recurring(), key=lambda t: (t["date"], t["best_time"] or "zz"))

# Attach week numbers
for _t in TASKS:
    for _w in WEEKS:
        if _w["start"] <= _t["date"] <= _w["start"] + timedelta(days=6):
            _t["week"] = _w["num"]
            break
    else:
        _t["week"] = 0


# ---------------------------------------------------------------------------
# PLAYBOOK - strategy, templates & reference (rendered on the Playbook tab)
# ---------------------------------------------------------------------------
PLAYBOOK = [
    {"title": "How this system works", "icon": "\U0001F9ED", "body": """
**The rhythm:** ~30-60 min on Monday (post + GBP + SEO task), then 10-15 min most days.
Every task here is pre-written - captions are paste-ready, prompts are copy-ready.

**If you fall behind:** overdue tasks stack up in the *Catch-up* section of the Today tab,
oldest first. Work top-down: tick **Done** or hit **Skip** (skipping is allowed! An old
dated post - e.g. a catalogue that ended - should be skipped, not posted late). The one
marked **UP NEXT** is always your single next action.

**Golden rule:** consistency beats perfection. 4 average posts a week beats 1 perfect
post a fortnight, every time, on every platform.
"""},
    {"title": "Weekly rhythm & time budget", "icon": "⏱️", "body": """
| Day | Jobs | Time |
|---|---|---|
| Mon | Feed post + GBP post + weekly SEO task | 45-60 min |
| Tue | Interactive story + reply to reviews | 25 min |
| Wed | Reel (the big rock of the week) | 30-35 min |
| Thu | Feed post (+ catalogue uploads fortnightly) | 15-40 min |
| Fri | Story + GBP photo upload | 20 min |
| Sat | Feed post (scheduled Fri if you prefer) | 15 min |
| Sun | **Off.** Protected. | 0 min |

**Batching tip:** you can do the whole week's captions in one Monday sitting and just
hit post each day - the content is already written, so it's mostly copy-paste-photo.
"""},
    {"title": "Best posting times (AU retail)", "icon": "\U0001F552", "body": """
- **Feed posts:** 7:00-8:00 PM weekdays (scroll-after-dinner peak) - **Sat 9:00 AM** for weekend-shopper planning
- **Reels:** 7:30 PM - give them a 2-hour head start before late-night scrolling
- **Stories:** midday (12 PM) and 3 PM - lunch break + school-run scroll
- **GBP posts:** Monday morning - fresh for the week's searches
- **Catalogue content:** morning of launch day, always

These are starting points - after 4 weeks, check IG Insights > Audience > most active
times and shift to match YOUR followers.
"""},
    {"title": "Hashtag library", "icon": "#️⃣", "body": f"""
Copy the set that matches the post (already baked into every caption in the plan):

**Core (every post):**
`{TAGS_CORE}`

**Beauty posts:**
`{TAGS_BEAUTY}`

**Wellness posts:**
`{TAGS_WELL}`

Keep it to 8-12 total. Local tags (#PacificFair #Broadbeach #GoldCoast) matter most -
that's who can actually walk in. Swap #WinterWellness for #SpringSkin etc. as seasons turn.
"""},
    {"title": "Review reply templates", "icon": "⭐", "body": """
**PRIVACY RULE (pharmacy-specific, non-negotiable):** never confirm someone is a patient,
never mention their medicines, conditions or visits - even if THEY mention them in the
review. Reply warmly but generically.

**5 stars (general):**
> Thanks so much, [Name]! Our team works hard to make every visit a good one, and this
> made their day. See you next time at Pacific Fair! \U0001F49B

**5 stars (staff mentioned):**
> [Name], thank you! We've passed this on to [staff name] - you've made their week.
> Thanks for the support, and see you in store soon!

**3-4 stars (good but...):**
> Thanks for the honest feedback, [Name] - genuinely helpful. We're glad [positive bit]
> hit the mark, and we hear you on [issue]. We're onto it. Hope to see you again soon.

**1-2 stars (service issue):**
> Hi [Name], I'm sorry your visit fell short - that's not the standard we hold ourselves
> to. I'd really like to understand what happened and make it right. Please call me
> directly on (07) XXXX XXXX and ask for Jason. - Jason, Owner

**1-2 stars (price/stock):**
> Hi [Name], thanks for flagging this and sorry for the frustration. Stock moves fast at
> Pacific Fair - if you call ahead we'll happily check and hold items for you. We've
> passed your feedback on. Hope we can win you back.

Reply to **every** review within 48h. Owner-signed replies to negative reviews are read
by hundreds of future customers - you're really writing to *them*.
"""},
    {"title": "Google Business Profile checklist", "icon": "\U0001F4CD", "body": """
The GBP is your #1 local marketing asset - most customers see it before your Instagram.

- [ ] Primary category: **Pharmacy** - secondaries: Beauty Supply Store, Vitamin & Supplements Store
- [ ] All services listed WITH descriptions (flu vax, BP checks, Webster-paks, NDSS, beauty)
- [ ] Hours accurate incl. public holidays (Google flags 'hours may differ' otherwise)
- [ ] 1 post per week (scheduled in this plan - Mondays)
- [ ] 3-5 new photos per week (scheduled - Fridays)
- [ ] 100% review response rate, <48h (scheduled - Tuesdays)
- [ ] Q&A seeded with your top questions (Week 2 task)
- [ ] Messaging ON only if someone will actually answer it

**Why it matters:** activity signals (posts, photos, review replies) directly influence
the local 3-pack ranking for searches like "pharmacy near me" and "chemist Pacific Fair".
"""},
    {"title": "Local SEO essentials", "icon": "\U0001F50E", "body": """
**Keywords you want to own** (weave naturally into GBP posts & service descriptions):
- pharmacy Pacific Fair / chemist Pacific Fair
- pharmacy Broadbeach / chemist Broadbeach
- flu vaccination Gold Coast
- Webster pack pharmacy Gold Coast
- Priceline Pacific Fair

**The checklist:**
1. **NAP consistency** - Name/Address/Phone identical everywhere (Week 3 task)
2. **Review velocity** - 3-5 fresh reviews/month beats 200 old ones (Week 7 drive)
3. **GBP activity** - weekly posts + photos (scheduled)
4. **Your Priceline store page** - confirm services/hours are current; it ranks for
   brand searches
5. **Socials linked** - IG/FB profiles link to your store page

That's genuinely 90% of local SEO for a single-location retailer. No agency required.
"""},
    {"title": "Photo shot-list library", "icon": "\U0001F4F8", "body": """
Evergreen bank - shoot monthly (scheduled), pull from it daily. Phone + morning light
before open is all you need.

**Storefront & space:** mall-walkway front (portrait + landscape), entrance context,
each aisle wide, consult room (open, empty), seasonal end-caps.

**People (consent first, keep a note):** team candids at stations, group shot, hands
restocking, "mid-chat" advice moments (staged is fine).

**Product:** bestseller close-ups on white counter near window light, flat lays,
hand-holding-product against blurred shelf, basket-with-products.

**Rules:** portrait orientation for IG, tidy shelf edges first, NEVER any scripts,
patient info or dispensary labels in frame. Nothing kills trust like a privacy slip.
"""},
    {"title": "AI image & video prompt guide", "icon": "\U0001F916", "body": f"""
Every content task carries a ready-made AI prompt. To keep the grid looking like ONE
brand, they all share this style base - reuse it for anything new:

> {AI_STYLE}

**Where AI works well:** flat lays, concept shots, backgrounds, seasonal scenes,
story graphics.

**Where real always beats AI:** your actual shelves, your products (AI mangles labels),
and your PEOPLE - never use AI faces as 'staff'; followers can tell, and trust is your
whole brand as a pharmacy.

**Text-on-image rule:** generate imagery clean (no text) and add any words in the IG
editor or Canva - AI text is still unreliable and it keeps everything editable.
"""},
    {"title": "Pharmacy advertising compliance", "icon": "⚖️", "body": """
You know this world, but as a standing checklist for anything you post (TGA Advertising
Code + AHPRA guidance):

- **Prescription medicines (S4/S8): never.** No names, photos, prices or availability
  posts. Includes 'behind the counter' shots where labels are readable.
- **Pharmacist Only (S3):** only a small approved subset may be advertised - simplest
  policy for social: don't feature specific S3 products at all.
- **Vitamins/supplements:** stick to general wellbeing language ('supports your daily
  routine'). No treatment/cure/prevention claims. When in doubt, quote the label only.
- **No testimonials about therapeutic goods** in your posts/ads (sharing service
  praise - friendly staff, easy experience - is fine).
- **Vaccinations:** promote the *service* (availability, walk-ins, booking) - no vaccine
  brand names.
- **Review replies:** never confirm patient status or discuss anyone's health. Ever.
- **Price promos:** front-shop retail (beauty, general merch) - promote freely.

Every task in this plan was written inside these lines. The final call on anything is
yours as the pharmacist - if something feels grey, it's a no.
"""},
    {"title": "Monthly review ritual", "icon": "\U0001F4C8", "body": """
Last Friday of the month, 30 minutes (Week 8 has it scheduled):

1. **IG Insights:** top 3 posts by reach and by saves. What formats/topics won? Do more.
2. **GBP Performance:** calls, direction requests, website clicks - trending up?
3. **Reviews:** count + average this month vs last.
4. **Pick next month's 4 weekly themes** from what's coming (September = Festival of
   Beauty season) and what worked.
5. **Ask Claude to generate the next 4-week block** in this same format - give it your
   theme notes and any real staff names/products to write in.

What gets measured gets managed - and this closes the loop so the plan improves each month.
"""},
]
