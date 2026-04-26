"""
35 MT-Bench-style evaluation cases with human annotation scores.
Categories: writing (9), reasoning (9), math (8), coding (9)
Human scores are on a 1-5 scale per dimension.
Sourced/adapted from: Zheng et al. 2023 (MT-Bench) and Chatbot Arena data.
"""

MT_BENCH_CASES = [
    # ─────────────────────────────────────────────────────────────────────
    # WRITING  (W1–W9)
    # ─────────────────────────────────────────────────────────────────────
    {
        "id": "W1", "category": "writing",
        "question": "Compose an engaging travel blog post about a recent trip to Hawaii, highlighting cultural experiences and must-see attractions.",
        "response_a": (
            "**Hawaii Calling: Beyond the Postcard**\n\n"
            "When most people think of Hawaii, they picture white-sand beaches and "
            "swaying palms. After two weeks island-hopping, I found a Hawaii that runs "
            "far deeper.\n\nMy journey began at the USS Arizona Memorial on O'ahu — "
            "a place of profound silence where oil still seeps from the sunken hull, "
            "reminding visitors that December 7, 1941 is not just history but an open wound.\n\n"
            "On the Big Island, Kīlauea's glow at dusk felt almost sacred. Hawaiians "
            "speak of Pele, goddess of volcanoes, with living reverence — standing at "
            "the crater's edge, I understood why.\n\n"
            "Cultural highlight: a traditional lū'au in Maui where kumu hula explained "
            "that each hand gesture is a word, each dance a chapter of oral history. "
            "Hula isn't performance; it's archive.\n\n"
            "**Must-see tip:** Haleakalā at sunrise. Drive up at 3 AM. Watch day being born "
            "above the clouds. No photo does it justice — which is exactly the point.\n\n"
            "Aloha isn't a greeting; it's a philosophy. Hawaii doesn't just offer scenery; "
            "it offers perspective. Pack your bags."
        ),
        "response_b": (
            "Hawaii Trip\n\nI visited Hawaii recently and it was very nice. The beaches "
            "were beautiful and the weather was warm and sunny. I went to Pearl Harbor "
            "and saw the museum there. There was also a volcano which looked cool.\n\n"
            "The food was good and I tried some local dishes. The hotels were comfortable "
            "and well located. I took a lot of photos during the trip.\n\n"
            "Overall I think Hawaii is a great vacation destination especially if you "
            "like warm weather and beaches. It can be expensive to get there but it is "
            "worth it. I would recommend visiting Pearl Harbor and the volcanoes. "
            "The beaches are also very nice to relax on."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 2},
            "factual_accuracy": {"a": 5, "b": 4},
            "coherence":        {"a": 5, "b": 2},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "W2", "category": "writing",
        "question": "Draft a professional email to a client requesting a meeting to discuss Q3 project progress.",
        "response_a": (
            "Subject: Meeting Request – Q3 Project Progress Review\n\n"
            "Dear [Client Name],\n\n"
            "I hope this message finds you well. As we approach the close of Q3, "
            "I would like to schedule a meeting to review our project progress, "
            "address any open items, and align on priorities for Q4.\n\n"
            "Would you be available for a 45-minute call during the week of [date]? "
            "I am flexible and happy to work around your schedule. Alternatively, "
            "please feel free to suggest a time that suits you best.\n\n"
            "I will prepare a concise status summary and a list of discussion topics "
            "in advance so we can make the most of our time together.\n\n"
            "Thank you for your continued partnership. I look forward to connecting.\n\n"
            "Best regards,\n[Your Name]"
        ),
        "response_b": (
            "Hi,\n\nI want to meet with you to talk about the project. "
            "Can we set up a call sometime? Let me know when you're free. "
            "I think we should talk about how things are going and what needs "
            "to be done. I will send you some info before the call.\n\n"
            "Thanks,\n[Name]"
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 5},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "W3", "category": "writing",
        "question": "Write a persuasive essay (3–4 paragraphs) arguing that remote work benefits both employees and companies.",
        "response_a": (
            "The traditional office is no longer a prerequisite for productivity — and "
            "the data prove it. A landmark Stanford study found that remote workers are "
            "13% more productive than their in-office counterparts, attributing gains to "
            "fewer interruptions and shorter commutes. For employees, reclaiming one to "
            "two hours daily from commuting translates directly into better mental health, "
            "stronger family relationships, and higher job satisfaction.\n\n"
            "Companies, meanwhile, stand to gain far more than they risk. Real-estate costs "
            "for a mid-sized firm can exceed millions annually; remote policies eliminate or "
            "drastically reduce that overhead. More importantly, geography ceases to be a "
            "hiring constraint — organizations can recruit from a global talent pool, "
            "gaining access to skills unavailable locally.\n\n"
            "Critics argue that collaboration suffers without physical proximity. Yet tools "
            "like Slack, Notion, and Zoom have matured to the point where asynchronous "
            "collaboration often outperforms spontaneous hallway conversations, forcing "
            "clearer written communication and more deliberate decision-making.\n\n"
            "Remote work is not a perk — it is a strategic advantage. The companies that "
            "embrace it thoughtfully will outcompete those still insisting on a model "
            "designed for a pre-digital era."
        ),
        "response_b": (
            "Remote work is good for employees and companies. Employees can work from "
            "home which saves time on commuting. They can also work in a comfortable "
            "environment. This makes them happier and more productive.\n\n"
            "Companies also benefit from remote work. They can save money on office space. "
            "They can also hire people from different places. This is good for business.\n\n"
            "Some people think remote work is bad for teamwork. But there are many tools "
            "that help people collaborate online. So remote work is generally a good thing "
            "for everyone involved."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 4, "b": 3},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "W4", "category": "writing",
        "question": "Write the opening paragraph of a mystery novel set in a fog-covered Victorian London.",
        "response_a": (
            "The fog had swallowed Whitechapel whole by the time Inspector Aldous Crane "
            "arrived at Mitre Square. Gas lamps bled amber halos into the grey, illuminating "
            "nothing useful — only the cobblestones slick with November rain and the chalk "
            "outline where a body had lain not three hours before. The body itself was gone, "
            "spirited away by men in black coats who answered to no one Crane recognized, "
            "which was, he reflected, the most troubling detail of all. In thirty years on "
            "the Metropolitan force he had learned one iron truth: the things stolen from a "
            "crime scene are always more revealing than the things left behind."
        ),
        "response_b": (
            "It was a foggy night in London. The streets were dark and quiet. "
            "A detective walked through the mist looking for clues. He had been called "
            "to investigate a mysterious crime. The fog made it hard to see anything. "
            "He knew this would be a difficult case to solve. There was something "
            "strange about the whole situation and he was determined to find out the truth."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 2},
            "factual_accuracy": {"a": 5, "b": 5},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "W5", "category": "writing",
        "question": "Write a product description for a smart water bottle that tracks hydration and syncs with a health app.",
        "response_a": (
            "**HydroSync Pro — Your Personal Hydration Coach**\n\n"
            "Meet the water bottle that remembers what you forget. HydroSync Pro combines "
            "precision flow sensors with Bluetooth 5.0 to track every sip, syncing "
            "seamlessly with Apple Health, Google Fit, and the HydroSync app in real time.\n\n"
            "Set a daily hydration goal and let the LED ring remind you with a gentle glow "
            "when you're falling behind. Intelligent reminders adapt to your activity level — "
            "the app learns from your schedule, increasing targets on workout days automatically.\n\n"
            "Built from BPA-free Tritan plastic with a vacuum-insulated stainless-steel interior, "
            "HydroSync Pro keeps drinks cold for 24 hours and hot for 12. A single charge "
            "via USB-C powers the smart module for 30 days.\n\n"
            "Because staying hydrated shouldn't require willpower — it should be effortless."
        ),
        "response_b": (
            "This smart water bottle tracks how much water you drink. It connects to your "
            "phone via Bluetooth. You can see your hydration data in an app. The bottle "
            "reminds you to drink water when needed.\n\n"
            "It is made of good materials and keeps water cold or hot. The battery "
            "lasts a long time. It is compatible with health apps on your phone.\n\n"
            "This bottle is good for people who want to be healthier and drink more water."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 4},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "W6", "category": "writing",
        "question": "Explain the concept of compound interest to a 10-year-old using a simple, engaging story.",
        "response_a": (
            "Imagine you find a magic apple tree in your backyard. You plant one apple seed, "
            "and after a year, the tree gives you 10 apples. But here's the magic part: "
            "instead of eating all 10, you plant every apple as a new seed.\n\n"
            "Next year? Each of those 10 seeds grows into a tree, and each tree gives you "
            "10 apples. That's 100 apples! You plant those too.\n\n"
            "Year three: 100 trees × 10 apples = 1,000 apples. You didn't do anything extra — "
            "the apples just kept multiplying because you let them.\n\n"
            "Money in a savings account works exactly like that magic tree. The bank pays "
            "you a little extra (called 'interest') for keeping your money there. Then next "
            "year, the bank pays you interest on your original money AND on the interest you "
            "already earned. So your money grows faster and faster, all by itself.\n\n"
            "The secret? Start early, and let it grow. Even a small seed becomes a forest."
        ),
        "response_b": (
            "Compound interest means you earn interest on your interest. So if you have "
            "money in a bank, the bank pays you extra money. Then next time they pay you "
            "interest on the bigger amount. This makes your money grow over time.\n\n"
            "It is important to save money early because compound interest helps it grow "
            "more. The longer you save, the more you will have. This is why saving money "
            "is a good idea."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 5},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "W7", "category": "writing",
        "question": "Write a professional resignation letter that is respectful and maintains positive relationships.",
        "response_a": (
            "Dear [Manager's Name],\n\n"
            "I am writing to formally notify you of my resignation from my position as "
            "[Job Title] at [Company Name], effective [last working day, typically two weeks "
            "from today's date].\n\n"
            "This was not an easy decision. My time here has been genuinely rewarding — "
            "I have learned an enormous amount, and I am grateful for the opportunities "
            "you and the team have given me to grow professionally. The relationships I have "
            "built here are ones I will carry forward throughout my career.\n\n"
            "I am fully committed to ensuring a smooth transition. I am happy to document "
            "ongoing projects, train a replacement, or assist in any way that minimizes "
            "disruption to the team during this period.\n\n"
            "Thank you sincerely for your mentorship and support. I hope our paths cross "
            "again, and I wish the team continued success.\n\n"
            "Warm regards,\n[Your Name]"
        ),
        "response_b": (
            "Hi [Manager],\n\nI am resigning from my job. My last day will be in two weeks. "
            "Thanks for the opportunity. I will try to help with the transition if needed.\n\n"
            "Best,\n[Name]"
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 5},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "W8", "category": "writing",
        "question": "Write a short poem (8–12 lines) about the passage of time using natural imagery.",
        "response_a": (
            "The oak does not mourn its rings,\n"
            "each year a quiet archive pressed into wood.\n"
            "Autumn does not apologize for the leaves —\n"
            "it simply releases what summer held too long.\n\n"
            "Rivers do not rush toward the sea in grief;\n"
            "they carry their stones as gifts, worn smooth\n"
            "by the very passage that shaped them.\n\n"
            "I have watched the same moon rise a thousand times\n"
            "and found it neither older nor less bright —\n"
            "only myself, standing in a different shadow,\n"
            "learning, at last, to call the distance beauty."
        ),
        "response_b": (
            "Time passes by like the seasons change,\n"
            "From spring to summer then fall and winter.\n"
            "The flowers bloom and then they fade away,\n"
            "And leaves fall down from the trees each day.\n\n"
            "The river flows and time goes on,\n"
            "Each moment here and then it's gone.\n"
            "We watch the sun rise and then set,\n"
            "These are the moments we should not forget."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 5},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "W9", "category": "writing",
        "question": "Write a press release announcing the launch of a new AI-powered customer support platform called 'ClaraDesk'.",
        "response_a": (
            "FOR IMMEDIATE RELEASE\n\n"
            "**NovaTech Launches ClaraDesk: AI-Powered Customer Support Platform That Resolves "
            "80% of Tickets Without Human Intervention**\n\n"
            "*San Francisco, CA – [Date]* — NovaTech today announced the general availability "
            "of ClaraDesk, an enterprise customer support platform powered by large language "
            "model technology. ClaraDesk resolves up to 80% of inbound support tickets "
            "autonomously, reducing average response time from 6 hours to under 3 minutes.\n\n"
            "\"Our early customers have cut support costs by 40% while achieving higher "
            "customer satisfaction scores than with human-only teams,\" said Jane Wu, CEO of "
            "NovaTech. \"ClaraDesk doesn't replace support agents — it eliminates the tedious "
            "work so they can focus on complex, high-value interactions.\"\n\n"
            "ClaraDesk integrates with Zendesk, Salesforce Service Cloud, and Intercom. "
            "A 30-day free trial is available at claradesk.com.\n\n"
            "**About NovaTech:** NovaTech builds AI infrastructure for enterprise customer "
            "experience teams. Founded in 2021, the company is backed by leading Silicon "
            "Valley investors.\n\n"
            "Media Contact: press@novatech.com"
        ),
        "response_b": (
            "NovaTech has launched a new product called ClaraDesk. It is an AI customer "
            "support platform. It can answer customer questions automatically. This will "
            "help companies save time and money on customer support.\n\n"
            "ClaraDesk works with popular support software. Companies can try it for free. "
            "NovaTech thinks this product will help a lot of businesses improve their "
            "customer service."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 2},
            "factual_accuracy": {"a": 5, "b": 4},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },

    # ─────────────────────────────────────────────────────────────────────
    # REASONING  (R1–R9)
    # ─────────────────────────────────────────────────────────────────────
    {
        "id": "R1", "category": "reasoning",
        "question": "If all Blorks are Snorps, and some Snorps are Glorps, does it necessarily follow that some Blorks are Glorps? Explain your reasoning.",
        "response_a": (
            "No, it does not necessarily follow that some Blorks are Glorps.\n\n"
            "Here is why:\n"
            "- Premise 1: All Blorks are Snorps. → Every Blork is inside the Snorps set.\n"
            "- Premise 2: Some Snorps are Glorps. → There exists an overlap between Snorps "
            "and Glorps, but we are not told which Snorps overlap.\n\n"
            "The Snorps that happen to be Glorps might be entirely non-Blork Snorps. "
            "Think of it with a Venn diagram: the Blork circle is fully inside the Snorp circle, "
            "but the Snorp-Glorp overlap could be in the region of Snorps that are not Blorks.\n\n"
            "**Counterexample:** Suppose the only Glorps that are also Snorps are "
            "'Tall Snorps,' and no Blork is tall. Then we have some Snorps that are Glorps, "
            "but zero Blorks that are Glorps.\n\n"
            "Therefore the conclusion is **not logically guaranteed** by the premises."
        ),
        "response_b": (
            "Yes, some Blorks are Glorps. Since all Blorks are Snorps, and some Snorps are "
            "Glorps, then some of those Blorks that are Snorps must also be Glorps. "
            "The logic flows from one group to the next, so the conclusion follows."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 2},
            "factual_accuracy": {"a": 5, "b": 1},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "R2", "category": "reasoning",
        "question": "A bat and a ball together cost $1.10. The bat costs $1.00 more than the ball. How much does the ball cost? Show your work.",
        "response_a": (
            "The ball costs **$0.05**.\n\n"
            "Let b = price of the ball.\n"
            "Then the bat costs b + $1.00.\n\n"
            "Total: b + (b + 1.00) = 1.10\n"
            "       2b + 1.00 = 1.10\n"
            "       2b = 0.10\n"
            "       b = 0.05\n\n"
            "**Check:** ball = $0.05, bat = $1.05, total = $1.10 ✓  "
            "Difference = $1.05 − $0.05 = $1.00 ✓\n\n"
            "The intuitive (but wrong) answer of $0.10 fails the second condition: "
            "if the ball were $0.10, the bat would be $1.10, and the total would be $1.20, not $1.10."
        ),
        "response_b": (
            "The ball costs $0.10. The bat costs $1.00. Together they cost $1.10. "
            "The bat costs $1.00 more than the ball, so the answer is $0.10 for the ball."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 2},
            "factual_accuracy": {"a": 5, "b": 1},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "R3", "category": "reasoning",
        "question": "You have three boxes: one contains only apples, one only oranges, and one a mix. All labels are wrong. You may pick one fruit from one box. How do you correctly label all three boxes?",
        "response_a": (
            "Pick one fruit from the box labeled 'Mixed.'\n\n"
            "Because **all labels are wrong**, the box labeled 'Mixed' cannot actually "
            "be the mixed box. It must be either all-apples or all-oranges.\n\n"
            "**Case:** Suppose you draw an apple from the 'Mixed' box.\n"
            "→ The 'Mixed' box is actually: **Apples only**.\n\n"
            "Now look at the box labeled 'Oranges.' It can't be oranges (label is wrong), "
            "and it can't be apples (that's taken). So it must be: **Mixed**.\n\n"
            "The remaining box, labeled 'Apples,' must therefore be: **Oranges only**.\n\n"
            "The key insight: sampling from the misidentified 'Mixed' box gives perfect "
            "information because that box has only one fruit type, and once its identity "
            "is known, the other two are forced by elimination."
        ),
        "response_b": (
            "You should pick from the mixed box and look at what fruit comes out. "
            "If it is an apple then that box has apples. Then you can look at the other "
            "boxes and guess from there. Since the labels are all wrong you need to "
            "think carefully about which box is which based on what you found."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 2},
            "factual_accuracy": {"a": 5, "b": 3},
            "coherence":        {"a": 5, "b": 2},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "R4", "category": "reasoning",
        "question": "A company's revenue grew 20% in Year 1 and then declined 20% in Year 2. Is the company's revenue the same as the starting value? Explain.",
        "response_a": (
            "No — the revenue is **lower** than the original value.\n\n"
            "Let's use a concrete example. Start with $100.\n\n"
            "Year 1: +20% → $100 × 1.20 = **$120**\n"
            "Year 2: −20% → $120 × 0.80 = **$96**\n\n"
            "The company ends up at $96, which is **4% below** the starting value.\n\n"
            "**Why?** The 20% decrease is applied to a larger base ($120), so it removes "
            "more in absolute dollars than the 20% increase added. Mathematically:\n"
            "1.20 × 0.80 = 0.96, not 1.00.\n\n"
            "This is a common cognitive bias — symmetric percentage changes are not "
            "symmetric in dollar terms. A 20% gain followed by a 20% loss always "
            "results in a net loss of (0.20)² = 4%."
        ),
        "response_b": (
            "Yes, the revenue should be the same because the company went up 20% and "
            "then down 20%, so those two changes cancel each other out and you end up "
            "back where you started."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 2},
            "factual_accuracy": {"a": 5, "b": 1},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "R5", "category": "reasoning",
        "question": "What are the strongest arguments for and against requiring mandatory voting in a democracy? Evaluate both sides.",
        "response_a": (
            "**Arguments FOR mandatory voting:**\n"
            "1. *Legitimacy:* Governments elected by 40–50% turnout represent a minority; "
            "full participation produces a mandate that reflects the genuine will of the "
            "entire citizenry.\n"
            "2. *Reduced campaign distortion:* When turnout is guaranteed, parties cannot "
            "win by suppressing opponent votes; policy platforms must appeal broadly.\n"
            "3. *Evidence from practice:* Australia has used compulsory voting since 1924 "
            "with ~95% turnout, high civic satisfaction, and no evidence of coerced outcomes.\n\n"
            "**Arguments AGAINST mandatory voting:**\n"
            "1. *Freedom of expression:* The right not to vote — or to vote informally — "
            "is itself a political statement; compulsion violates freedom of conscience.\n"
            "2. *Uninformed voters:* Forcing disengaged citizens to vote may add noise "
            "rather than signal, potentially rewarding name recognition over substance.\n"
            "3. *Enforcement burden:* Penalizing non-voters is administratively costly and "
            "disproportionately affects marginalized groups.\n\n"
            "**Assessment:** Both positions have genuine merit. The tension is ultimately "
            "between collective democratic health and individual political liberty — "
            "a values question, not an empirical one."
        ),
        "response_b": (
            "Mandatory voting would mean everyone has to vote. This could be good because "
            "more people would vote and the results would better represent the population. "
            "But it could also be bad because some people don't want to vote and forcing "
            "them might not be fair. Some countries do this and it seems to work okay. "
            "Overall there are pros and cons to mandatory voting."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 3},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "R6", "category": "reasoning",
        "question": "If you flip a fair coin 10 times and get heads every time, what is the probability of getting heads on the 11th flip? Explain the reasoning carefully.",
        "response_a": (
            "The probability is exactly **50%** (0.5).\n\n"
            "A fair coin has no memory. Each flip is an **independent event**, meaning "
            "the outcome of any past flip has zero influence on future flips. The coin "
            "does not 'know' it landed heads 10 times; it has no mechanism to compensate.\n\n"
            "The **Gambler's Fallacy** is the mistaken belief that after a streak of one "
            "outcome, the opposite is 'due.' This only applies to dependent events "
            "(e.g., drawing cards without replacement). Coin flips are independent.\n\n"
            "What IS interesting: the probability of getting 10 heads in a row beforehand "
            "is (0.5)^10 ≈ 0.1%. But *given that it already happened*, we're now simply "
            "asking about flip #11 in isolation. Conditional on the past, P(heads) = 0.5.\n\n"
            "One caveat: if the coin's fairness is in question, 10 consecutive heads is "
            "Bayesian evidence the coin may be biased — in which case P(heads on flip 11) "
            "> 0.5. But for a *known* fair coin, it's always 50%."
        ),
        "response_b": (
            "The probability is 50% because it's a fair coin. But after getting heads "
            "10 times in a row, it seems like tails is more likely now to balance things "
            "out. The coin should start to even out over many flips, so tails might be "
            "slightly more likely on the next flip to compensate for all those heads."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 2},
            "factual_accuracy": {"a": 5, "b": 2},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "R7", "category": "reasoning",
        "question": "Two trains start 300 km apart and head toward each other. Train A travels at 80 km/h; Train B at 70 km/h. A bird flies from A toward B at 150 km/h, bounces between the trains until they meet. How far does the bird fly?",
        "response_a": (
            "The bird flies **100 km**.\n\n"
            "The elegant trick: ignore the bird's back-and-forth and focus on **time**.\n\n"
            "The trains close the 300 km gap at a combined speed of 80 + 70 = **150 km/h**.\n"
            "Time until they meet: 300 ÷ 150 = **2 hours**.\n\n"
            "The bird flies the entire 2 hours at 150 km/h:\n"
            "Distance = 150 × 2 = **100 km**.\n\n"
            "*(The apparent complexity of the zig-zag is a red herring — the time is fixed "
            "regardless of the bird's path, so the distance calculation is trivial.)*"
        ),
        "response_b": (
            "This is a complicated problem. The bird keeps flying back and forth between "
            "the trains until they meet. To solve it you would need to calculate each "
            "individual segment of the bird's journey as the trains get closer and closer. "
            "This involves an infinite series. The answer would be approximately 100 km "
            "but you need to sum all the infinite legs of the journey."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 4},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "R8", "category": "reasoning",
        "question": "Evaluate this argument: 'We should not invest in solar energy because solar panels require energy to manufacture, so they will never produce more energy than they consume.'",
        "response_a": (
            "The argument is **factually incorrect** and contains a **false premise**.\n\n"
            "The claim that solar panels 'never produce more energy than they consume' "
            "is refuted by the concept of **Energy Payback Time (EPBT)** — the time a "
            "panel takes to generate the energy used in its manufacture.\n\n"
            "For modern crystalline silicon panels, EPBT is **1–4 years** depending on "
            "location and manufacturing method. Given a typical lifespan of 25–30 years, "
            "a panel produces **6–25× more energy** than was consumed to make it.\n\n"
            "The **logical error** in the argument is assuming that because energy is spent "
            "upfront, the net energy balance must be negative. This ignores the panel's "
            "multi-decade operational output — like arguing a factory is wasteful because "
            "it cost energy to build, while ignoring everything it subsequently produces.\n\n"
            "A valid concern would be: 'the transition requires upfront energy investment.' "
            "That is true but not a reason to avoid it — it is a reason to manage the "
            "transition timeline carefully."
        ),
        "response_b": (
            "This argument is not very convincing. Solar panels do use energy to make but "
            "they also produce energy once they are installed. Over time they produce more "
            "than they use. So the argument is wrong because solar panels do eventually "
            "pay back the energy used to make them. This is why solar energy is still "
            "a good investment."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 4},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "R9", "category": "reasoning",
        "question": "If you are in a room with no windows and three light switches outside control three bulbs inside, and you can only enter the room once, how do you determine which switch controls which bulb?",
        "response_a": (
            "**Solution:**\n"
            "1. Turn Switch 1 ON. Wait 5–10 minutes.\n"
            "2. Turn Switch 1 OFF. Turn Switch 2 ON.\n"
            "3. Enter the room.\n\n"
            "**Reading the room:**\n"
            "- The bulb that is **on**: controlled by Switch 2.\n"
            "- The bulb that is **off but warm**: controlled by Switch 1 (it was on, "
            "then turned off — still retains heat).\n"
            "- The bulb that is **off and cold**: controlled by Switch 3 (never turned on).\n\n"
            "This works because we use an additional dimension of information — **heat** — "
            "beyond the binary on/off state. The constraint is 'one entry,' not 'binary "
            "sensing.' Using physical properties of the bulb expands the information "
            "available within that single observation."
        ),
        "response_b": (
            "You can turn on two of the switches and leave one off. Then when you enter "
            "the room you will know which bulbs correspond to the switches that are on "
            "and the one that is off will be the third switch. But wait, this only tells "
            "you two switches, not all three. I'm not sure how to distinguish the two "
            "that are on from each other."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 2},
            "factual_accuracy": {"a": 5, "b": 3},
            "coherence":        {"a": 5, "b": 2},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },

    # ─────────────────────────────────────────────────────────────────────
    # MATH  (M1–M8)
    # ─────────────────────────────────────────────────────────────────────
    {
        "id": "M1", "category": "math",
        "question": "Solve the equation 2x² + 5x − 3 = 0. Show all steps.",
        "response_a": (
            "Using the quadratic formula: x = (−b ± √(b²−4ac)) / 2a\n"
            "with a=2, b=5, c=−3:\n\n"
            "Discriminant: b²−4ac = 25 − 4(2)(−3) = 25 + 24 = 49\n"
            "√49 = 7\n\n"
            "x = (−5 ± 7) / 4\n"
            "x₁ = (−5 + 7)/4 = 2/4 = **1/2**\n"
            "x₂ = (−5 − 7)/4 = −12/4 = **−3**\n\n"
            "**Verification:**\n"
            "x=1/2: 2(1/4)+5(1/2)−3 = 0.5+2.5−3 = 0 ✓\n"
            "x=−3: 2(9)+5(−3)−3 = 18−15−3 = 0 ✓"
        ),
        "response_b": (
            "Using the quadratic formula:\n"
            "x = (−5 ± √(25+24)) / 4 = (−5 ± √49) / 4 = (−5 ± 7) / 4\n\n"
            "x₁ = 2/4 = 0.5\n"
            "x₂ = −12/4 = −4\n\n"  # Error: −12/4 = −3, not −4
            "So the solutions are x = 0.5 and x = −4."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 2},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "M2", "category": "math",
        "question": "Find the derivative of f(x) = 3x³ − 2x² + 5x − 7 and evaluate it at x = 2.",
        "response_a": (
            "Apply the power rule term by term:\n\n"
            "f'(x) = 3·3x² − 2·2x + 5·1 − 0\n"
            "f'(x) = **9x² − 4x + 5**\n\n"
            "Evaluate at x = 2:\n"
            "f'(2) = 9(4) − 4(2) + 5 = 36 − 8 + 5 = **33**"
        ),
        "response_b": (
            "The derivative is found using the power rule:\n"
            "f'(x) = 9x² − 4x + 5\n\n"
            "At x = 2:\n"
            "f'(2) = 9(4) − 4(2) + 5 = 36 − 8 + 5 = 34"  # Arithmetic error: should be 33
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 4},
            "factual_accuracy": {"a": 5, "b": 3},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "M3", "category": "math",
        "question": "P(A) = 0.6, P(B) = 0.5, P(A∩B) = 0.3. Find P(A∪B) and state whether A and B are independent.",
        "response_a": (
            "**P(A∪B):**\n"
            "P(A∪B) = P(A) + P(B) − P(A∩B) = 0.6 + 0.5 − 0.3 = **0.8**\n\n"
            "**Independence check:**\n"
            "A and B are independent iff P(A∩B) = P(A)·P(B)\n"
            "P(A)·P(B) = 0.6 × 0.5 = 0.30\n"
            "P(A∩B) = 0.30 ✓\n\n"
            "Since P(A∩B) = P(A)·P(B), **A and B are independent**."
        ),
        "response_b": (
            "P(A∪B) = P(A) + P(B) − P(A∩B) = 0.6 + 0.5 − 0.3 = 0.8\n\n"
            "For independence, we check if P(A∩B) equals P(A) × P(B).\n"
            "P(A) × P(B) = 0.6 × 0.5 = 0.30\n"
            "This does not equal P(A∩B) = 0.3, so A and B are not independent."  # Wrong: 0.30 = 0.3
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 2},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "M4", "category": "math",
        "question": "Solve the system: 2x + 3y = 12 and x − y = 1.",
        "response_a": (
            "From equation 2: x = y + 1\n\n"
            "Substitute into equation 1:\n"
            "2(y+1) + 3y = 12\n"
            "2y + 2 + 3y = 12\n"
            "5y = 10\n"
            "y = 2\n\n"
            "Back-substitute: x = 2 + 1 = 3\n\n"
            "**Solution: x = 3, y = 2**\n\n"
            "Check: 2(3)+3(2)=6+6=12 ✓  and  3−2=1 ✓"
        ),
        "response_b": (
            "Multiply equation 2 by 2: 2x − 2y = 2\n"
            "Subtract from equation 1: (2x+3y) − (2x−2y) = 12−2\n"
            "5y = 10, so y = 2\n"
            "Then x = y + 1 = 3\n\n"
            "Solution: x = 3, y = 2"
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 5},
            "factual_accuracy": {"a": 5, "b": 5},
            "coherence":        {"a": 5, "b": 5},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",  # Slight preference for showing verification
    },
    {
        "id": "M5", "category": "math",
        "question": "You invest $5,000 at 6% annual interest compounded annually. How much will you have after 10 years?",
        "response_a": (
            "Use the compound interest formula: A = P(1 + r)^t\n\n"
            "P = 5000, r = 0.06, t = 10\n\n"
            "A = 5000 × (1.06)^10\n"
            "(1.06)^10 ≈ 1.79085\n"
            "A ≈ 5000 × 1.79085 ≈ **$8,954.24**\n\n"
            "So your investment grows by approximately $3,954 over 10 years."
        ),
        "response_b": (
            "After 10 years with 6% compound interest:\n"
            "A = 5000 × (1.06)^10\n"
            "(1.06)^10 ≈ 1.7908\n"
            "A ≈ 5000 × 1.7908 ≈ $8,854"  # Slightly off due to rounding
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 4},
            "factual_accuracy": {"a": 5, "b": 3},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "M6", "category": "math",
        "question": "Dataset: [4, 7, 2, 9, 4, 6, 4, 8, 3, 9]. Find the mean, median, and mode.",
        "response_a": (
            "**Mean:** Sum = 4+7+2+9+4+6+4+8+3+9 = 56; n = 10\n"
            "Mean = 56/10 = **5.6**\n\n"
            "**Median:** Sort: [2, 3, 4, 4, 4, 6, 7, 8, 9, 9]\n"
            "n=10 (even) → average of 5th and 6th values = (4+6)/2 = **5.0**\n\n"
            "**Mode:** 4 appears 3 times (most frequent) → Mode = **4**"
        ),
        "response_b": (
            "Sorted data: [2, 3, 4, 4, 4, 6, 7, 8, 9, 9]\n\n"
            "Mean = (2+3+4+4+4+6+7+8+9+9)/10 = 56/10 = 5.6\n"
            "Median = middle value = 4 (the 5th value)\n"  # Error: should be avg of 5th and 6th
            "Mode = 4"
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 4},
            "factual_accuracy": {"a": 5, "b": 3},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "M7", "category": "math",
        "question": "Find the area of a triangle with vertices A(0,0), B(4,0), and C(2,3).",
        "response_a": (
            "Using the coordinate formula:\n"
            "Area = ½|x_A(y_B − y_C) + x_B(y_C − y_A) + x_C(y_A − y_B)|\n"
            "= ½|0(0−3) + 4(3−0) + 2(0−0)|\n"
            "= ½|0 + 12 + 0|\n"
            "= ½ × 12 = **6 square units**\n\n"
            "Alternatively: base AB = 4 (along x-axis), height = y-coordinate of C = 3.\n"
            "Area = ½ × base × height = ½ × 4 × 3 = **6** ✓"
        ),
        "response_b": (
            "Base = distance from A to B = 4\n"
            "Height = y-coordinate of C = 3\n"
            "Area = base × height = 4 × 3 = 12"  # Missing the ½ factor
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 1},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "M8", "category": "math",
        "question": "What is the sum of the interior angles of a convex polygon with n sides? Use this to find the sum for a hexagon.",
        "response_a": (
            "The sum of interior angles of a convex n-gon is:\n"
            "**(n − 2) × 180°**\n\n"
            "**Derivation:** Any n-gon can be divided into (n−2) triangles by drawing "
            "diagonals from one vertex. Each triangle contributes 180°, giving (n−2)×180°.\n\n"
            "**For a hexagon (n = 6):**\n"
            "(6 − 2) × 180° = 4 × 180° = **720°**\n\n"
            "Each interior angle of a regular hexagon = 720°/6 = 120°."
        ),
        "response_b": (
            "The formula for interior angles is n × 180°.\n"  # Wrong formula
            "For a hexagon: 6 × 180° = 1080°."  # Wrong
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 2},
            "factual_accuracy": {"a": 5, "b": 1},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },

    # ─────────────────────────────────────────────────────────────────────
    # CODING  (C1–C9)
    # ─────────────────────────────────────────────────────────────────────
    {
        "id": "C1", "category": "coding",
        "question": "Write a Python function that returns all prime numbers up to n using the Sieve of Eratosthenes.",
        "response_a": (
            "```python\n"
            "def sieve_of_eratosthenes(n: int) -> list[int]:\n"
            "    if n < 2:\n"
            "        return []\n"
            "    is_prime = [True] * (n + 1)\n"
            "    is_prime[0] = is_prime[1] = False\n"
            "    for i in range(2, int(n**0.5) + 1):\n"
            "        if is_prime[i]:\n"
            "            for j in range(i*i, n + 1, i):\n"
            "                is_prime[j] = False\n"
            "    return [i for i, prime in enumerate(is_prime) if prime]\n"
            "```\n\n"
            "**Time complexity:** O(n log log n)  \n"
            "**Space complexity:** O(n)  \n"
            "The inner loop starts at i² (not 2i) because all smaller multiples "
            "have already been marked by previous primes."
        ),
        "response_b": (
            "```python\n"
            "def find_primes(n):\n"
            "    primes = []\n"
            "    for num in range(2, n + 1):\n"
            "        is_prime = True\n"
            "        for i in range(2, num):\n"
            "            if num % i == 0:\n"
            "                is_prime = False\n"
            "                break\n"
            "        if is_prime:\n"
            "            primes.append(num)\n"
            "    return primes\n"
            "```\n\n"
            "This function checks each number for primality and collects the primes."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 4},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "C2", "category": "coding",
        "question": "Implement a stack in Python with push, pop, peek, and is_empty methods.",
        "response_a": (
            "```python\n"
            "class Stack:\n"
            "    def __init__(self):\n"
            "        self._items: list = []\n\n"
            "    def push(self, item) -> None:\n"
            "        self._items.append(item)\n\n"
            "    def pop(self):\n"
            "        if self.is_empty():\n"
            "            raise IndexError('pop from empty stack')\n"
            "        return self._items.pop()\n\n"
            "    def peek(self):\n"
            "        if self.is_empty():\n"
            "            raise IndexError('peek at empty stack')\n"
            "        return self._items[-1]\n\n"
            "    def is_empty(self) -> bool:\n"
            "        return len(self._items) == 0\n\n"
            "    def __len__(self) -> int:\n"
            "        return len(self._items)\n"
            "```"
        ),
        "response_b": (
            "```python\n"
            "class Stack:\n"
            "    def __init__(self):\n"
            "        self.items = []\n\n"
            "    def push(self, item):\n"
            "        self.items.append(item)\n\n"
            "    def pop(self):\n"
            "        return self.items.pop()  # crashes on empty\n\n"
            "    def peek(self):\n"
            "        return self.items[-1]  # crashes on empty\n\n"
            "    def is_empty(self):\n"
            "        return self.items == []\n"
            "```"
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 4},
            "factual_accuracy": {"a": 5, "b": 4},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "C3", "category": "coding",
        "question": "Write a Python function to find two numbers in a list that sum to a given target. Return their indices. Aim for O(n) time.",
        "response_a": (
            "```python\n"
            "def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:\n"
            "    seen: dict[int, int] = {}\n"
            "    for i, num in enumerate(nums):\n"
            "        complement = target - num\n"
            "        if complement in seen:\n"
            "            return (seen[complement], i)\n"
            "        seen[num] = i\n"
            "    return None\n"
            "```\n\n"
            "**O(n) time, O(n) space.** Uses a hash map to record each value's index; "
            "for each element checks if its complement was seen earlier."
        ),
        "response_b": (
            "```python\n"
            "def two_sum(nums, target):\n"
            "    for i in range(len(nums)):\n"
            "        for j in range(i+1, len(nums)):\n"
            "            if nums[i] + nums[j] == target:\n"
            "                return [i, j]\n"
            "    return None\n"
            "```\n\n"
            "This checks every pair of numbers to find the ones that sum to the target."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 4},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "C4", "category": "coding",
        "question": "Write a Python function to check if a string is a palindrome, ignoring case and non-alphanumeric characters.",
        "response_a": (
            "```python\n"
            "import re\n\n"
            "def is_palindrome(s: str) -> bool:\n"
            "    cleaned = re.sub(r'[^a-zA-Z0-9]', '', s).lower()\n"
            "    return cleaned == cleaned[::-1]\n"
            "```\n\n"
            "Examples:\n"
            "- `is_palindrome('A man, a plan, a canal: Panama')` → `True`\n"
            "- `is_palindrome('race a car')` → `False`"
        ),
        "response_b": (
            "```python\n"
            "def is_palindrome(s):\n"
            "    s = s.lower()\n"
            "    # Remove spaces only\n"
            "    s = s.replace(' ', '')\n"
            "    return s == s[::-1]\n"
            "```\n\n"
            "This converts to lowercase and removes spaces, then checks if it reads "
            "the same forwards and backwards."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 3},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "C5", "category": "coding",
        "question": "Write a Python function that performs binary search on a sorted list and returns the index of the target, or -1 if not found.",
        "response_a": (
            "```python\n"
            "def binary_search(arr: list, target) -> int:\n"
            "    left, right = 0, len(arr) - 1\n"
            "    while left <= right:\n"
            "        mid = left + (right - left) // 2  # avoids overflow\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            left = mid + 1\n"
            "        else:\n"
            "            right = mid - 1\n"
            "    return -1\n"
            "```\n\n"
            "**O(log n) time, O(1) space.** Note: `mid = left + (right-left)//2` "
            "instead of `(left+right)//2` prevents integer overflow in languages with "
            "fixed-size integers (Python doesn't overflow, but it's good practice)."
        ),
        "response_b": (
            "```python\n"
            "def binary_search(arr, target):\n"
            "    left = 0\n"
            "    right = len(arr)\n"  # Bug: should be len(arr)-1
            "    while left < right:\n"  # Bug: should be <=
            "        mid = (left + right) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            left = mid + 1\n"
            "        else:\n"
            "            right = mid\n"
            "    return -1\n"
            "```"
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 3},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "C6", "category": "coding",
        "question": "Write a Python function to count the frequency of each word in a string (case-insensitive, ignore punctuation).",
        "response_a": (
            "```python\n"
            "import re\n"
            "from collections import Counter\n\n"
            "def word_frequency(text: str) -> dict[str, int]:\n"
            "    words = re.findall(r\"[a-zA-Z']+\", text.lower())\n"
            "    return dict(Counter(words))\n"
            "```\n\n"
            "Uses regex to extract only alphabetic tokens (preserves contractions), "
            "lowercases everything, then counts with `Counter`."
        ),
        "response_b": (
            "```python\n"
            "def word_frequency(text):\n"
            "    freq = {}\n"
            "    words = text.lower().split()\n"
            "    for word in words:\n"
            "        word = word.strip('.,!?;:')\n"
            "        if word in freq:\n"
            "            freq[word] += 1\n"
            "        else:\n"
            "            freq[word] = 1\n"
            "    return freq\n"
            "```"
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 4},
            "factual_accuracy": {"a": 5, "b": 4},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "C7", "category": "coding",
        "question": "Write a Python function to find the most frequent element in a list. If there is a tie, return any one of them.",
        "response_a": (
            "```python\n"
            "from collections import Counter\n\n"
            "def most_frequent(lst: list):\n"
            "    if not lst:\n"
            "        raise ValueError('List is empty')\n"
            "    return Counter(lst).most_common(1)[0][0]\n"
            "```\n\n"
            "One-liner using `Counter.most_common(1)`, which returns the single "
            "element with the highest count in O(n) time."
        ),
        "response_b": (
            "```python\n"
            "def most_frequent(lst):\n"
            "    max_count = 0\n"
            "    result = None\n"
            "    for item in lst:\n"
            "        count = lst.count(item)\n"  # O(n²) due to repeated .count()
            "        if count > max_count:\n"
            "            max_count = count\n"
            "            result = item\n"
            "    return result\n"
            "```"
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 3},
            "factual_accuracy": {"a": 5, "b": 4},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "C8", "category": "coding",
        "question": "Write a Python function that takes a list of integers and returns a new list with duplicates removed, preserving original order.",
        "response_a": (
            "```python\n"
            "def remove_duplicates(lst: list) -> list:\n"
            "    seen = set()\n"
            "    result = []\n"
            "    for item in lst:\n"
            "        if item not in seen:\n"
            "            seen.add(item)\n"
            "            result.append(item)\n"
            "    return result\n"
            "```\n\n"
            "**O(n) time and space.** Using a `set` for O(1) membership checks. "
            "Note: `list(dict.fromkeys(lst))` also works in Python 3.7+ since dicts "
            "preserve insertion order, but the explicit approach is clearer."
        ),
        "response_b": (
            "```python\n"
            "def remove_duplicates(lst):\n"
            "    return list(set(lst))\n"
            "```\n\n"
            "Convert to a set to remove duplicates, then back to a list."
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 2},
            "factual_accuracy": {"a": 5, "b": 3},
            "coherence":        {"a": 5, "b": 4},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
    {
        "id": "C9", "category": "coding",
        "question": "Debug this Python code: it is supposed to compute the factorial of n recursively but gives wrong results.\n\n```python\ndef factorial(n):\n    if n == 0:\n        return 0\n    return n * factorial(n - 1)\n```",
        "response_a": (
            "**Bug:** The base case returns `0` instead of `1`.\n\n"
            "When `n == 0`, factorial(0) should be **1** (by definition). "
            "Returning 0 causes the entire chain to evaluate to 0 because "
            "any number multiplied by 0 is 0.\n\n"
            "**Fixed code:**\n"
            "```python\n"
            "def factorial(n: int) -> int:\n"
            "    if n < 0:\n"
            "        raise ValueError('factorial undefined for negative numbers')\n"
            "    if n == 0:\n"
            "        return 1  # <- fix here\n"
            "    return n * factorial(n - 1)\n"
            "```\n\n"
            "Added negative-input guard for robustness."
        ),
        "response_b": (
            "The function looks mostly correct. The issue might be with how you are "
            "calling it. Make sure you are passing an integer. You could also try "
            "using a loop instead of recursion if you are getting errors.\n\n"
            "```python\n"
            "def factorial(n):\n"
            "    result = 1\n"
            "    for i in range(1, n + 1):\n"
            "        result *= i\n"
            "    return result\n"
            "```"
        ),
        "human_scores": {
            "helpfulness":      {"a": 5, "b": 2},
            "factual_accuracy": {"a": 5, "b": 3},
            "coherence":        {"a": 5, "b": 3},
            "safety":           {"a": 5, "b": 5},
        },
        "human_preference": "a",
    },
]

CATEGORIES = ["writing", "reasoning", "math", "coding"]
DIMENSIONS = ["helpfulness", "factual_accuracy", "coherence", "safety"]

def get_cases_by_category(category: str) -> list[dict]:
    return [c for c in MT_BENCH_CASES if c["category"] == category]

def get_case_by_id(case_id: str) -> dict | None:
    return next((c for c in MT_BENCH_CASES if c["id"] == case_id), None)
