from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Category, Base, Item, User
 
engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

Daniel = User(name="Daniel Burkard")
session.add(Daniel)

John = User(name="John Doe")
session.add(John)

Basketball = Category(name="Basketball")
session.add(Basketball)

Baselball = Category(name="Baselball")
session.add(Baselball)

Snowboarding = Category(name="Snowboarding")
session.add(Snowboarding)

Judo = Category(name="Judo")
session.add(Judo)

Capoeira = Category(name="Capoeira")
session.add(Capoeira)

IceHockey = Category(name="Ice Hockey")
session.add(IceHockey)

Googles = Item(name="Googles",category=Snowboarding,owner=John)
session.add(Googles)

Bat = Item(name="Bat",category=Basketball,owner=John)
session.add(Bat)

JudoGi = Item(name="Judogi",
	category=Judo,
	owner=Daniel,
	image="http://www.goods.pl/images/products/pl/Judogi_plecionka-biale_12oz_GTTA318_200.jpg",
	description="Judogi is the formal Japanese name for the traditional uniform used for Judo practice and competition.")
session.add(JudoGi)

Obi = Item(name="Obi",category=Judo,owner=Daniel,image="http://3.bp.blogspot.com/-Rkxk5i9mMd4/Ul_rFJ1KwoI/AAAAAAAAAbU/6lw0hQSqZGg/s1600/Black%2BBelt.png")
session.add(Obi)

Snowboard = Item(name="Snowboard",category=Snowboarding,owner=John)
session.add(Snowboard)

Berimbau = Item(name="Berimbau",
	category=Capoeira,
	owner=Daniel,
	image="http://202.67.224.137/pfimage/53/743253_berimbau_capoeira.jpg",
	description="The berimbau is a single-string percussion instrument, a musical bow, from Brazil. The berimbau was eventually incorporated into the practice of the Afro-Brazilian martial art capoeira, the berimbau (the soul of capoeira) leads the capoeiristas movement in the roda the faster the berimbau is playing the faster the capoeirista moves in the game.")
session.add(Berimbau)

Atabaque = Item(name="Atabaque",
	category=Capoeira,
	owner=Daniel,
	image="http://4.bp.blogspot.com/-7-RtMPOQueQ/TphDxsTAgTI/AAAAAAAAALA/CCFjK5khMrE/s1600/atabaque.jpg",
	description="The atabaque is a tall, wooden, Afro-Brazilian hand drum. The shell is made traditionally of Jacaranda wood from Brazil. The head is traditionally made from calfskin. A system of ropes are intertwined around the body, connecting a metal ring near the base to the head.")
session.add(Atabaque)

session.commit()

