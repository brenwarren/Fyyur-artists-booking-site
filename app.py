#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate ##added for database migrations
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config['SECRET_KEY'] = 'brens-big-secret-key'  # Set a secret key for CSRF protection
moment = Moment(app)
#app.config.from_object('config')
app.config.from_object('config.Config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)  ##added for database migrations

# TODO: connect to a local postgresql database 
# >>>>That action has now BEEN DONE. See config.py for database connection details.

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # >>>> Done - see new genres, website, seeking_talent, and seeking_description fields.

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    #>>>> Done - see new website, seeking_venue, and seeking_description fields.

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
#>>> Done - See Show model below created with relationships to Artist and Venue models.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

# @app.route('/venues')
# def venues():
#   # TODO: replace with real venues data.
#   #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
#   data=[{
#     "city": "San Francisco",
#     "state": "CA",
#     "venues": [{
#       "id": 1,
#       "name": "The Musical Hop",
#       "num_upcoming_shows": 0,
#     }, {
#       "id": 3,
#       "name": "Park Square Live Music & Coffee",
#       "num_upcoming_shows": 1,
#     }]
#   }, {
#     "city": "New York",
#     "state": "NY",
#     "venues": [{
#       "id": 2,
#       "name": "The Dueling Pianos Bar",
#       "num_upcoming_shows": 0,
#     }]
#   }]
#   return render_template('pages/venues.html', areas=data);



@app.route('/venues')
def venues():
    try:
        venues = Venue.query.all()
        print(f"Found {len(venues)} venues in database")  # Debug info
        
        # If no venues, return empty data structure
        if not venues:
            data = []
            return render_template('pages/venues.html', areas=data)
        
        # Organize venues by city and state
        data = []
        locations = set()
        for venue in venues:
            locations.add((venue.city, venue.state))
        
        for city, state in locations:
            city_venues = []
            for venue in venues:
                if venue.city == city and venue.state == state:
                    # Count upcoming shows
                    num_upcoming_shows = len([show for show in venue.shows if show.start_time > datetime.now()])
                    city_venues.append({
                        "id": venue.id,
                        "name": venue.name,
                        "num_upcoming_shows": num_upcoming_shows
                    })
            data.append({
                "city": city,
                "state": state,
                "venues": city_venues
            })
        
        print(f"Returning data: {data}")  # Debug info
        return render_template('pages/venues.html', areas=data)
    except Exception as e:
        print(f"Error in venues route: {e}")  # Add debugging
        import traceback
        traceback.print_exc()  # Print full stack trace
        db.session.rollback()
        return render_template('errors/500.html'), 500
    finally:
        db.session.close()



@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  try:
    # Get venue from database
    venue = Venue.query.get(venue_id)
    
    if not venue:
      return render_template('errors/404.html'), 404
    
    # Get shows for this venue
    shows = Show.query.filter_by(venue_id=venue_id).join(Artist).all()
    
    # Separate past and upcoming shows
    now = datetime.now()
    past_shows = []
    upcoming_shows = []
    
    for show in shows:
      show_data = {
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.isoformat() + "Z"
      }
      
      if show.start_time < now:
        past_shows.append(show_data)
      else:
        upcoming_shows.append(show_data)
    
    # Convert genres string to list if it exists
    genres_list = venue.genres.split(',') if venue.genres else []
    
    # Prepare data for template
    data = {
      "id": venue.id,
      "name": venue.name,
      "genres": genres_list,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
    
    return render_template('pages/show_venue.html', venue=data)
    
  except Exception as e:
    print(f"Error in show_venue: {e}")
    db.session.rollback()
    return render_template('errors/500.html'), 500
  finally:
    db.session.close()

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

# @app.route('/venues/create', methods=['POST'])
# def create_venue_submission():
#   # TODO: insert form data as a new Venue record in the db, instead
# >>>>Done - see create_venue_submission function below.
#   # TODO: modify data to be the data object returned from db insertion
# >>>>Done - see create_venue_submission function below.

#   # on successful db insert, flash success
#   flash('Venue ' + request.form['name'] + ' was successfully listed!')
#   # TODO: on unsuccessful db insert, flash an error instead.
# >>>> Done - see create_venue_submission function below.
#   # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
#   # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
#   return render_template('pages/home.html')


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  error = False
  try:
    venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      genres=','.join(form.genres.data) if isinstance(form.genres.data, list) else form.genres.data,
      website=form.website_link.data,
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except Exception as e:
    error = True
    db.session.rollback()
    print(f"Error creating venue: {e}")  # Debug line
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    # Find the venue by ID
    venue = Venue.query.get(venue_id)
    
    if not venue:
      flash(f'Venue with ID {venue_id} not found.')
      return redirect(url_for('index'))
    
    venue_name = venue.name  # Store name for flash message
    
    # Delete associated shows first (cascade delete)
    Show.query.filter_by(venue_id=venue_id).delete()
    
    # Delete the venue
    db.session.delete(venue)
    db.session.commit()
    
    flash(f'Venue "{venue_name}" was successfully deleted!')
    return redirect(url_for('index'))
    
  except Exception as e:
    db.session.rollback()
    print(f"Error deleting venue: {e}")
    flash(f'An error occurred. Venue could not be deleted.')
    return redirect(url_for('index'))
  finally:
    db.session.close()

#     TODO: Complete this endpoint for taking a venue_id, and using
# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
# clicking that button delete it from the db then redirect the user to the homepage
# >>>> Done - see delete_venue function above.


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  try:
    # Query all artists from database
    artists = Artist.query.all()
    
    # Format data for template
    data = []
    for artist in artists:
      data.append({
        "id": artist.id,
        "name": artist.name,
      })
    
    return render_template('pages/artists.html', artists=data)
  except Exception as e:
    print(f"Error in artists route: {e}")
    db.session.rollback()
    return render_template('errors/500.html'), 500
  finally:
    db.session.close()

@app.route('/artists/search', methods=['POST'])
def search_artists():
  try:
    search_term = request.form.get('search_term', '')
    
    # Case-insensitive partial string search using ilike
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    
    # Count upcoming shows for each artist
    data = []
    for artist in artists:
      # Count upcoming shows for this artist
      now = datetime.now()
      upcoming_shows_count = len([show for show in artist.shows if show.start_time > now])
      
      data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": upcoming_shows_count,
      })
    
    response = {
      "count": len(data),
      "data": data
    }
    
    return render_template('pages/search_artists.html', results=response, search_term=search_term)
  except Exception as e:
    print(f"Error in search_artists: {e}")
    db.session.rollback()
    return render_template('errors/500.html'), 500
  finally:
    db.session.close()

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  try:
    # Get artist from database
    artist = Artist.query.get(artist_id)
    
    if not artist:
      return render_template('errors/404.html'), 404
    
    # Get shows for this artist
    shows = Show.query.filter_by(artist_id=artist_id).join(Venue).all()
    
    # Separate past and upcoming shows
    now = datetime.now()
    past_shows = []
    upcoming_shows = []
    
    for show in shows:
      show_data = {
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.isoformat() + "Z"
      }
      
      if show.start_time < now:
        past_shows.append(show_data)
      else:
        upcoming_shows.append(show_data)
    
    # Convert genres string to list if it exists
    genres_list = artist.genres.split(',') if artist.genres else []
    
    # Prepare data for template
    data = {
      "id": artist.id,
      "name": artist.name,
      "genres": genres_list,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
    
    return render_template('pages/show_artist.html', artist=data)
    
  except Exception as e:
    print(f"Error in show_artist: {e}")
    db.session.rollback()
    return render_template('errors/500.html'), 500
  finally:
    db.session.close()

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  try:
    # Get artist from database
    artist = Artist.query.get(artist_id)
    
    if not artist:
      return render_template('errors/404.html'), 404
    
    # Create form and populate with existing data
    form = ArtistForm()
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres.split(',') if artist.genres else []
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    
    # Prepare artist data for template
    artist_data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres.split(',') if artist.genres else [],
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link
    }
    
    return render_template('forms/edit_artist.html', form=form, artist=artist_data)
  except Exception as e:
    print(f"Error in edit_artist: {e}")
    db.session.rollback()
    return render_template('errors/500.html'), 500
  finally:
    db.session.close()

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    # Get artist from database
    artist = Artist.query.get(artist_id)
    
    if not artist:
      flash(f'Artist with ID {artist_id} not found.')
      return redirect(url_for('artists'))
    
    # Get form data
    form = ArtistForm(request.form)
    
    # Update artist with form data
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = ','.join(form.genres.data) if isinstance(form.genres.data, list) else form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    
    # Commit changes
    db.session.commit()
    flash(f'Artist {artist.name} was successfully updated!')
    
    return redirect(url_for('show_artist', artist_id=artist_id))
    
  except Exception as e:
    db.session.rollback()
    print(f"Error updating artist: {e}")
    flash(f'An error occurred. Artist could not be updated.')
    return redirect(url_for('show_artist', artist_id=artist_id))
  finally:
    db.session.close()

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  try:
    # Get venue from database
    venue = Venue.query.get(venue_id)
    
    if not venue:
      return render_template('errors/404.html'), 404
    
    # Create form and populate with existing data
    form = VenueForm()
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres.split(',') if venue.genres else []
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    
    # Prepare venue data for template
    venue_data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres.split(',') if venue.genres else [],
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link
    }
    
    return render_template('forms/edit_venue.html', form=form, venue=venue_data)
  except Exception as e:
    print(f"Error in edit_venue: {e}")
    db.session.rollback()
    return render_template('errors/500.html'), 500
  finally:
    db.session.close()

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    # Get venue from database
    venue = Venue.query.get(venue_id)
    
    if not venue:
      flash(f'Venue with ID {venue_id} not found.')
      return redirect(url_for('venues'))
    
    # Get form data
    form = VenueForm(request.form)
    
    # Update venue with form data
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = ','.join(form.genres.data) if isinstance(form.genres.data, list) else form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    
    # Commit changes
    db.session.commit()
    flash(f'Venue {venue.name} was successfully updated!')
    
    return redirect(url_for('show_venue', venue_id=venue_id))
    
  except Exception as e:
    db.session.rollback()
    print(f"Error updating venue: {e}")
    flash(f'An error occurred. Venue could not be updated.')
    return redirect(url_for('show_venue', venue_id=venue_id))
  finally:
    db.session.close()

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    # Get form data
    form = ArtistForm(request.form)
    
    # Create new artist instance
    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=','.join(form.genres.data) if isinstance(form.genres.data, list) else form.genres.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website=form.website_link.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data
    )
    
    # Add to database
    db.session.add(artist)
    db.session.commit()
    
    # Flash success message
    flash('Artist ' + form.name.data + ' was successfully listed!')
    
  except Exception as e:
    db.session.rollback()
    print(f"Error creating artist: {e}")
    # Flash error message
    flash('An error occurred. Artist ' + request.form.get('name', '') + ' could not be listed.')
  finally:
    db.session.close()
    
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
