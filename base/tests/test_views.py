import datetime
import uuid

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from unittest import skip


from base.models import Room, Event, Message, Comment, Notification, AdminNotification, Choice, Poll
# Create your tests here.

User = get_user_model()


class HomeIndexViewTests(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username='testuser1',
            password='@95lasfasfAf'
        )
        test_user2 = User.objects.create_user(
            username='testuser2',
            password='@95lasfasfAf'
        )

        test_user1.save()
        test_user2.save()

        #Create a room
        test_room1 = Room.objects.create(
            title='Test room 1',
            host=test_user1,
        )

        test_room1.admins.add(*[test_user1])
        test_room1.members.add(*[test_user1, test_user2])
        test_room1.save()

        #Create messages
        test_message1 = Message.objects.create(
            author=test_user2,
            room=test_room1,
            title='Test message 1',
            body='Test message 1 body'
        )
        test_message1.save()

        test_comment1 = Comment.objects.create(
            author=test_user1,
            message=test_message1,
            body='Test comment 1 on test message 1'
        )
        test_comment1.save()

        self.test_notification1 = Notification.objects.create(
            action_by=test_user1,
            action_to=test_user2,
            room=test_room1,
            message=test_message1
        )

        self.test_admin_notification1 = AdminNotification.objects.create(
            action_by=test_user1,
            action_to=test_user2,
            room=test_room1,
            message=test_message1
        )
        self.test_notification1.save()
        self.test_admin_notification1.save()


    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/home.html')


    def test_not_read_notification_by_false_user(self):
        login = self.client.login(username='testuser1', password='@95lasfasfAf')
        response = self.client.post(reverse('home'),
                                    {
                                        'notification_id': self.test_notification1.id,
                                        'read-notification': 'read-notification'
                                    })
        self.assertEqual(response.context['error'], 'Cannot process this request. not owner')
        self.assertTemplateUsed(response, 'base/error_page.html')
        self.assertFalse(Notification.objects.get(id=self.test_notification1.id).read_status)

    def test_read_notification_by_user(self):
        login = self.client.login(username='testuser2',
                                    password='@95lasfasfAf')
        response = self.client.post(reverse('home'),
                                    {
                                        'notification_id': self.test_notification1.id,
                                        'read-notification': 'read-notification'
                                    })
        self.assertTrue(Notification.objects.get(id=self.test_notification1.id).read_status)
        self.assertRedirects(response, reverse('home'))

    def test_deny_read_admin_notification_by_false_admin(self):
        login = self.client.login(username='testuser2',
                                    password='@95lasfasfAf')
        response = self.client.post(reverse('home'),
                                    {
                                        'admin_notification_id': self.test_admin_notification1.pk,
                                        'read-admin-notification': 'read-admin-notification'
                                    })
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.context['error'], 'Cannot process this request, not owner')
        self.assertTemplateUsed(response, 'base/error_page.html')
        self.assertFalse(AdminNotification.objects.get(id=self.test_admin_notification1.id).read_status)

    def test_read_admin_notification_by_admin(self):
        login = self.client.login(username='testuser1', password='@95lasfasfAf')
        response = self.client.post(reverse('home'),
                                        {
                                            'admin_notification_id': self.test_admin_notification1.id,
                                            'read-admin-notification': 'read-admin-notification'
                                        })
        self.assertTrue(AdminNotification.objects.get(id=self.test_admin_notification1.id).read_status)
        self.assertRedirects(response, reverse('home'))


