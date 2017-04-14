# A simple data pipeline service
Author: Eric Yang (jiweni__removeme__624@gmail.com) (iron_mq.py is a library provided by Heroku, not me)

## How it works
The service is running on Heroku with URL (I masked the URL, contact me if you'd like to give it a try): `https://pure--badl__removeme__ands-49030.hero__removeme__kuapp.com/`.

As it's running on a free cloud account it may not be fast, but it's functional.

There are limits on the monthly usage for free users(e.g., 10,000 messages per month for the message queue) and the performance is not good for Heroku's free service so it may not be able to serve long-time stress test.

Try it with curl:

`curl -d '{"event_name": "crash_report","user_id": 888,"timestamp": 1000,"message": "have_fun"}' "https://pure-badlands-49030.herokuapp.com/"`

## Assumptions
 - event_type with heading or trailing spaces is considered a different type (thus invalid). e.g., `'crash_report'` is a valid message but `' crash_report'` is invalid.

## The architecture
The service is running on Heroku.

Data flow:

`Data source (from POST) --> Data Processor --> In-memory Message Queue --> Data Loader --> PostgreSQL database`

The data processor will do the following tasks:
 - check input validity and respond with `status_code` and `status_message`.
 - parse json message from the `POST` body and extract events from it.
 - insert the events to message queues.

The data loader does the following tasks:

 - wake up every 5 minutes (the interval is configurable).
 - check existing events in the message queue.
 - implements a file-like class to pull messages from the queues and call PostgreSQL `\copy` API to load data to the database in bulk.
 - the data pulled from the message queue will be removed as well.

The message queue will help to store the events temporarily. The queues will protect us from:

 - events duplicates or loss.
 - concurrent read and write without race conditions and consistency issues.
 - scalable store size and a buffer between the data processor and the data loader
 - much faster I/O than storing events on disk files.
 - other benefits.

## Features
 - Almost all parameters are configurable, with either the default values in `settings.py`, or values read from `/etc/datapipe.json`, or any other file specified by environment variable `$DATAPIPE_CNF`.
 - easy to extend to support new event types, developers just need to inherit from the base class Event and register the child class for the new event type to the event_handlers. You don't need to modify the existing data processing functions.
 - configurable numbers of database loader workers and minimum and regular loading intervals.

## TODO List
 - Wrap the database layer to support different databases.
 - More exception handling and corner cases test for the external services (PostgreSQL database and the message queues) to make the application more robust.
 - Multiprocessing support for the web application (for now it's useless as the Heroku free service is weak).
 - configuration of the service daemon monitoring for production environment (without the help of cloud provider), e.g., `supervisord`.
 - code refactoring. e.g., remove most of the global variables and re-organize the inheritances, etc.
