from api_helper_fuctions import *

__author__ = 'mingles'


class FriendList(Resource):
    decorators = [requires_auth]

    @marshal_with(serialisers.user_fields)
    def post(self):

        friend_id = int(request.form['friend_id'])
        email = request.authorization.username
        user_id = User.query.filter_by(email=email).first().id

        existing_friend = Friend.query.filter_by(id=user_id, friend_id=friend_id)
        friend_user_row = User.query.filter_by(id=friend_id).first()

        if (not existing_friend.count() > 0) and friend_id != user_id:

            friendship = Friend(id=user_id, friend_id=friend_id)

            db.session.add(friendship)
            db.session.commit()

            return add_is_friend(friend_user_row, request), 201

        else:

            return add_is_friend(friend_user_row, request), 401




    @marshal_with(serialisers.user_fields_with_locks)
    def get(self):

        email = request.authorization.username
        user_id = User.query.filter_by(email=email).first().id

        users = self.get_users_friends(user_id)
        users = add_related_locks(users, request)
        users = add_is_friend(users, request)

        return users, 200

    @marshal_with(serialisers.user_fields)
    def delete(self):

        email = request.authorization.username
        user_id = User.query.filter_by(email=email).first().id
        friend_id = int(request.args['friend_id'])
        existing_friend = Friend.query.filter_by(id=user_id, friend_id=friend_id)

        if existing_friend.count() > 0:

            user_locks = UserLock.query.filter_by(user_id=user_id, is_owner=True).all()

            for user_lock in user_locks:
                db.session.query(UserLock).filter(UserLock.user_id == friend_id, UserLock.lock_id == user_lock.lock_id).delete()
                db.session.commit()

            db.session.query(Friend).filter(Friend.id == user_id,
                                                   Friend.friend_id == friend_id).delete()
            db.session.commit()

            return add_is_friend(self.get_users_friends(user_id), request), 200

        else:
            # deleting friendship with an id which isn't a friend
            return self.get_users_friends(user_id), 401

    @staticmethod
    def get_users_friends(user_id):
        friend_ids = Friend.query.filter_by(id=user_id)
        friend_user_rows = []
        for friend_id in friend_ids:
            friend_user_rows.append(User.query.filter_by(id=friend_id.friend_id).first())

        return friend_user_rows


class FriendLocks(Resource):
    decorators = [requires_auth]

    # add a friend to one of your locks
    def post(self):
        friend_id = request.form['friend_id']
        lock_id = request.form['lock_id']
        user_id = get_user_id()

        are_friends = Friend.query.filter_by(id=user_id, friend_id=friend_id).count() > 0

        lock_exists = UserLock.query.filter_by(user_id=user_id, lock_id=lock_id)
        if lock_exists.count() > 0:
            user_owns_lock = lock_exists.first().is_owner
        else:
            user_owns_lock = False

        if are_friends is True and user_owns_lock is True:
            user = User.query.filter_by(id=friend_id).first()
            lock = Lock.query.filter_by(id=lock_id).first()
            user_lock = UserLock(user, lock, is_owner=False)
            db.session.add(user_lock)
            db.session.commit()
            return True, 201
        else:
            return False, 400

    def delete(self):
        friend_id = request.args['friend_id']
        lock_id = request.args['lock_id']
        user_id = get_user_id()

        lock_exists = UserLock.query.filter_by(user_id=user_id, lock_id=lock_id)
        if lock_exists.count() > 0:
            user_owns_lock = lock_exists.first().is_owner
        else:
            user_owns_lock = False

        friend_assigned_to_lock = UserLock.query.filter_by(user_id=friend_id, lock_id=lock_id, is_owner=False).count() > 0

        if friend_assigned_to_lock and user_owns_lock:

            db.session.query(UserLock).filter(UserLock.user_id == friend_id, UserLock.lock_id == lock_id).delete()
            db.session.commit()

            return True, 200
        else:
            return False, 401

