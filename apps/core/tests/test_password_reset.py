import pytest


@pytest.mark.django_db
class TestPasswordResetViews:
    @pytest.mark.parametrize(['flavor'], [('libushe',), ('pythia',), ('foobar',)])
    def test_start_password_reset(self, settings, flavor, mailoutbox, admin_user, client):
        resp = client.post('/api/rest-auth/password/reset/', {'email': admin_user.email})
        assert resp.status_code == 200
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        assert flavor in mail.subject.lower(), f'flavor "{flavor}" should appear in subject'
        assert flavor in mail.body.lower(), f'flavor "{flavor}" should appear in email body'
