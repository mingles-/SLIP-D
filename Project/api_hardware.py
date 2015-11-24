from api_helper_fuctions import *

__author__ = 'mingles'


class ImOpen(Resource):
    # im open
    def get(self, lock_id):
        database_lock_id = Lock.query.filter_by(id=lock_id)
        if database_lock_id.count() > 0:

            lock = database_lock_id.first()
            if lock.requested_open is True and lock.actually_open is False: # Open is requested, Lock is closed on server, Lock is open
                lock.actually_open = True # Open the lock
                db.session.commit()
                return lock.actually_open, 202
            elif lock.requested_open is True and lock.actually_open is True: # Open is requested, Lock is open on server, Lock is open
                return lock.actually_open, 202
            elif lock.requested_open is False and lock.actually_open is True: # Close is requested, Lock is open on server, Lock is open
                return lock.actually_open, 200
            elif lock.requested_open is False and lock.actually_open is False: # Close is requested, Lock is closed on server, Lock is open
                lock.actually_open = True # Open the lock
                db.session.commit()
                return lock.actually_open, 200
        else:
            return False, 404


class ImClosed(Resource):
    # im closed
    def get(self, lock_id):
        database_lock_id = Lock.query.filter_by(id=lock_id)
        if database_lock_id.count() > 0:

            lock = database_lock_id.first()
            if lock.requested_open is False and lock.actually_open is True: # Close is requested, Lock is open on server, Lock is closed
                lock.actually_open  = False # Open the lock
                db.session.commit()
                return lock.actually_open, 202
            elif lock.requested_open is False and lock.actually_open is False: # Close is requested, Lock is closed on server, Lock is closed
                return lock.actually_open, 202
            elif lock.requested_open is True and lock.actually_open is False: # Open is requested, Lock is closed on server, Lock is closed
                return lock.actually_open, 200
            elif lock.requested_open is True and lock.actually_open is True: # Open is requested, Lock is open on server, Lock is closed
                lock.actually_open = False # Open the lock
                db.session.commit()
                return lock.actually_open, 200
        else:
            return False, 404


class Status(Resource):
    def get(self, lock_id):
        database_lock_id = Lock.query.filter_by(id=lock_id)
        if database_lock_id.count() > 0:
            state = database_lock_id.first().requested_open
            if state:
                return state, 202
            else:
                return state, 200
        else:
            return False, 404