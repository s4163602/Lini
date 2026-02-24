from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction

from board.models import Board, BoardMember, List, Card


TEMPLATE = {
    "board_name": "Mai Phuong Linh",
    "lists": [
        {
            "title": "March 2026",
            "cards": [
                {
                    "title": "GPA",
                    "desc": (
                        "Focus: Build study system.\n"
                        "- Daily review after class (15–20 min)\n"
                        "- 2 practice sessions per subject/week\n"
                        "- Start error log\n"
                        "- Weekly review every Sunday\n"
                    ),
                },
                {
                    "title": "IELTS",
                    "desc": (
                        "Focus: Foundation.\n"
                        "- 3 Listening + 3 Reading/week\n"
                        "- 1 Writing task/week\n"
                        "- 2 Speaking recordings/week\n"
                        "- Start vocabulary notebook\n"
                    ),
                },
                {
                    "title": "SAT",
                    "desc": (
                        "Focus: Basics.\n"
                        "- Learn SAT format\n"
                        "- Start Math fundamentals\n"
                        "- Daily short reading practice\n"
                        "- Build vocabulary\n"
                    ),
                },
                {
                    "title": "Finance Extracurriculars",
                    "desc": (
                        "Focus: Exploration.\n"
                        "- Join business/economics club\n"
                        "- Start personal finance journal\n"
                        "- Learn basic money concepts\n"
                    ),
                },
            ],
        },

        {
            "title": "April 2026",
            "cards": [
                {
                    "title": "GPA",
                    "desc": (
                        "Focus: Improve weak subjects.\n"
                        "- Use error log\n"
                        "- Focus on hardest topics\n"
                        "- Practice exam-style questions\n"
                        "- Track progress weekly\n"
                    ),
                },
                {
                    "title": "IELTS",
                    "desc": (
                        "Focus: Improvement.\n"
                        "- 2 Writing tasks/week\n"
                        "- Improve structure + clarity\n"
                        "- Expand vocabulary\n"
                        "- Continue speaking practice\n"
                    ),
                },
                {
                    "title": "SAT",
                    "desc": (
                        "Focus: Skill building.\n"
                        "- Math problem solving\n"
                        "- Reading strategies\n"
                        "- Start timed practice\n"
                        "- Identify weak areas\n"
                    ),
                },
                {
                    "title": "Finance Extracurriculars",
                    "desc": (
                        "Focus: Skill building.\n"
                        "- Learn Excel basics\n"
                        "- Create budget spreadsheet\n"
                        "- Read 2 finance articles/week\n"
                    ),
                },
            ],
        },

        {
            "title": "May 2026",
            "cards": [
                {
                    "title": "GPA",
                    "desc": (
                        "Focus: Exam preparation.\n"
                        "- Full revision plan\n"
                        "- Timed practice\n"
                        "- Review mistakes carefully\n"
                        "- Aim highest scores\n"
                    ),
                },
                {
                    "title": "IELTS",
                    "desc": (
                        "Focus: Test practice.\n"
                        "- Weekly mini mock tests\n"
                        "- Improve timing\n"
                        "- Focus weak skills\n"
                        "- Maintain consistency\n"
                    ),
                },
                {
                    "title": "SAT",
                    "desc": (
                        "Focus: Speed + accuracy.\n"
                        "- Weekly mini tests\n"
                        "- Improve timing\n"
                        "- Fix weak topics\n"
                        "- Review all mistakes\n"
                    ),
                },
                {
                    "title": "Finance Extracurriculars",
                    "desc": (
                        "Focus: Experience.\n"
                        "- Join 1 competition/event\n"
                        "- Do a small finance project\n"
                        "- Write learning reflection\n"
                    ),
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