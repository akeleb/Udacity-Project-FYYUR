#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
from datetime import datetime
import dateutil.parser
import babel
from flask import (render_template, request, flash, redirect, url_for)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
import sys
from model import app, db, Venue, Artist, Show
import collections
from waitress import serve

moment = Moment(app)
db.init_app(app)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    collections.Callable = collections.abc.Callable
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues---------------------------------------------------------------

@app.route('/venues')
def venues():
    states = db.session.query(Venue.state, Venue.city).distinct().all()
    venues = db.session.query(Venue).all()
    return render_template('pages/venues.html', states=states, venues=venues)


@app.route('/venues/search', methods=['POST'])
def search_venues():

    search_term = request.form.get('search_term', '')
    venues = db.session.query(Venue).all()
    results = []
    for venue in venues:
        if (venue.name).lower() == search_term.lower():
            results.append(venue)
    results_count = len(results)
    print(results)
    return render_template('pages/search_venues.html', results_count=results_count, results=results, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue1 = Venue.query.get(venue_id)
    venue_genres = [s.strip() for s in venue1.genres[1:-1].split(',')]
    upcoming_shows_details = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time >= datetime.now()).all()
    past_shows_details = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
    upcoming_shows = []
    for show in upcoming_shows_details:
        upcoming_shows.append({
            'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'artist_image_link': show.artist.image_link,
            'artist_id': show.artist_id,
            'artist_name': show.artist.name
        })
    past_shows = []
    for show in past_shows_details:
        past_shows.append({
            'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'artist_image_link': show.artist.image_link,
            'artist_id': show.artist_id,
            'artist_name': show.artist.name
        })
    data = {'upcoming_shows_count': len(upcoming_shows), 'past_shows_count': len(
        past_shows), 'upcoming_shows': upcoming_shows, 'past_shows': past_shows}

    return render_template('pages/show_venue.html', data=data, venue_genres=venue_genres, venue=venue1)

