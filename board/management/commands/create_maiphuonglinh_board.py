from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction

from board.models import Board, BoardMember, List, Card


TEMPLATE = {
    "board_name": "Mai Phuong Linh",
    "lists": [
        {
            "title": "GENERAL INFO",
            "cards": [
                {
                    "title": "GPA Goal (Grade 10 – Semester 2): Aim for 8.8+ / strong upward trend",
                    "desc": (
                        "Focus on consistency and exam performance.\n"
                        "Weekly routine:\n"
                        "- Review notes the same day\n"
                        "- 2 focused practice sessions per subject/week\n"
                        "- Track scores + mistakes in a simple log\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "English Goal: IELTS prep (long-term target: 7.0–7.5+)",
                    "desc": (
                        "Semester 2 (Mar–Jun): build foundation + habits.\n"
                        "Plan:\n"
                        "- Listening/Reading: 30–45 min/day (Cambridge sets + review mistakes)\n"
                        "- Speaking: 2 sessions/week (record + self-correct)\n"
                        "- Writing: 1 task/week (Task 1 or Task 2) + get feedback\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Finance Major Direction: What to explore (Grade 10–11)",
                    "desc": (
                        "Explore early so your profile looks ‘finance-shaped’ later.\n"
                        "Topics to sample:\n"
                        "- Personal finance basics (budgeting, saving, investing)\n"
                        "- Business & economics fundamentals\n"
                        "- Excel for analysis + charts\n"
                        "- Basic statistics for decision-making\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Core Skill Stack (Finance track): Excel + Math + Communication",
                    "desc": (
                        "Priority skills to build from March:\n"
                        "1) Excel: formulas, tables, charts, basic modeling\n"
                        "2) Math: algebra + functions + statistics\n"
                        "3) Communication: writing clearly, presenting ideas, teamwork\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Roadmap Overview (March start) — Semester 2 focus",
                    "desc": (
                        "Main focus (Mar–Jun 2026):\n"
                        "- Strong grades + stable study routine\n"
                        "- Start finance-themed activities\n"
                        "- Build English habit (IELTS foundation)\n"
                        "- Begin a small portfolio: mini projects + reflections\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
            ],
        },

        {
            "title": "MARCH 2026 (Grade 10 – Semester 2 Start)",
            "cards": [
                {
                    "title": "Academics: Build a weekly study system",
                    "desc": (
                        "Set your weekly plan (Mon–Sun).\n"
                        "- 5 study days + 1 light review day + 1 rest day\n"
                        "- After each class: 15-minute recap\n"
                        "- End of week: 60–90 min review + prepare next week\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "English: Start IELTS foundation routine",
                    "desc": (
                        "Weekly targets:\n"
                        "- 3 Listening sets + review mistakes\n"
                        "- 3 Reading passages + vocabulary notes\n"
                        "- 1 Writing task (Task 1 or Task 2)\n"
                        "- 1 Speaking topic recording (2–3 minutes)\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Finance Exposure: Begin personal finance journal",
                    "desc": (
                        "Create a simple journal (Google Doc/Notion):\n"
                        "- Track spending categories (even if small)\n"
                        "- Write 1 reflection/week: “What did I learn about money?”\n"
                        "- Learn: needs vs wants, saving goals, budgeting\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Extracurricular: Join/plan 1 finance-related activity",
                    "desc": (
                        "Choose ONE to start:\n"
                        "- School business/economics club\n"
                        "- Debate/public speaking (helps finance presentations)\n"
                        "- A small online course (Excel or intro economics)\n\n"
                        "Goal: show consistent participation, not “many things once.”"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Portfolio: Set up your “Finance Growth Folder”",
                    "desc": (
                        "Make folders:\n"
                        "- Notes (economics/finance)\n"
                        "- Excel mini projects\n"
                        "- Certificates\n"
                        "- Reflections (what you learned)\n\n"
                        "This will become your future application story."
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
            ],
        },

        {
            "title": "APRIL 2026 (Mid-semester momentum)",
            "cards": [
                {
                    "title": "Academics: Improve weak subjects using an error log",
                    "desc": (
                        "Pick 1–2 weakest topics.\n"
                        "For each mistake write:\n"
                        "- Why it happened\n"
                        "- The correct method\n"
                        "- A similar practice question\n\n"
                        "Review the log every weekend."
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Excel Skill: Basic formulas + charts (mini project #1)",
                    "desc": (
                        "Learn and use:\n"
                        "- SUM, AVERAGE, IF, COUNTIF, VLOOKUP/XLOOKUP (if available)\n"
                        "- Basic charts\n\n"
                        "Mini project idea:\n"
                        "- Monthly budget tracker + chart\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "English: Writing focus (clarity + structure)",
                    "desc": (
                        "Goal: 2 writing tasks this month.\n"
                        "- 1 Task 1 (report)\n"
                        "- 1 Task 2 (argument)\n\n"
                        "Checklist:\n"
                        "- Clear thesis\n"
                        "- Topic sentences\n"
                        "- Examples\n"
                        "- Strong conclusion"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Finance Reading: 2 short articles/week + summary",
                    "desc": (
                        "Pick beginner-friendly sources.\n"
                        "Each summary should include:\n"
                        "- 3 key ideas\n"
                        "- 5 new words\n"
                        "- 1 question you still have\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Extracurricular: Take a small responsibility role",
                    "desc": (
                        "Examples:\n"
                        "- Help organize a club session\n"
                        "- Create slides for a meeting\n"
                        "- Lead a 10-minute sharing segment\n\n"
                        "Leadership doesn’t need a title—show actions."
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
            ],
        },

        {
            "title": "MAY 2026 (Assessment + performance month)",
            "cards": [
                {
                    "title": "Academics: Exam preparation plan (2–3 weeks)",
                    "desc": (
                        "Break revision into:\n"
                        "1) Concepts\n"
                        "2) Practice questions\n"
                        "3) Timed practice\n\n"
                        "Use spaced repetition: revisit topics every few days."
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "English: One mini mock (Listening + Reading)",
                    "desc": (
                        "Do 1 mini mock per week:\n"
                        "- 1 Listening section\n"
                        "- 1 Reading passage set\n\n"
                        "Rule: always review errors and write what to fix."
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Excel Mini project #2: Simple savings/investment simulator",
                    "desc": (
                        "Build a sheet that shows:\n"
                        "- monthly saving amount\n"
                        "- growth over time\n"
                        "- change interest rate / contribution\n\n"
                        "Goal: understand compound growth visually."
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Extracurricular: Finance-themed event / webinar (1)",
                    "desc": (
                        "Attend 1 beginner event and write a reflection:\n"
                        "- What did you learn?\n"
                        "- What surprised you?\n"
                        "- What skill do you want to build next?"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Profile: Start a short “About Me” finance story draft",
                    "desc": (
                        "Write 150–250 words:\n"
                        "- Why finance interests you\n"
                        "- A personal experience (saving, planning, business idea)\n"
                        "- What you want to learn next\n\n"
                        "This becomes a future personal statement foundation."
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
            ],
        },

        {
            "title": "JUNE 2026 (Semester wrap-up + reset)",
            "cards": [
                {
                    "title": "Academics: Final review + improvement summary",
                    "desc": (
                        "Make a 1-page summary:\n"
                        "- Best improvements\n"
                        "- Remaining weaknesses\n"
                        "- Targets for next term\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "English: Speaking confidence week (3 recordings)",
                    "desc": (
                        "Record 3 speaking sessions:\n"
                        "- 2 minutes: personal topic\n"
                        "- 2 minutes: education/technology\n"
                        "- 2 minutes: money/finance related\n\n"
                        "Focus: fluency > perfection."
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Finance: Learn the basics of “stocks vs bonds” (notes)",
                    "desc": (
                        "Write simple notes:\n"
                        "- What each is\n"
                        "- Why people invest\n"
                        "- Risk vs return\n"
                        "- Real-life examples\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Portfolio: Organize Semester 2 evidence",
                    "desc": (
                        "Save:\n"
                        "- Best test results\n"
                        "- Excel files\n"
                        "- Reading summaries\n"
                        "- Activity proof (photos, notes, certificates)\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
            ],
        },

        {
            "title": "JULY–AUGUST 2026 (Break Projects)",
            "cards": [
                {
                    "title": "Project: Personal Finance Dashboard (Excel) — showcase piece",
                    "desc": (
                        "Build a dashboard with:\n"
                        "- Budget categories\n"
                        "- Monthly trend\n"
                        "- Saving goal progress\n"
                        "- Simple insights (what changed and why)\n\n"
                        "This is a strong finance-themed portfolio item."
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Course: Intro to Economics OR Excel for Business",
                    "desc": (
                        "Pick ONE course and finish it.\n"
                        "Deliverables:\n"
                        "- Completion certificate\n"
                        "- 1-page notes summary\n"
                        "- 3 key takeaways\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "English: Maintain habit (light but consistent)",
                    "desc": (
                        "Weekly:\n"
                        "- 2 Listening\n"
                        "- 2 Reading\n"
                        "- 1 Writing\n"
                        "- 1 Speaking\n\n"
                        "Don’t stop completely during break."
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Extracurricular: Volunteer/club contribution (finance angle if possible)",
                    "desc": (
                        "Examples:\n"
                        "- Help manage a small fundraiser budget\n"
                        "- Track donations and create a report\n"
                        "- Create posters + simple financial summary\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
            ],
        },

        {
            "title": "SEPTEMBER–DECEMBER 2026 (Next step preparation)",
            "cards": [
                {
                    "title": "Academics: Set Grade 11 Semester 1 targets",
                    "desc": (
                        "Targets should be measurable:\n"
                        "- GPA target\n"
                        "- Subject targets\n"
                        "- Weekly study hours\n"
                        "- One improvement goal per subject\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "English: Decide a realistic IELTS test window (future)",
                    "desc": (
                        "Discuss and plan:\n"
                        "- Are you ready in early Grade 11?\n"
                        "- If not, continue building to avoid rushing.\n\n"
                        "Goal: stable skills, not just test tricks."
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Finance Profile: Pick 1 focus theme",
                    "desc": (
                        "Choose ONE theme to build depth:\n"
                        "- Personal finance & budgeting\n"
                        "- Business & entrepreneurship\n"
                        "- Investing basics\n"
                        "- Data analysis for finance (Excel/Stats)\n\n"
                        "Depth beats “random activities.”"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
                {
                    "title": "Portfolio: Monthly ‘Finance Reflection’ (1 per month)",
                    "desc": (
                        "Each reflection includes:\n"
                        "- What you learned\n"
                        "- A small example/project\n"
                        "- What to improve next month\n"
                    ),
                    "tag": Card.TAG_NOT_STARTED,
                },
            ],
        },
    ],
}


class Command(BaseCommand):
    help = "Create the Mai Phuong Linh board (Grade 10 Sem 2 plan starting March 2026)."

    def add_arguments(self, parser):
        parser.add_argument("--user-id", type=int, required=True, help="User ID who will own the board")
        parser.add_argument(
            "--mentor-id",
            type=int,
            default=None,
            help="Optional mentor user ID to add as mentor member",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        try:
            owner = User.objects.get(id=options["user_id"])
        except User.DoesNotExist:
            raise CommandError("Owner user not found. Provide a valid --user-id.")

        # Create Board
        join_code = Board.generate_join_code()
        board = Board.objects.create(
            name=TEMPLATE["board_name"],
            created_by=owner,
            join_code=join_code,
        )

        # Add owner as admin
        BoardMember.objects.create(
            board=board,
            user=owner,
            role=BoardMember.ROLE_ADMIN,
        )

        # Optional mentor
        mentor_id = options.get("mentor_id")
        if mentor_id:
            try:
                mentor = User.objects.get(id=mentor_id)
                BoardMember.objects.create(
                    board=board,
                    user=mentor,
                    role=BoardMember.ROLE_MENTOR,
                )
            except User.DoesNotExist:
                raise CommandError("Mentor user not found. Provide a valid --mentor-id.")

        # Create Lists + Cards
        for li, list_data in enumerate(TEMPLATE["lists"]):
            lst = List.objects.create(
                board=board,
                title=list_data["title"],
                position=li,
            )

            for ci, card_data in enumerate(list_data["cards"]):
                Card.objects.create(
                    board=board,
                    list=lst,
                    title=card_data["title"],
                    desc=card_data.get("desc", ""),
                    tag=card_data.get("tag", Card.TAG_NOT_STARTED),
                    position=ci,
                )

        self.stdout.write(self.style.SUCCESS(
            f'Created board "{board.name}" with join code: {board.join_code}'
        ))