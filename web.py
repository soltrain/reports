import os
from flask import Flask, render_template
from model import Restaurant, RestaurantVoteHistory, Diner, engine, Base
from sqlalchemy.orm import scoped_session, sessionmaker
import pdb


app = Flask(__name__)

@app.route('/')
def index():

    db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
    Base.query = db_session.query_property()

    restaurants_with_rating = Restaurant.query.filter(Restaurant.likevotes+Restaurant.dislikevotes>5).count()
    #returns instances of RestaurantVoteHistory, in order to get actual data, need to call method of the Class  
    noah_vote_history = db_session.query(RestaurantVoteHistory, Diner, Restaurant).\
                        join(Restaurant).join(Diner).filter(RestaurantVoteHistory.isvalid==1).\
                        filter(Diner.dinerID==42).order_by(RestaurantVoteHistory.votedate.desc()).all()
    #pdb.set_trace()
    db_session.remove()

    return render_template('index.html', restaurants_with_rating=restaurants_with_rating, noah_vote_history=noah_vote_history)

if __name__ == '__main__':
    app.debug = True
    app.run()
    
