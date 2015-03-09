# inspired by https://github.com/cenkalti/github-flask/blob/master/example.py
# setup flask
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, g, session
from flask.ext.seasurf import SeaSurf
app = Flask(__name__)
csrf = SeaSurf(app)
# setup ssl if needed
# import ssl
# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
# context.load_cert_chain('/etc/ssl/private/server.pem')

# setup client id and secret of github application for oauth 
from flask.ext.github import GitHub

# config application
app.config['GITHUB_CLIENT_ID'] = 'XXX'
app.config['GITHUB_CLIENT_SECRET'] = 'YYY'
github_callback_url = "https://dev.danielburkard.de/github-callback"
github = GitHub(app)

# setup sqlalchemy
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker,scoped_session
from database_setup import Base, Category, Item, User
engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

# http://docs.sqlalchemy.org/en/rel_0_8/orm/session.html#sqlalchemy.orm.scoping.scoped_session
db_session = scoped_session(sessionmaker(autocommit=False,
	autoflush=False,
	bind=engine))

Base.query = db_session.query_property()

# flask functions 
##################
"""show whole catalog with latest items"""
@app.route('/')
@app.route('/catalog/')
def showCatalog():
	categories = Category.query.all()
	items = Item.query.order_by(Item.created.desc()).all()
	return render_template('catalog.html', categories = categories,items=items,user=g.user)

"""show a category with its items"""
@app.route('/catalog/<string:category_name>/')
def showCategory(category_name):
	categories = Category.query.all()
	category = Category.query.filter_by(name=category_name).one()
	items = Item.query.filter_by(category = category).all()
	return render_template('catalog.html', categories = categories,items=items,category=category,user=g.user)

"""show a item"""
@app.route('/item/<int:item_id>/')
def showItem(item_id):
	item = Item.query.filter_by(id = item_id).one()
	return render_template('item.html', item = item,user=g.user)

"""add a item"""
@app.route('/catalog/<string:category_name>/add/', methods = ['GET', 'POST'])
def addItem(category_name):
	categories = Category.query.all()
	category = Category.query.filter_by(name = category_name).one()
	user = g.user
	# check if user is authenticated
	if user is not None:
		if request.method == 'POST':
			# check if an item name was entered
			if request.form['name'] != "":
				mycategory = Category.query.filter_by(name=request.form['category']).one()
				item = Item(name=request.form['name'],
					image=request.form['image'],
					description=request.form['description'],
					category=mycategory,
					owner=user)
				db_session.add(item)
				db_session.commit()
				flash("Item " + item.name + " added to " + item.category.name)
				return redirect(url_for('showCategory',category_name=mycategory.name))
			else:
				flash("Item name must not be empty")
				return redirect(url_for('addItem',category_name=category_name))
		else:
			return render_template('additem.html',category=category,categories=categories,user=user)
	else:
		flash("Unauthorized user")
		return redirect(url_for('showCatalog'))

"""edit a item"""
@app.route('/item/<int:item_id>/edit/', methods = ['GET', 'POST'])
def editItem(item_id):
	item = Item.query.filter_by(id = item_id).one()
	user = g.user
	# check if user is owner
	if user == item.owner:
		if request.method == 'POST':
			# check if an item name was entered
			if request.form['name'] != "":
				item.name = request.form['name']
				item.image = request.form['image']
				item.description = request.form['description']
				if request.form['category']:
					category = Category.query.filter_by(name=request.form['category']).one()
					item.category = category
				db_session.add(item)
				db_session.commit()
				flash("Item " + item.name + " saved")
				return redirect(url_for('showItem',item_id=item.id))
			else:
				flash("Item name must not be empty")
				return redirect(url_for('editItem',item_id=item.id))
		else:
			categories = Category.query.all()
			return render_template('edititem.html', item = item,categories=categories,user=user)
	else:
		flash("Unauthorized user")
		return redirect(url_for('showCatalog'))

"""delete a item"""
@app.route('/item/<int:item_id>/delete/', methods = ['GET', 'POST'])
def deleteItem(item_id):
	item = Item.query.filter_by(id = item_id).one()
	category = item.category
	user = g.user
	# check if user is owner
	if user == item.owner:
		if request.method == 'POST':
			flash("Item " + item.name + " deleted")
			db_session.delete(item)
			db_session.commit()
			return redirect(url_for('showCategory', category_name=category.name))
		else:
			return render_template('deleteitem.html', item = item, user=g.user)
	else:
		flash("Unauthorized user")
		return redirect(url_for('showCatalog'))


"""user Login"""
@app.route('/login')
def loginUser():
	# send user back to the source page
	uri = github_callback_url + "?next=" + request.referrer
	return github.authorize(redirect_uri=uri)
	# if session.get('user_id', None) is None:
	# 	return github.authorize()
	# else:
	# 	flash('User is already logged in')
	# 	return redirect(url_for('showCatalog'))
	
"""logout user and show main catalog view"""
@app.route('/logout')
def logoutUser():
	session.pop('user_id', None)
	flash('User logged out')
	return redirect(url_for('showCatalog'))

"""callback for github oauth"""
@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
	next_url = request.args.get('next') or url_for('showCatalog')
	if oauth_token is None:
		# something went wront
		flash("Authorization failed")
		flash(request.args.get('error'))
		flash(request.args.get('error_description'))
		flash(request.args.get('error_uri'))
		return redirect(next_url)
	user = User.query.filter_by(github_access_token=oauth_token).first()
	if user is None:
		# new user is not in database
		user = User(name="",github_access_token=oauth_token)
		db_session.add(user)
	# save oauth token in database
	user.github_access_token = oauth_token
	db_session.commit()
	session['user_id'] = user.id
	flash("User " + user.name + " logged in")
	return redirect(next_url)

"""github token getter"""
@github.access_token_getter
def token_getter():
	user = g.user
	if user is not None:
		return user.github_access_token

# Registers a function to run before each request.
"""save user data to database, maybe it changed or user is new"""
@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.get(session['user_id'])
		g.user.name = github.get('user')["name"]
		g.user.avatar = github.get('user')["avatar_url"]
		db_session.add(g.user)
		db_session.commit()

"""Register a function to be run after each request"""
@app.after_request
def after_request(response):
	db_session.remove()
	return response

"""json api for list of all items"""
@app.route('/json')
def catalogjson():
	list = []
	items = Item.query.all()
	for item in items:
		list.append({"name" : item.name,
			"id" : item.id,
			"description" : item.description,
			"category" : item.category.name,
			"image" : item.image,
			"owner" : item.owner.name
		})
	return jsonify({"items":list})
	
# run flask server if script is started directly 
if __name__ == '__main__':
	app.debug = True
	app.secret_key='ZZZ'
	app.run(host = '0.0.0.0', port = 5000)