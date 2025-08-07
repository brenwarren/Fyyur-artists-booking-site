#!/usr/bin/env python3
"""
Script to add sample venue data for testing
"""
from app import app, db, Venue, Artist, Show
from datetime import datetime

def add_sample_data():
    with app.app_context():
        # Create sample venues
        venue1 = Venue(
            name="The Musical Hop",
            city="San Francisco",
            state="CA", 
            address="1015 Folsom Street",
            phone="123-123-1234",
            image_link="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
            facebook_link="https://www.facebook.com/TheMusicalHop",
            genres="Jazz,Reggae,Swing,Classical,Folk",
            website="https://www.themusicalhop.com",
            seeking_talent=True,
            seeking_description="We are on the lookout for a local artist to play every two weeks. Please call us."
        )
        
        venue2 = Venue(
            name="The Dueling Pianos Bar",
            city="New York",
            state="NY",
            address="335 Delancey Street", 
            phone="914-003-1132",
            image_link="https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
            facebook_link="https://www.facebook.com/theduelingpianos",
            genres="Classical,R&B,Hip-Hop",
            website="https://www.theduelingpianos.com",
            seeking_talent=False
        )
        
        venue3 = Venue(
            name="Park Square Live Music & Coffee",
            city="San Francisco", 
            state="CA",
            address="34 Whiskey Moore Ave",
            phone="415-000-1234",
            image_link="https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
            genres="Rock n Roll,Jazz,Classical,Folk",
            website="https://www.parksquarelivemusicandcoffee.com",
            seeking_talent=False
        )
        
        # Add sample artists
        artist1 = Artist(
            name="Guns N Petals",
            city="San Francisco",
            state="CA",
            phone="326-123-5000",
            genres="Rock n Roll",
            image_link="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            facebook_link="https://www.facebook.com/GunsNPetals",
            website="https://www.gunsnpetalsband.com",
            seeking_venue=True,
            seeking_description="Looking for shows to perform at in the San Francisco Bay Area!"
        )
        
        artist2 = Artist(
            name="Matt Quevedo", 
            city="New York",
            state="NY",
            phone="300-400-5000",
            genres="Jazz",
            image_link="https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
            facebook_link="https://www.facebook.com/mattquevedo923251523",
            seeking_venue=False
        )
        
        artist3 = Artist(
            name="The Wild Sax Band",
            city="San Francisco",
            state="CA",
            phone="432-325-5432",
            genres="Jazz,Classical",
            image_link="https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            seeking_venue=False
        )
        
        try:
            # Add to database
            db.session.add(venue1)
            db.session.add(venue2) 
            db.session.add(venue3)
            db.session.add(artist1)
            db.session.add(artist2)
            db.session.add(artist3)
            db.session.commit()
            
            # Add some shows
            show1 = Show(
                start_time=datetime(2019, 5, 21, 21, 30),
                artist_id=artist1.id,
                venue_id=venue1.id
            )
            
            show2 = Show(
                start_time=datetime(2019, 6, 15, 23, 0),
                artist_id=artist2.id,
                venue_id=venue3.id
            )
            
            show3 = Show(
                start_time=datetime(2035, 4, 1, 20, 0),
                artist_id=artist3.id, 
                venue_id=venue3.id
            )
            
            show4 = Show(
                start_time=datetime(2035, 4, 8, 20, 0),
                artist_id=artist3.id, 
                venue_id=venue3.id
            )
            
            show5 = Show(
                start_time=datetime(2035, 4, 15, 20, 0),
                artist_id=artist3.id, 
                venue_id=venue3.id
            )
            
            db.session.add(show1)
            db.session.add(show2)
            db.session.add(show3)
            db.session.add(show4)
            db.session.add(show5)
            db.session.commit()
            
            print("Sample data added successfully!")
            print(f"Added {len([venue1, venue2, venue3])} venues")
            print(f"Added {len([artist1, artist2, artist3])} artists")
            print(f"Added {len([show1, show2, show3, show4, show5])} shows")
            
        except Exception as e:
            print(f"Error adding sample data: {e}")
            db.session.rollback()
            
if __name__ == "__main__":
    add_sample_data()
