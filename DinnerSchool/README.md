# 🍽️ DinnerSchool - Sistema de Comedor Escolar

Sistema integral de gestión de comedor escolar desarrollado en Django que permite administrar pedidos, usuarios, créditos y noticias de forma eficiente.

## 🌟 Características

- **👥 Gestión de Usuarios**: Administración completa de alumnos, empleados y tutores
- **🍕 Sistema de Pedidos**: Gestión de platillos, ingredientes y pedidos con estados en tiempo real
- **💳 Manejo de Créditos**: Sistema de créditos diarios y acumulados para los tutores
- **📰 Noticias**: Publicación y gestión de noticias escolares
- **🔧 Panel Administrativo**: Interface completa de administración con Django Admin
- **📱 Responsive**: Diseño adaptable para dispositivos móviles

## 🚀 Instalación

### Prerrequisitos

- Python 3.8+
- PostgreSQL (para producción) o SQLite (para desarrollo)
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/Marco0425/DinnerSchool.git
cd DinnerSchool
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
# Generar SECRET_KEY en: https://djecrety.ir/
```

### 5. Configurar base de datos

#### Para desarrollo (SQLite):
```bash
cd DinnerSchool
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

#### Para producción (PostgreSQL):
```bash
# Crear base de datos PostgreSQL
createdb dinnerschool_db

# Configurar DATABASE_URL en .env
DATABASE_URL=postgresql://usuario:password@localhost:5432/dinnerschool_db

# Ejecutar migraciones
cd DinnerSchool
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Ejecutar el servidor

```bash
python manage.py runserver
```

Visita `http://127.0.0.1:8000` para ver la aplicación.

## 🐳 Docker (Opcional)

### Ejecutar con Docker Compose

```bash
# Construir y ejecutar
docker-compose up --build

# Solo ejecutar (después del primer build)
docker-compose up
```

## 📊 Migración de SQLite a PostgreSQL

Si ya tienes datos en SQLite y quieres migrar a PostgreSQL:

### 1. Instalar PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS con Homebrew
brew install postgresql
```

### 2. Crear base de datos

```bash
sudo -u postgres psql
CREATE DATABASE dinnerschool_db;
CREATE USER dinnerschool_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE dinnerschool_db TO dinnerschool_user;
\q
```

### 3. Configurar variables de entorno

```bash
# En tu archivo .env
DATABASE_URL=postgresql://dinnerschool_user:tu_password@localhost:5432/dinnerschool_db
```

### 4. Ejecutar script de migración

```bash
python migrate_to_postgres.py
```

### 5. Verificar migración

```bash
python manage.py runserver
# Verificar que todos los datos estén presentes
```

## 🏗️ Estructura del Proyecto

```
DinnerSchool/
├── DinnerSchool/
│   ├── core/                 # App principal de usuarios
│   │   ├── models.py        # Modelos de Usuario, Empleados, Tutores, Alumnos
│   │   ├── admin.py         # Configuración del admin
│   │   └── templates/       # Templates del core
│   ├── comedor/             # App del sistema de comedor
│   │   ├── models.py        # Modelos de Platillos, Pedidos, Créditos
│   │   ├── admin.py         # Admin del comedor
│   │   └── migrations/      # Migraciones de base de datos
│   └── mysite/              # Configuración principal
│       ├── settings.py      # Configuraciones de Django
│       └── urls.py          # URLs principales
├── static/                  # Archivos estáticos
├── requirements.txt         # Dependencias de Python
├── docker-compose.yml       # Configuración de Docker
└── README.md               # Este archivo
```

## 💻 Tecnologías Utilizadas

- **Backend**: Django 4.2.23
- **Base de datos**: PostgreSQL / SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Contenedor**: Docker & Docker Compose
- **Autenticación**: Django Auth System

## 🔧 Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic

# Ejecutar tests
python manage.py test

# Shell de Django
python manage.py shell
```

## 📱 Uso del Sistema

### Panel Administrativo
- Accede a `/admin/` con tu cuenta de superusuario
- Gestiona usuarios, platillos, pedidos y noticias

### Funcionalidades Principales
1. **Gestión de Usuarios**: Crear y administrar alumnos, empleados y tutores
2. **Catálogo de Platillos**: Administrar menú con ingredientes y precios
3. **Sistema de Pedidos**: Estados: Pendiente → En preparación → Listo → Entregado
4. **Créditos**: Sistema de monedero virtual para tutores
5. **Noticias**: Comunicación oficial del comedor

## 🤝 Contribución

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Contacto

Marco Antonio - [@Marco0425](https://github.com/Marco0425)

Project Link: [https://github.com/Marco0425/DinnerSchool](https://github.com/Marco0425/DinnerSchool)

## 🙏 Agradecimientos

- Django Framework por su robustez y facilidad de uso
- PostgreSQL por la gestión confiable de datos
- La comunidad de código abierto por las herramientas utilizadas