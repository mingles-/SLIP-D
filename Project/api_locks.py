from api_helper_fuctions import *

__author__ = 'mingles'


class LockDetail(Resource):
    decorators = [requires_auth]

    @marshal_with(serialisers.lock_fields)
    def get(self, lock_id):
        """
        returns info associated with lock_id
        """
        lock = Lock.query.filter_by(id=lock_id).first()
        return lock


class LockList(Resource):
    decorators = [requires_auth]
    @marshal_with(serialisers.lock_fields)
    def get(self):
        """
        return list of user's locks
        """
        email = request.authorization.username
        user = User.query.filter_by(email=email).first()
        return list(user.locks)


    @marshal_with(serialisers.lock_fields)
    def post(self):
        """
        register lock to user
        """
        lock_name = request.form['lock_name']
        lock_id = request.form['lock_id']
        email = request.authorization.username
        # add in many to many table
        database_lock_id = Lock.query.filter_by(id=lock_id)

        if database_lock_id.count() > 0:
            return lock_id, 406
        else:
            user = User.query.filter_by(email=email).first()
            lock = Lock(id=lock_id, name=lock_name, requested_open=False, actually_open=False)

            user_lock = UserLock(user, lock, is_owner=True)

            db.session.add(lock)
            db.session.add(user_lock)
            db.session.commit()
            lock = Lock.query.filter_by(id=lock_id)
            return lock.first(), 201


class Status(Resource):
    def get(self, lock_id):
        """
        return lock status
        """
        database_lock_id = Lock.query.filter_by(id=lock_id)
        if database_lock_id.count() > 0:
            state = database_lock_id.first().requested_open
            if state:
                return state, 202
            else:
                return state, 200
        else:
            return False, 404

# @api.doc(responses={200: 'Lock Successfully Opened', 401: 'User has no permission to open lock'})
class OpenLock(Resource):
    """
    This endpoint opens the lock if lockID and associated user is consistent within the database
    """
    decorators = [requires_auth]
    @marshal_with(serialisers.lock_fields)
    def put(self, lock_id):
        """opens a Lock"""
        return change_lock_state(lock_id, True)

# @api.doc(responses={200: 'Lock Successfully Closed', 401: 'User has no permission to open lock'})
class CloseLock(Resource):
    """
    This endpoint closes the lock if lockID and associated user is consistent within the database
    """
    decorators = [requires_auth]

    @marshal_with(serialisers.lock_fields)
    def put(self, lock_id):
        """closes a lock"""
        return change_lock_state(lock_id, False)