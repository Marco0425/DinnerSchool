services:
  - type: web
    name: dinnerschool
    env: docker
    plan: free
    branch: main
    healthCheckPath: /admin/
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: dinnerschool_db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: "False"
      - key: ALLOWED_HOSTS
        value: ".onrender.com,dinnerschool.onrender.com"
      - key: DJANGO_SETTINGS_MODULE
        value: "mysite.settings"

databases:
  - name: dinnerschool_db
    databaseName: dinnerschool_db
    user: dinnerschool_db_user
    plan: free
