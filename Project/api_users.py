from api_helper_fuctions import *

__author__ = 'mingles'

class UserList(Resource):
    @requires_auth
    @marshal_with(serialisers.user_fields)
    def get(self):
        """
        return list of users
        """
        users = db.session.query(User)

        # optionally allow the user list to be filter by lock id
        lock_id = request.args.get('lock_id')
        if lock_id:
            users = users.filter(User.locks.any(id=lock_id))

        users = add_is_friend(users.all(), request)

        return users, 200


    @marshal_with(serialisers.user_fields)
    def post(self):
        """
        register user
        """
        email = request.form['email']
        password = encrypt_password(request.form['password'])
        first_name = "" + request.form['first_name']
        last_name = "" + request.form['last_name']

        if not is_user_in_db(email):
            user_datastore.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
            db.session.commit()
            new_user = User.query.filter_by(email=email).first()
            return new_user, 201

        return User.query.filter_by(email=email).first(), 406


class UserDetail(Resource):
    decorators = [requires_auth]
    @marshal_with(serialisers.user_fields_with_locks)
    def get(self, user_id):
        """
        return user information
        """
        user_exists = db.session.query(exists().where(User.id == user_id)).scalar()
        user = User.query.filter_by(id=user_id).first()
        if user_exists:
            user = add_related_locks(user, request)
            user = add_is_friend(user, request)
            return user, 200
        else:
            return user_id, 404


class Me(Resource):
    decorators = [requires_auth]
    @marshal_with(serialisers.user_fields)
    def get(self):
        """
        return self information
        """
        email = request.authorization.username
        user_exists = User.query.filter_by(email=email)
        if user_exists > 0:
            return add_is_friend(user_exists.first(), request), 200
        else:
            return email, 404
