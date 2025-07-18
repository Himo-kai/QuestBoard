"""
User API endpoints.

This module handles all user-related API operations.
"""
from flask_restx import Resource, fields, abort
from flask import request
from ...models.user import User
from .namespaces import user_ns

# Request/Response models
user_model = user_ns.model('User', {
    'id': fields.Integer(readonly=True, description='The user unique identifier'),
    'username': fields.String(required=True, description='The username'),
    'email': fields.String(required=True, description='The email address'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
    'updated_at': fields.DateTime(readonly=True, description='Last update timestamp')
})

@user_ns.route('/')
class UserList(Resource):
    """Shows a list of all users, and lets you POST to add new users"""
    
    @user_ns.doc('list_users')
    @user_ns.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        return User.query.all()
    
    @user_ns.doc('create_user')
    @user_ns.expect(user_model)
    @user_ns.marshal_with(user_model, code=201)
    def post(self):
        """Create a new user"""
        data = request.get_json()
        
        if User.query.filter_by(email=data['email']).first():
            abort(400, 'Email already registered')
            
        if User.query.filter_by(username=data['username']).first():
            abort(400, 'Username already taken')
        
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        user.save()
        
        return user, 201

@user_ns.route('/<int:id>')
@user_ns.response(404, 'User not found')
@user_ns.param('id', 'The user identifier')
class UserResource(Resource):
    """Show a single user and lets you update/delete it"""
    
    @user_ns.doc('get_user')
    @user_ns.marshal_with(user_model)
    def get(self, id):
        """Fetch a user given its identifier"""
        return User.query.get_or_404(id)
    
    @user_ns.doc('update_user')
    @user_ns.expect(user_model)
    @user_ns.marshal_with(user_model)
    def put(self, id):
        """Update a user given its identifier"""
        user = User.query.get_or_404(id)
        data = request.get_json()
        
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                abort(400, 'Email already registered')
            user.email = data['email']
            
        if 'username' in data and data['username'] != user.username:
            if User.query.filter_by(username=data['username']).first():
                abort(400, 'Username already taken')
            user.username = data['username']
            
        if 'password' in data:
            user.set_password(data['password'])
        
        user.save()
        return user
    
    @user_ns.doc('delete_user')
    @user_ns.response(204, 'User deleted')
    def delete(self, id):
        """Delete a user given its identifier"""
        user = User.query.get_or_404(id)
        user.delete()
        return '', 204
