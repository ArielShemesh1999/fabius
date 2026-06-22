DROP TRIGGER IF EXISTS trigger_trip_update ON trip;
DROP TRIGGER IF EXISTS trigger_checklist_update ON checklist_item;
DROP TRIGGER IF EXISTS trigger_adk_session_event_insert ON adk_session_event;

DROP FUNCTION IF EXISTS notify_changes();
DROP FUNCTION IF EXISTS shortkey_generate();

DROP TABLE IF EXISTS trip_crew;
DROP TABLE IF EXISTS artifact;
DROP TABLE IF EXISTS checklist_item;
DROP TABLE IF EXISTS trip;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS adk_session_event;

DROP EXTENSION IF EXISTS pgcrypto;
