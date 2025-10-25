Ideal and reusable workflow: CSV with movie titles, year, genre, leading actor(s) and rating -> parse out genres and actors, dedupe and save to tables -> save movie info and join table back to genres and actors. Some additional columns potentially. Same flow with shows just more columns like network name and season/episode info etc.

- [ ] Parse CSV in leding actor column, deduplicate and push into db with ids
- [ ] Same as above for genres
- [ ] Insert media and relate actors and genres to it
