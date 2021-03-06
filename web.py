import os
from flask import Flask, render_template
from flask.json import jsonify 
from model import Restaurant, RestaurantVoteHistory, Diner, engine, Base, SearchLog, RestaurantGallery, Review, Invite, Invitee
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import func, or_
from datetime import datetime, timedelta
import pdb

app = Flask(__name__)




@app.route('/')
def index():
    db_session = scoped_session(sessionmaker(bind=engine))
    Base.query = db_session.query_property()
    restaurants_with_rating = Restaurant.query.filter(Restaurant.likeVotes+Restaurant.dislikeVotes>5).count()
    restaurants_with_pictures = db_session.query(RestaurantGallery.restaurantID).distinct(RestaurantGallery.restaurantID).\
                                filter(RestaurantGallery.isValid==1).count()
    # following doesn't work for some reason    
    # restaurants_with_reviews = Review.query(Review.fkrestaurantID).distinct(Review.fkrestaurantID)
    restaurants_with_reviews = db_session.query(Review.fkrestaurantID).distinct(Review.fkrestaurantID).count()

    # SELECT diner.FirstName, inviterdinerid, COUNT(DISTINCT InviteeUID) from inviteeinfo INNER JOIN inviteinfo ON inviteeinfo.fkinviteid=inviteinfo.inviteid 
    # INNER JOIN diner ON diner.dinerID=inviteinfo.inviterdinerid  GROUP BY inviterdinerid ORDER BY COUNT(DISTINCT InviteeUID) DESC
    # returns an array of Diner instances and a count
    top_referrers = db_session.query(Diner, func.count(func.distinct(Invitee.inviteeUID))).\
                    join(Invite).\
                    join(Invitee).group_by(Invite.inviterDinerID).\
                    order_by(func.count(Invitee.inviteeUID).desc()).all()

# SELECT firstname, r.dinerID, COUNT(content) FROM reviews r, diner d WHERE r.dinerID=d.dinerID AND r.isvalid=1 GROUP BY r.dinerID ORDER BY COUNT(content) DESC;

    recent_reviewers = db_session.query(Diner, func.count(Review.content)).join(Review).filter(Review.isValid==1).\
                       filter(Diner.createDT>x_days_ago(5)).\
                       group_by(Diner.dinerID).all()


# example of sqlalchemy subquery
# SELECT users.*, adr_count.address_count FROM users 
# LEFT OUTER JOIN (SELECT user_id, count(*) AS address_count FROM addresses 
    # GROUP BY user_id) AS adr_count ON users.id=adr_count.user_id

# stmt = session.query(Address.user_id, func.count('*').\
#          label('address_count')).\
#          group_by(Address.user_id).subquery()

# session.query(User, stmt.c.address_count).\
#      outerjoin(stmt, User.id==stmt.c.user_id).order_by(User.id): 



    recentvotes = db_session.query(RestaurantVoteHistory.fkdinerID, func.count(RestaurantVoteHistory.voteID).label('a')).filter(RestaurantVoteHistory.voteDate>x_days_ago(1)).\
                  group_by(RestaurantVoteHistory.fkdinerID).subquery()

    recentreviews = db_session.query(Review.dinerID, func.count(Review.id).label('b')).filter(Review.reviewDate>x_days_ago(1)).\
                  group_by(Review.dinerID).subquery()

    recentsearches = db_session.query(SearchLog.userID, func.count(SearchLog.id).label('c')).filter(SearchLog.DT>x_days_ago(1)).\
                  group_by(SearchLog.userID).subquery()

    active_users = db_session.query(Diner, recentvotes.c.a, recentreviews.c.b, recentsearches.c.c).\
                   filter(or_(recentvotes.c.a != None, recentreviews.c.b != None, recentsearches.c.c != None)).\
                   outerjoin(recentvotes).\
                   outerjoin(recentreviews).\
                   outerjoin(recentsearches)
                                      #filter(recentreviews!=None).\


# select diner.dinerid, diner.username, recentsearches, recentvotes, recentreviews, recentpics, recentfavorites, recentwishlist, recentuseful from diner

# LEFT JOIN (select userID, count(DT) as recentsearches from searchlog
# where DATEDIFF(CURDATE(), DT) < 1
# group by userID) se ON diner.dinerid=se.userID

# LEFT JOIN (select fkdinerid, count(votedate) as recentvotes from restaurantvotehistory
# where isvalid=1
# and DATEDIFF(CURDATE(), votedate) < 1
# group by fkdinerid) vo ON diner.dinerid=vo.fkdinerid

