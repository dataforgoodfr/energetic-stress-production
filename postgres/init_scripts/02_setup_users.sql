-- Création de l'utilisateur super
CREATE ROLE super_user WITH LOGIN PASSWORD '$$POSTGRES_SUPER_USER_PASSWORD$$' SUPERUSER;

-- Création de l'utilisateur read-only
CREATE ROLE readonly_user WITH LOGIN PASSWORD '$$POSTGRES_READONLY_USER_PASSWORD$$';

-- Accorder des privilèges de lecture
GRANT CONNECT ON DATABASE stress_energetic TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Pour accorder des privilèges de lecture sur les nouvelles tables créées ultérieurement
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;