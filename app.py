#!/usr/bin/env python3

from flask import Flask, request, session, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class ClearSession(Resource):
    def delete(self):
        session['page_views'] = 0
        session['user_id'] = None
        return {}, 204


class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200


class ShowArticle(Resource):
    def get(self, id):
        # Initialize page_views if not set
        session['page_views'] = session.get('page_views', 0)

        # Increment page_views counter FIRST
        session['page_views'] += 1

        # Check if user has NOW exceeded the 3 article limit
        if session['page_views'] > 3:
            return {'message': 'Maximum pageview limit reached'}, 401

        # Query the article by ID
        article = Article.query.filter_by(id=id).first()

        if not article:
            return {'message': 'Article not found'}, 404

        # Return article as JSON using to_dict()
        return article.to_dict(), 200


class Login(Resource):
    def post(self):
        # Get username from request JSON
        username = request.get_json().get('username')
        
        # Retrieve user by username
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return {'message': 'User not found'}, 404
        
        # Set session's user_id to the user's id
        session['user_id'] = user.id
        
        # Return user as JSON with 200 status
        return user.to_dict(), 200


class Logout(Resource):
    def delete(self):
        # Remove user_id from session
        session['user_id'] = None
        
        # Return no data with 204 status
        return {}, 204


class CheckSession(Resource):
    def get(self):
        # Retrieve user_id from session
        user_id = session.get('user_id')
        
        if user_id:
            # If session has user_id, return the user
            user = User.query.filter_by(id=user_id).first()
            if user:
                return user.to_dict(), 200
        
        # If no user_id in session, return 401
        return {}, 401


# Register resources with their routes
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')


if __name__ == '__main__':
    app.run(port=5555, debug=True)