# LEFT JOIN (select dinerid, count(*) as recentreviews from reviews 
# where isvalid=1
# and DATEDIFF(CURDATE(), reviewdate) < 1
# group by DinerID) re ON diner.dinerid=re.dinerid 

# LEFT JOIN (select restaurantgallery.fkuserid, count(*) as recentpics from restaurantgallery 
# where isvalid=1
# and DATEDIFF(CURDATE(), createdate) < 1
# group by restaurantgallery.fkuserid) ga ON diner.dinerid=ga.fkuserid 
 
# left join (select favourite.fkdinerid, count(*) as recentfavorites from favourite 
# where isvalid=1
# and DATEDIFF(CURDATE(), favouritedate) < 1
# group by favourite.fkdinerid) fa ON diner.dinerid = fa.fkdinerid 

# left join (select wishlist.fkdinerid, count(*) as recentwishlist from wishlist
# where isvalid=1
# and DATEDIFF(CURDATE(), wishdate) < 1
# group by wishlist.fkdinerid) wi ON diner.dinerid = wi.fkdinerid 

# left join (select reviewpraise.fkdinerid, count(*) as recentuseful from reviewpraise
# where isvalid=1
# and DATEDIFF(CURDATE(), praisedate) < 1
# group by reviewpraise.fkdinerid) us ON diner.dinerid = us.fkdinerid 

# where recentsearches is not null or recentvotes is not null or recentreviews is not null or recentfavorites is not null or recentwishlist 
# is not null or recentuseful is not null or recentpics is not null

    search_volume_guest = db_session.query(SearchLog.DT, func.count(SearchLog.IP)).distinct(SearchLog.IP).\
                          filter(SearchLog.userID == None).group_by(func.date(SearchLog.DT)).order_by(SearchLog.DT.desc()).all()
    search_volume_guest = [ [1000*convert_timestamp(timestamp), count] for (timestamp, count) in search_volume_guest if timestamp is not None]
    search_volume_registered = db_session.query(SearchLog.DT, func.count(SearchLog.IP)).distinct(SearchLog.IP).\
                          filter(SearchLog.userID != None).group_by(func.date(SearchLog.DT)).order_by(SearchLog.DT.desc()).all()
    search_volume_registered = [ [1000*convert_timestamp(timestamp), count] for (timestamp, count) in search_volume_registered if timestamp is not None]

    recent_voters = db_session.query(func.count(RestaurantVoteHistory.voteID), Diner).\
                    join(Diner).filter(Diner.createDT>x_days_ago(5)).group_by(Diner.dinerID).\
                    order_by(func.count(RestaurantVoteHistory.voteID).desc()).all()
  
    diners = Diner.query.all()
    db_session.remove()
    return render_template('index.html', restaurants_with_rating=restaurants_with_rating,
                                         restaurants_with_pictures=restaurants_with_pictures,
                                         restaurants_with_reviews=restaurants_with_reviews, 
                                         active_users=active_users,
                                         top_referrers=top_referrers,   
                                         diners=diners, 
                                         recent_voters=recent_voters,
                                         recent_reviewers=recent_reviewers, 
                                         search_volume_guest=search_volume_guest,
                                         search_volume_registered=search_volume_registered)

@app.route('/vote_history/<diner_id>')
def vote_history(diner_id):
    db_session = scoped_session(sessionmaker(bind=engine))
    Base.query = db_session.query_property()
    
    #returns instances of RestaurantVoteHistory, in order to get actual data, need to call method of the Class  
    noah_vote_history_raw = db_session.query(RestaurantVoteHistory, Diner, Restaurant).\
                             join(Restaurant).join(Diner).filter(RestaurantVoteHistory.isValid==1).\
                             filter(Diner.dinerID==diner_id).order_by(RestaurantVoteHistory.voteDate.desc()).all()
    timestamps = [ convert_timestamp(vote.voteDate) for (vote, diner, restaurant) in noah_vote_history_raw ]
    uniq_timestamps = set(timestamps)
    noah_vote_history = [ [1000*timestamp, count_timestamps(timestamp, timestamps)] for timestamp in uniq_timestamps ] 

    return jsonify({'data': noah_vote_history})

def count_timestamps(timestamp, timestamps):
    return sum([ 1 for t in timestamps if t == timestamp]) 

def convert_timestamp(from_datetime): 
   date = from_datetime.replace(minute=0, hour=0, second=0, microsecond=0)
   return (date-datetime(1970, 1, 1)).total_seconds()

def x_days_ago(days):
   return datetime.now() - timedelta(days=days)

# Vat does dis do?
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
    