#  Create Venue ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    FlaskForm = VenueForm()
    return render_template('forms/new_venue.html', form=FlaskForm)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    data = {
        'name': request.form.get('name'),
        'genres': str(request.form.getlist('genres')),
        'address': request.form.get('address'),
        'state': request.form.get('state'),
        'city': request.form.get('city'),
        'phone': request.form.get('phone'),
        'image_link': request.form.get('image_link'),
        'website': request.form.get('website'),
        'facebook_link': request.form.get('facebook_link'),
        'seeking_talent': request.form.get('seeking_talent'),
        'seeking_description': request.form.get('seeking_description'),
    }
    try:
        venue = Venue(name=data['name'],
                      genres=data['genres'],
                      address=data['address'],
                      state=data['state'],
                      city=data['city'],
                      phone=data['phone'],
                      image_link=data['image_link'],
                      website=data['website'],
                      facebook_link=data['facebook_link'],
                      seeking_talent=(data['seeking_talent'] == 'True'),
                      seeking_description=data['seeking_description'],
                      )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # on successful db insert, flash success
    except:
        db.session.rollback()
      
        flash('An error occurred. Venue ' +
              data['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('The venue was successfully deleted!')
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('venues'))


#  Artists----------------------------------------------------------------


@app.route('/artists')
def artists():
    artists = db.session.query(Artist).all()
    return render_template('pages/artists.html', artists=artists)


@app.route('/artists/<artist_id>/delete', methods=['POST'])
def delete_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('artists'))


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = db.session.query(Artist).all()
    results = []
    for artist in artists:
        if (artist.name).lower() == search_term.lower():
            results.append(artist)
    results_count = len(results)
    print(results)
    return render_template('pages/search_artists.html', results_count=results_count, results=results, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    artist_genres = [s.strip() for s in artist.genres[1:-1].split(',')]
    upcoming_shows_details = db.session.query(Show).join(Artist).filter(
        Show.artist_id == artist_id).filter(Show.start_time >= datetime.now()).all()
    past_shows_details = db.session.query(Show).join(Artist).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()

    upcoming_shows = []
    for show in upcoming_shows_details:
        upcoming_shows.append({
            'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'venue_image_link': show.venue.image_link,
            'venue_id': show.venue_id,
            'venue_name': show.venue.name
        })
    past_shows = []
    for show in past_shows_details:
        past_shows.append({
            'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'venue_image_link': show.venue.image_link,
            'venue_id': show.venue_id,
            'venue_name': show.venue.name
        })
    data = {'upcoming_shows_count': len(upcoming_shows), 'past_shows_count': len(
        past_shows), 'upcoming_shows': upcoming_shows, 'past_shows': past_shows}
    return render_template('pages/show_artist.html', artist_genres=artist_genres, data=data, artist=artist)

#  Update Artist detail ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    FlaskForm = ArtistForm()
    artist = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=FlaskForm, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    data = {
        'name': request.form.get('name'),
        'genres': str(request.form.getlist('genres')),
        'state': request.form.get('state'),
        'city': request.form.get('city'),
        'phone': request.form.get('phone'),
        'image_link': request.form.get('image_link'),
        'website': request.form.get('website'),
        'facebook_link': request.form.get('facebook_link'),
        'seeking_venus': request.form.get('seeking_venue'),
        'seeking_description': request.form.get('seeking_description'),
    }
    try:
        artist = Artist.query.get(artist_id)
        artist.genres = data['genres']
        artist.state = data['state']
        artist.city = data['city']
        artist.name = data['name']
        artist.phone = data['phone']
        artist.image_link = data['image_link']
        artist.website = data['website']
        artist.facebook_link = data['facebook_link']
        artist.seeking_venus = (data['seeking_venus'] == 'True')
        artist.seeking_description = data['seeking_description']
        db.session.commit()
        flash('The Artist was successfully edited!')
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    data = {
        'name': request.form.get('name'),
        'genres': str(request.form.getlist('genres')),
        'address': request.form.get('address'),
        'state': request.form.get('state'),
        'city': request.form.get('city'),
        'phone': request.form.get('phone'),
        'image_link': request.form.get('image_link'),
        'website': request.form.get('website'),
        'facebook_link': request.form.get('facebook_link'),
        'seeking_talent': request.form.get('seeking_talent'),
        'seeking_description': request.form.get('seeking_description'),
    }
    try:
        venue = Venue.query.get(venue_id)
        venue.genres = data['genres']
        venue.address = data['address']
        venue.state = data['state']
        venue.city = data['city']
        venue.name = data['name']
        venue.phone = data['phone']
        venue.image_link = data['image_link']
        venue.website = data['website']
        venue.facebook_link = data['facebook_link']
        venue.seeking_talent = (data['seeking_talent'] == 'True')
        venue.seeking_description = data['seeking_description']
        db.session.commit()
        flash('The venue was successfully edited!')
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create New Artist----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    FlaskForm = ArtistForm()
    return render_template('forms/new_artist.html', form=FlaskForm)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    data = {
        'name': request.form.get('name'),
        'genres': str(request.form.getlist('genres')),
        'address': request.form.get('address'),
        'state': request.form.get('state'),
        'city': request.form.get('city'),
        'phone': request.form.get('phone'),
        'image_link': request.form.get('image_link'),
        'website': request.form.get('website'),
        'facebook_link': request.form.get('facebook_link'),
        'seeking_venue': request.form.get('seeking_venue'),
        'seeking_description': request.form.get('seeking_description'),
    }
    try:
        artist = Artist(name=data['name'],
                        genres=data['genres'],
                        state=data['state'],
                        city=data['city'],
                        phone=data['phone'],
                        image_link=data['image_link'],
                        website=data['website'],
                        facebook_link=data['facebook_link'],
                        seeking_venus=(data['seeking_venue'] == 'True'),
                        seeking_description=data['seeking_description']
                        )
        db.session.add(artist)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # on successful db insert, flash success
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred.Artist ' +
              data.name + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')
#  Shows----------------------------------------------------------------


@app.route('/shows')
def shows():
    shows = db.session.query(
        Show,
        Venue,
        Artist
    ).filter(
        Show.artist_id == Artist.id
    ).filter(
        Show.venue_id == Venue.id
    ).all()
    for show, venue, artist in shows:
        show.start_time = str(show.start_time)
    print(shows)
    return render_template('pages/shows.html', shows=shows)


@app.route('/shows/create')
def create_shows():
    FlaskForm = ShowForm()
    return render_template('forms/new_show.html', form=FlaskForm)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    data = {
        'artist_id': int(request.form.get('artist_id')),
        'venue_id': int(request.form.get('venue_id')),
        'start_time': str(request.form.get('start_time'))
    }
    try:
        show = Show(artist_id=data['artist_id'],
                    venue_id=data['venue_id'],
                    start_time=data['start_time'],
                    )
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

# if __name__ == '__main__':
#     # port = int(os.environ.get('PORT', 3000))
#     # app.run(host='0.0.0.0', port=port)
    serve(app, host='0.0.0.0', port='5000')
