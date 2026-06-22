package config

import (
	"fmt"
	"net/url"
)

// EnvGetter is a function that looks up an environment variable.
// It matches the signature of os.LookupEnv.
type EnvGetter func(key string) (string, bool)

const (
	DefaultEnv         = "production"
	DefaultPort        = "8080"
	DefaultFrontendDir = "web"
	DefaultDBUser      = "navallist_user"
	DefaultDBPass      = "password"
	DefaultDBHost      = "localhost"
	DefaultDBPort      = "5432"
	DefaultDBName      = "navallistdb"
	DefaultDBSSLMode   = "disable"
	DefaultSiteURL     = "http://localhost:8080"
)

// Config holds the application configuration.
type Config struct {
	Env          string
	Port         string
	ModelName    string
	GoogleAPIKey string
	FrontendDir  string
	SiteURL      string
	DB           DBConfig
}

// DBConfig holds database connection details.
type DBConfig struct {
	User     string
	Password string
	Host     string
	Port     string
	Name     string
	SSLMode  string
}

// Load populates the Config struct using the provided environment lookup function.
func Load(lookup EnvGetter) (*Config, error) {
	// Helper to use the injected lookup
	get := func(key, fallback string) string {
		if value, exists := lookup(key); exists {
			return value
		}
		return fallback
	}

	// Direct lookup for mandatory/optional without default
	getOptional := func(key string) string {
		val, _ := lookup(key)
		return val
	}

	siteURL := get("NAVALLIST_SITE_URL", DefaultSiteURL)

	cfg := &Config{
		Env:          get("ENV", DefaultEnv),
		Port:         get("NAVALLIST_PORT", DefaultPort),
		ModelName:    get("NAVALLIST_MODEL", "gemini-2.5-flash"),
		GoogleAPIKey: getOptional("NAVALLIST_GOOGLE_API_KEY"),
		FrontendDir:  get("NAVALLIST_FRONTEND_DIR", DefaultFrontendDir),
		SiteURL:      siteURL,
		DB: DBConfig{
			User:     get("NAVALLIST_DB_USER", DefaultDBUser),
			Password: get("NAVALLIST_DB_PASS", DefaultDBPass),
			Host:     get("NAVALLIST_DB_HOST", DefaultDBHost),
			Port:     get("NAVALLIST_DB_PORT", DefaultDBPort),
			Name:     get("NAVALLIST_DB_NAME", DefaultDBName),
			SSLMode:  get("NAVALLIST_DB_SSLMODE", DefaultDBSSLMode),
		},
	}

	return cfg, nil
}

// DSN constructs the PostgreSQL Data Source Name.
func (db DBConfig) DSN() string {
	q := make(url.Values)
	q.Set("sslmode", db.SSLMode)

	u := url.URL{
		Scheme:   "postgres",
		User:     url.UserPassword(db.User, db.Password),
		Host:     fmt.Sprintf("%s:%s", db.Host, db.Port),
		Path:     "/" + db.Name,
		RawQuery: q.Encode(),
	}
	return u.String()
}
