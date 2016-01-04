from api_helper_fuctions import *

__author__ = 'mingles'


class FriendList(Resource):
    decorators = [requires_auth]

    @marshal_with(serialisers.user_fields)
    def post(self):
        """
        register friend
        """
        friend_id = int(request.form['friend_id'])
        email = request.authorization.username
        user_id = User.query.filter_by(email=email).first().id

        existing_friend = Friend.query.filter_by(id=user_id, friend_id=friend_id)
        friend_user_row = User.query.filter_by(id=friend_id).first()

        if (not existing_friend.count() > 0) and friend_id != user_id:

            friendship = Friend(id=user_id, friend_id=friend_id)

            db.session.add(friendship)
            db.session.commit()

            return friend_user_row, 201

        else:

            return friend_user_row, 401


    @marshal_with(serialisers.user_fields_with_locks)
    def get(self):
        """
        return list of friends with access to user's locks
        """
        email = request.authorization.username
        user_id = User.query.filter_by(email=email).first().id

        users = self.get_users_friends(user_id)
        users = add_related_locks(users, request)

        return users, 200

    @marshal_with(serialisers.user_fields)
    def delete(self):
        """
        delete friend
        """
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

            return self.get_users_friends(user_id), 200

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

    def post(self):
        """
        register friend to a lock
        """
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
        """
        delete friend access to lock
        """
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

