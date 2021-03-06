from django.test import TestCase
from votee import crypto, models


class VoteeTests(TestCase):
    def test_1(self) -> None:
        e = models.Election.objects.create(
            name="Test",
            slug="tæst",
        )
        admin_key = e.get_admin_key()
        assert e.validate_admin_key(admin_key)
        assert not e.validate_admin_key("abc")
        assert not e.validate_admin_key("0123456789012345678912")
        assert (
            crypto.urldecode(crypto.urlencode(b"0123456789abcdef"))
            == b"0123456789abcdef"
        )

        poll = models.Poll.objects.create(
            election=e,
            name="Test poll",
            slug="test-poll",
        )
        (
            b0,
            b1,
            b2,
        ) = poll.get_ballots(0, 3)
        r0 = poll.validate_ballot(b0)
        assert r0 is None, r0
        assert poll.validate_ballot(b1) is None
        poll.number_of_ballots = 1
        assert poll.validate_ballot(b0) == 0
        assert poll.validate_ballot(b1) is None
        poll.number_of_ballots = 2
        assert poll.validate_ballot(b0) == 0
        assert poll.validate_ballot(b1) == 1
        assert poll.validate_ballot(b2) is None

        blank = models.PollOption.objects.create(
            poll=poll,
            name="(blank)",
        )
        opt1 = models.PollOption.objects.create(
            poll=poll,
            name="Potatoes",
        )
        opt2 = models.PollOption.objects.create(
            poll=poll,
            name="Carrots",
        )

        assert models.use_ballot(poll, 0, [opt1])
        assert not models.use_ballot(poll, 0, [opt1])
        assert models.PollOption.objects.get(id=opt1.id).count == 1
        assert models.use_ballot(poll, 1, [opt1, opt2])
        assert not models.use_ballot(poll, 1, [opt1])
        assert models.PollOption.objects.get(id=opt1.id).count == 2
        assert models.PollOption.objects.get(id=opt2.id).count == 1
        assert models.use_ballot(poll, 2, [blank, blank])
        assert models.PollOption.objects.get(id=blank.id).count == 2