class RoomDetailViewTests(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username='testuser1',
            password='@95lasfasfAf'
        )
        test_user2 = User.objects.create_user(
            username='testuser2',
            password='@95lasfasfAf'
        )

        self.test_user3 = User.objects.create_user(
            username='testuser3',
            password='@95lasfasfAf'
        )

        test_user1.save()
        test_user2.save()
        self.test_user3.save()

        #Create a room
        self.test_room1 = Room.objects.create(
            title='Test room 1',
            host=test_user1,
            open_status=False
        )

        self.test_room1.admins.add(test_user1)
        self.test_room1.members.add(*[test_user1, test_user2])
        self.test_room1.pending_requests.add(self.test_user3)
        self.test_room1.save()

    def test_does_not_return_view_on_non_member_request(self):
        login = self.client.login(
            username='testuser3',
            password='@95lasfasfAf'
        )

        response = self.client.get(reverse('room', kwargs={'pk': self.test_room1.id}))
        self.assertEqual(str(response.context['user']), 'testuser3')
        self.assertEqual(response.context['error'], 'Not a member of this room')
        self.assertTemplateUsed(response, 'base/error_page.html')

    def test_returns_the_correct_view_for_valid_request(self):
        login = self.client.login(
            username='testuser2',
            password='@95lasfasfAf'
        )
        response = self.client.get(reverse('room', kwargs={'pk': self.test_room1.id}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertTemplateUsed(response, 'base/room.html')

    def test_does_not_accept_or_reject_pending_by_non_admin(self):
        login = self.client.login(
            username='testuser2',
            password='@95lasfasfAf'
        )
        response = self.client.post(reverse('room', kwargs={'pk': self.test_room1.id}),
                                    {
                                        'action': 'accept',
                                        'user': self.test_user3.id
                                    })
        self.assertEqual(response.context['error'], 'Not an admin of this room')
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertTemplateUsed(response, 'base/error_page.html')

    def test_accept_pending_request_to_join_room(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )
        response = self.client.post(reverse('room', kwargs={'pk': self.test_room1.id}),
                                    {
                                        'action': 'accept',
                                        'user': self.test_user3.id
                                    })

        self.assertEqual(len(self.test_room1.pending_requests.all()), 0)
        self.assertEqual(len(self.test_room1.members.all()), 3)
        self.assertRedirects(response, reverse('room', kwargs={'pk': self.test_room1.id}))

    def test_reject_pending_request_to_join_room(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )
        response = self.client.post(reverse('room', kwargs={'pk': self.test_room1.id}),
                                    {
                                        'action': 'reject',
                                        'user': self.test_user3.id
                                    })
        self.assertEqual(len(self.test_room1.pending_requests.all()), 0)
        self.assertRedirects(response, reverse('room', kwargs={'pk': self.test_room1.id}))



class JoinRoomViewTests(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(
            username='testuser1',
            password='@95lasfasfAf'
        )
        test_user2 = User.objects.create_user(
            username='testuser2',
            password='@95lasfasfAf'
        )
        self.test_user3 = User.objects.create_user(
            username='testuser3',
            password='@95lasfasfAf'
        )

        test_user1.save()
        test_user2.save()
        self.test_user3.save()

        #Create a room
        self.test_room1 = Room.objects.create(
            title='Test room 1',
            host=test_user1,
        )

        self.test_room1.admins.add(*[test_user1])
        self.test_room1.members.add(*[test_user1, test_user2])

        self.test_room2 = Room.objects.create(
            title='Test room 2',
            host=test_user1,
            open_status=False
        )

        self.test_room2.admins.set([test_user1])
        self.test_room2.members.set([test_user1, test_user2])

        self.test_room1.save()
        self.test_room2.save()

    def test_join_room_with_existing_member(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )

        response = self.client.post(reverse('join-room', kwargs={'pk': self.test_room1.id}))
        self.assertRedirects(response, reverse('home'))


    def test_correct_redirect_on_valid_request(self):
        login = self.client.login(
            username='testuser3',
            password='@95lasfasfAf'
        )

        response = self.client.post(reverse('join-room', kwargs={'pk': self.test_room1.id}))
        self.assertIn(self.test_user3, self.test_room1.members.all())
        self.assertRedirects(response, reverse('room', kwargs={'pk': self.test_room1.id}))


    def test_add_user_to_pending_in_closed_room(self):
        login = self.client.login(
            username='testuser3',
            password='@95lasfasfAf'
        )
        response = self.client.post(reverse('join-room', kwargs={'pk': self.test_room2.id}))
        self.assertIn(self.test_user3, self.test_room2.pending_requests.all())
        self.assertNotIn(self.test_user3, self.test_room2.members.all())
        self.assertRedirects(response, reverse('home'))


class DeleteRoomViewTests(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username='testuser1',
            password='@95lasfasfAf'
        )
        test_user2 = User.objects.create_user(
            username='testuser2',
            password='@95lasfasfAf'
        )

        test_user1.save()
        test_user2.save()

        self.test_room1 = Room.objects.create(
            title='Test room 1',
            host=test_user1,
        )

        self.test_room1.admins.add(*[test_user1])
        self.test_room1.members.add(*[test_user1, test_user2])
        self.test_room1.save()


    def test_not_allow_room_delete_from_non_host(self):
        login = self.client.login(
            username='testuser2',
            password='@95lasfasfAf'
        )
        response = self.client.post(reverse('delete-room', kwargs={'pk': self.test_room1.id}))
        self.assertEqual(response.context['error'], 'Not host of this room')
        self.assertTemplateUsed(response, 'base/error_page.html')

    def test_allow_delete_of_room_by_host(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )
        response = self.client.post(reverse('delete-room', kwargs={'pk': self.test_room1.id}))
        self.assertEqual(Room.objects.all().count(), 0)
        self.assertRedirects(response, reverse('home'))


class UserProfileViewTests(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username='testuser1',
            password='@95lasfasfAf'
        )
        self.test_user2 = User.objects.create_user(
            username='testuser2',
            password='@95lasfasfAf'
        )

        test_user1.save()
        self.test_user2.save()

        self.test_room1 = Room.objects.create(
            title='Test room 1',
            host=test_user1,
        )

        self.test_room1.admins.add(*[test_user1])
        self.test_room1.members.add(*[test_user1, self.test_user2])
        self.test_room1.save()


    def test_check_that_all_users_rooms_are_returned(self):
        login = self.client.login(
            username='testuser2',
            password='@95lasfasfAf'
        )
        response = self.client.get(reverse('user-profile', kwargs={'pk': self.test_user2.id}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertIn(self.test_room1, response.context['rooms'])
        self.assertEqual(response.context['rooms'].count(), 1)

    def test_check_returns_correct_template(self):
        login = self.client.login(
            username='testuser2',
            password='@95lasfasfAf'
        )
        response = self.client.get(reverse('user-profile', kwargs={'pk': self.test_user2.id}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertTemplateUsed(response, 'base/profile.html')


class MessageDetailViewTests(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username='testuser1',
            password='@95lasfasfAf'
        )
        self.test_user2 = User.objects.create_user(
            username='testuser2',
            password='@95lasfasfAf'
        )

        test_user3 = User.objects.create_user(
            username='testuser3',
            password='@95lasfasfAf'
        )

        test_user1.save()
        self.test_user2.save()
        test_user3.save()

        test_room1 = Room.objects.create(
            title='Test room 1',
            host=test_user1,
        )

        test_room1.admins.set([test_user1])
        test_room1.members.set([test_user1, self.test_user2])
        test_room1.save()

        self.test_message1 = Message.objects.create(
            author=test_user1,
            room=test_room1,
            title='Test message 1',
            body='Body of test message 1'
        )
        self.test_message1.save()

        self.test_comment1 = Comment.objects.create(
            author=self.test_user2,
            message=self.test_message1,
            body='Test comment 1',
        )
        self.test_comment1.save()


    def test_does_not_allow_non_member_to_read_message(self):
        login = self.client.login(
            username='testuser3',
            password='@95lasfasfAf'
        )

        response = self.client.get(reverse('message', kwargs={'pk': self.test_message1.id}))
        self.assertEqual(str(response.context['user']), 'testuser3')
        self.assertTemplateUsed(response, 'base/error_page.html')
        self.assertEqual(response.context['error'], 'Not a member of this room')


    def test_allows_member_to_read_message(self):
        login = self.client.login(
            username='testuser2',
            password='@95lasfasfAf'
        )
        response = self.client.get(reverse('message', kwargs={'pk': self.test_message1.id}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.context['message'], self.test_message1)
        self.assertIn(self.test_comment1, response.context['comments'])



    def test_comment_operation_is_properly_submitted(self):
        login = self.client.login(
            username='testuser2',
            password='@95lasfasfAf'
        )
        response = self.client.post(reverse('message', kwargs={'pk': self.test_message1.id}),
                                    {
                                        'comment_submit': 'comment_submit',
                                        'body': 'test comment'
                                    })
        self.assertRedirects(response, reverse('room', kwargs={'pk': self.test_message1.room.id}))
        self.assertEqual(self.test_message1.comment_set.all().count(), 2)


    def test_like_operation_is_properly_submitted(self):
        login = self.client.login(
            username='testuser2',
            password='@95lasfasfAf'
        )
        response = self.client.post(reverse('message', kwargs={'pk': self.test_message1.id}),
                                    {
                                        'like_submit': 'like_submit'
                                    })
        self.assertEqual(self.test_message1.likes.all().count(), 1)
        self.assertIn(self.test_user2, self.test_message1.likes.all())
        self.assertRedirects(response, reverse('room', kwargs={'pk': self.test_message1.room.id}))


    def test_correct_template_is_returned(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )
        response = self.client.get(reverse('message', kwargs={'pk': self.test_message1.id}))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertTemplateUsed(response, 'base/message.html')


class CreateMessageViewTests(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username='testuser1',
            password='@95lasfasfAf'
        )
        test_user2 = User.objects.create_user(
            username='testuser2',
            password='@95lasfasfAf'
        )

        test_user3 = User.objects.create_user(
            username='testuser3',
            password='@95lasfasfAf'
        )

        test_user1.save()
        test_user2.save()
        test_user3.save()

        self.test_room1 = Room.objects.create(
            title='Test room 1',
            host=test_user1
        )
        self.test_room1.admins.add(*[test_user1])
        self.test_room1.members.add(*[test_user1, test_user2])
        self.test_room1.suspended_members.add(*[test_user2])
        self.test_room1.save()

    def test_not_allow_non_member_to_create_message(self):
        login = self.client.login(
            username='testuser3',
            password='@95lasfasfAf'
        )

        response = self.client.get(reverse('create-message', kwargs={'pk': self.test_room1.id}))
        self.assertEqual(str(response.context['user']), 'testuser3')
        self.assertEqual(response.context['error'], 'Not a member of this room')
        self.assertTemplateUsed(response, 'base/error_page.html')
    def test_not_allow_suspended_member_to_create_message(self):
        login = self.client.login(
            username='testuser2',
            password='@95lasfasfAf'
        )

        response = self.client.get(reverse('create-message', kwargs={'pk': self.test_room1.id}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.context['error'], 'Cannot make request, Suspended')
        self.assertTemplateUsed(response, 'base/error_page.html')

    def test_check_template_is_valid(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )

        response = self.client.get(reverse('create-message', kwargs={'pk': self.test_room1.id}))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertTemplateUsed(response, 'base/create_message.html')

    def test_allow_non_suspended_member_to_create_message(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )

        response = self.client.post(reverse('create-message', kwargs={'pk': self.test_room1.id}),
                                    {
                                        'title': 'Test message title',
                                        'body': 'Test message body'
                                    })
        self.assertRedirects(response, reverse('message', kwargs={'pk': 1}))
        self.assertEqual(self.test_room1.message_set.count(), 1)


class PollDetailViewTests(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username='testuser1',
            password='@95lasfasfAf'
        )
        test_user2 = User.objects.create_user(
            username='testuser2',
            password='@95lasfasfAf'
        )

        test_user3 = User.objects.create_user(
            username='testuser3',
            password='@95lasfasfAf'
        )

        test_user1.save()
        test_user2.save()
        test_user3.save()

        test_room1 = Room.objects.create(
            title='Test room 1',
            host=test_user1,
        )
        test_room1.admins.add(*[test_user1])
        test_room1.members.add(*[test_user1, test_user2])
        test_room1.suspended_members.add(*[test_user2])
        test_room1.save()

        self.test_poll1 = Poll.objects.create(
            question='Test poll 1',
            room=test_room1,
            created_by=test_user1,
            starts_at=timezone.now(),
            expires_at=datetime.timedelta(days=1) + timezone.now()
        )

        self.test_poll2 = Poll.objects.create(
            question='Test poll 2',
            room=test_room1,
            created_by=test_user1,
            starts_at=timezone.now(),
            expires_at=datetime.timedelta(days=1) + timezone.now(),
        )
        self.test_poll2.voted_users.add(*[test_user2])
        self.test_poll1.save()
        self.test_poll2.save()

        test_choice1 = Choice.objects.create(
            text='Test choice 1 for poll1',
            poll=self.test_poll1,
        )
        test_choice2 = Choice.objects.create(
            text='Test choice 2 for poll2',
            poll=self.test_poll2,
        )

        test_choice1.save()
        test_choice2.save()

    def test_deny_unauthorized_user_from_poll(self):
        login = self.client.login(
            username='testuser3',
            password='@95lasfasfAf'
        )
        response = self.client.get(reverse('poll', kwargs={'pk': self.test_poll1.id}))
        self.assertEqual(str(response.context['user']), 'testuser3')
        self.assertEqual(response.context['error'], 'Not a member of this polls room')
        self.assertTemplateUsed(response, 'base/error_page.html')

    @skip('Not passed in vote form values')
    def test_allow_authorized_user_to_vote_poll(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )
        response = self.client.post(reverse('poll', kwargs={'pk': self.test_poll1.id}))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        #TODO: Implement passing choice into the request and assert for it

    @skip('Not passed in vote form values')
    def test_redirects_to_correct_url_after_voting(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )
        #TODO: Implement passing choice into the request and assert
        response = self.client.post(reverse('poll', kwargs={'pk': self.test_poll1.id}),{})
        self.assertEqual(str(response.context['user']), 'testuser1')

    @skip('Not passed in vote form values')
    def test_does_not_allow_already_voted_user_to_vote(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )
        response = self.client.post(reverse('poll', kwargs={'pk': self.test_poll2.id}),{})
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.context['error_message'], 'You already voted on this poll')

    def test_renders_correct_template_for_authorized_user(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )
        response = self.client.get(reverse('poll', kwargs={'pk': self.test_poll2.id}))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertTemplateUsed(response, 'base/poll.html')

@skip('Done')
class CreatePollViewTests(TestCase):

    def setUp(self):
        pass

    def test_deny_non_admin_from_creating_poll(self):
        pass

    def test_render_correct_template_for_authorized_user(self):
        pass

    def test_deny_incorrect_date_setting(self):
        pass

    def test_create_poll_with_correct_datetime_setting(self):
        pass


class EventDetailViewTests(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username='testuser1',
            password='@95lasfasfAf'
        )
        self.test_user2 = User.objects.create_user(
            username='testuser2',
            password='@95lasfasfAf'
        )

        test_user3 = User.objects.create_user(
            username='testuser3',
            password='@95lasfasfAf'
        )

        test_user1.save()
        self.test_user2.save()
        test_user3.save()

        #Create a room
        test_room1 = Room.objects.create(
            title='Test room 1',
            host=test_user1,
        )

        test_room1.admins.add(*[test_user1])
        test_room1.members.add(*[test_user1, self.test_user2])


        self.test_event1 = Event.objects.create(
            title='Test event 1',
            created_by=test_user1,
            room=test_room1,
            starts_at=datetime.timedelta(days=1) + timezone.now(),
            expires_at=datetime.timedelta(days=2) + timezone.now()
        )

        self.test_event2 = Event.objects.create(
            title='Test event 2',
            created_by=test_user1,
            room=test_room1,
            starts_at=datetime.timedelta(days=-2) + timezone.now(),
            expires_at=datetime.timedelta(days=-1) + timezone.now()
        )

        self.test_event1.accepted.add(*[test_user1])
        self.test_event1.save()
        self.test_event2.save()
    def test_deny_non_member_request(self):
        login = self.client.login(
            username='testuser3',
            password='@95lasfasfAf')

        response = self.client.get(reverse('room', kwargs={'pk': self.test_event1.id}))
        self.assertEqual(str(response.context['user']), 'testuser3')
        self.assertEqual(response.context['error'], 'Not a member of this room')
        self.assertTemplateUsed(response, 'base/error_page.html')

    def test_check_event_has_ended(self):
        login = self.client.login(
            username='testuser2',
            password='@95lasfasfAf')
        response = self.client.post(reverse('event', kwargs={'pk': self.test_event2.id}), {
            'rejected': 'rejected'
        })
        self.assertEqual(response.context['error_message'], 'Event ended')
        self.assertTemplateUsed(response, 'base/event.html')

    def test_deny_request_from_already_accepted_or_rejected_member(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf')
        response = self.client.post(reverse('event', kwargs={'pk': self.test_event1.id}), {
            'rejected': 'rejected'
        })
        self.assertEqual(response.context['error_message'], 'You already accepted or rejected this event')
        self.assertTemplateUsed(response, 'base/event.html')
    def test_accept_event_from_room_member(self):
        login = self.client.login(
            username='testuser2',
            password='@95lasfasfAf')

        response = self.client.post(reverse('event', kwargs={
            'pk': self.test_event1.id}), {
            'accepted': 'accepted'
        })
        self.assertIn(self.test_user2, self.test_event1.accepted.all())
        self.assertNotIn(self.test_user2, self.test_event1.rejected.all())
        self.assertRedirects(response, reverse('event', kwargs={'pk': self.test_event1.room.id}))
    def test_reject_event_from_room_member(self):
        login = self.client.login(
            username='testuser2',
            password='@95lasfasfAf')

        response = self.client.post(reverse('event', kwargs={
            'pk': self.test_event1.id}), {
                'rejected': 'rejected'
            })
        self.assertIn(self.test_user2, self.test_event1.rejected.all())
        self.assertNotIn(self.test_user2, self.test_event1.accepted.all())
        self.assertRedirects(response, reverse('event', kwargs={'pk': self.test_event1.room.id}))


class CreateEventViewTests(TestCase):
    def setUp(self):
        self.test_user1 = User.objects.create_user(
            username='testuser1',
            password='@95lasfasfAf'
        )
        self.test_user2 = User.objects.create_user(
            username='testuser2',
            password='@95lasfasfAf'
        )

        test_user3 = User.objects.create_user(
            username='testuser3',
            password='@95lasfasfAf'
        )

        self.test_user1.save()
        self.test_user2.save()
        test_user3.save()

        #Create a room
        self.test_room1 = Room.objects.create(
            title='Test room 1',
            host=self.test_user1,
        )

        self.test_room1.admins.add(*[self.test_user1])
        self.test_room1.members.add(*[self.test_user1, self.test_user2])

    def test_deny_non_admin_request(self):
        login = self.client.login(
            username='testuser2',
            password='@95lasfasfAf'
        )

        response = self.client.get(reverse('create-event', kwargs={'pk': self.test_room1.id}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.context['error'], 'Not an admin of this room')
        self.assertTemplateUsed(response, 'base/error_page.html')

    def test_correct_template_is_returned_valid_request(self):
        login = self
    @skip('not done')
    def test_deny_post_request_with_invalid_datetime(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )

        response = self.client.post(reverse('create-event', kwargs={'pk': self.test_room1.id}),
                                    {
                                        'starts_at': timezone.now(),
                                        'expires_at': timezone.now() - datetime.timedelta(days=2),
                                        'title': 'Test invalid event'
                                    })
        self.assertEqual(response.context['error'], 'Invalid datetime settings')
        self.assertTemplateUsed(response, 'base/error_page.html')
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )

        response = self.client.get(reverse('create-event', kwargs={'pk': self.test_room1.id}))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertTemplateUsed(response, 'base/event_form.html')
    @skip('not done')
    def test_create_new_event_with_valid_datetime(self):
        login = self.client.login(
            username='testuser1',
            password='@95lasfasfAf'
        )
        response = self.client.post(reverse('create-event', kwargs={'pk': self.test_room1.id}),
                                    {
                                        'starts_at': datetime.timedelta(days=1) + timezone.now(),
                                        'expires_at': datetime.timedelta(days=2) + timezone.now(),
                                        'title': 'Test valid event'
                                    })
        self.assertEqual(self.test_room1.events_set().count(), 1)
        self.assertRedirects(response, reverse('event', kwargs={'pk': 1}))

