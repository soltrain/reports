from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine("mysql+mysqldb://noah:noahgogogo@112.124.110.150:3306/DB_IS", convert_unicode=True)

#for making the model
Base = declarative_base()

class Diner(Base):
	__tablename__ = 'diner'
	#declaring a method that returns Column
	dinerID = Column(Integer, primary_key=True)
	firstname = Column(String(30))
	createDT = Column(DateTime)

	def __repr__(self):
		return '<Diner %r>' % (self.firstname)

class Restaurant(Base):
	__tablename__ = 'restaurant'
	restaurantID = Column(Integer, primary_key=True)
	likevotes = Column(Integer)
	dislikevotes = Column(Integer)
	name = Column(String)
	isValid = Column(Integer)

class RestaurantVoteHistory(Base):
	__tablename__ = 'restaurantvotehistory'
	voteID = Column(Integer, primary_key=True)
	fkrestaurantID = Column(Integer, ForeignKey('restaurant.restaurantID'))
	votedate = Column(DateTime)
	fkdinerID = Column(Integer, ForeignKey('diner.dinerID'))
	isValid = Column(Integer)

	restaurant = relationship("Restaurant")
	diner = relationship("Diner")

class SearchLog(Base):
	__tablename__ = 'searchlog'
	id = Column(Integer, primary_key=True)
	DT = Column(DateTime)
	IP = Column(String(50))
	userID = Column(Integer)

class RestaurantGallery(Base):
	__tablename__ = 'restaurantgallery'
	galleryID = Column(Integer, primary_key=True)
	restaurantID = Column(Integer)
	fkuserID = Column(Integer, ForeignKey('diner.dinerID'))
	createDate = Column(DateTime)
	isValid = Column(Integer)

	diner = relationship("Diner")

class Review(Base):
	__tablename__ = 'reviews'
	id = Column(Integer, primary_key=True)
	fkrestaurantID = Column(Integer, ForeignKey('restaurant.restaurantID'))
	dinerID = Column(Integer, ForeignKey('diner.dinerID'))
	isValid = Column(Integer)

	restaurant = relationship("Restaurant")
	diner = relationship("Diner")
	



# select COUNT(DISTINCT RestaurantID) from restaurant a where likevotes+dislikevotes>5;


