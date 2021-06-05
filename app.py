# Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from flask_graphql import GraphQLView

# app initialization
app = Flask(__name__)
app.debug = True

basedir = os.path.abspath(os.path.dirname(__file__))

# Configs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# TO-DO
# Modules
db = SQLAlchemy(app)


# TO-DO
# Models
class User(db.Model):
    __tablename__ = 'users'
    uuid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), index=True, unique=True)
    posts = db.relationship('Post', backref='author')

    def __repr__(self):
        return '<User %r>' % self.username


class Post(db.Model):
    __tablename__ = 'posts'
    uuid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True)
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.uuid'))

    def __repr__(self):
        return '<Post %r>' % self.title


# TO-DO
# Schema Objects
class PostObject(SQLAlchemyObjectType):
    class Meta:
        model = Post
        interfaces = (graphene.relay.Node,)


class UserObject(SQLAlchemyObjectType):
    class Meta:
        model = User
        interfaces = (graphene.relay.Node,)


class Hellyson(graphene.ObjectType):
    first_name = graphene.String()
    last_name = graphene.String()

    full_name = graphene.String()

    def resolve_full_name(self, info):
        full_name = f'{self.first_name} {self.last_name}'
        
        return full_name
class Quadrado(graphene.ObjectType):
    l1 = graphene.Float()
    l2 = graphene.Float()
    area = graphene.Float()

    def resolve_area(self,info):
        area = self.l1 * self.l2

        return area

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_posts = SQLAlchemyConnectionField(PostObject)
    all_users = SQLAlchemyConnectionField(UserObject)
    hellyson = graphene.Field(Hellyson, first_name=graphene.String(), last_name=graphene.String())
    quadrado = graphene.Field(Quadrado,l1=graphene.Float(),l2=graphene.Float())

    def resolve_hellyson(self, info, first_name, last_name):
        return Hellyson(first_name=first_name, last_name=last_name)

    def resolve_quadrado(self, info, l1, l2):
        return Quadrado(l1=l1, l2=l2)



class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        body = graphene.String(required=True)
        username = graphene.String(required=True)

    post = graphene.Field(lambda: PostObject)
    posts_quantity = graphene.Field(graphene.Int)

    def mutate(self, info, title, body, username):
        user = User.query.filter_by(username=username).first()
        post = Post(title=title, body=body)
        if user is not None:
            post.author = user
        db.session.add(post)
        db.session.commit()

        posts_quantity = db.session.query(Post).count()
        return CreatePost(post=post, posts_quantity=posts_quantity)


class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

# TO-DO
# Routes
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # for having the GraphiQL interface
    )
)


# TO-DO
@app.route('/')
def index():
    return '<p> Hello World</p>'


if __name__ == '__main__':
    app.run()
# {
#   allPosts{
#     edges{
#       node{
#         title
#         body
#         author{
#           username
#         }
#       }
#     }
#   }
# }
# mutation {
#   createPost(username:"Hellyson", title:"Creating a GraphQL server with flask", body:"GraphQL is a query language for APIs and a runtime for fulfilling those queries with your existing data. GraphQL provides a complete and understandable description of the data in your API, gives clients the power to ask for exactly what they need and nothing more, makes it easier to evolve APIs over time, and enables powerful developer tools."){
#     post{
#       title
#       body
#       author{
#         username
#       }
#     }
#   }
# }


