import re

from blog_chat.features.accounts.services import generate_guest_name


class TestGenerateGuestName:
    def test_format(self):
        name = generate_guest_name()
        assert re.fullmatch(r"[A-Z][a-z]+[A-Z][a-z]+-\d{4}", name)

    def test_uniqueness(self):
        names = {generate_guest_name() for _ in range(100)}
        assert len(names) == 100
