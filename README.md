# DinnerSchool - Sistema de Comedor Escolar

![Django](https://img.shields.io/badge/Django-4.2.23-green.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Sistema web para gestión de comedor escolar desarrollado con Django. Permite la administración de usuarios, pedidos, platillos, créditos y noticias para instituciones educativas.

## 🚀 Características Principales

- **Gestión de Usuarios**: Administración de alumnos, tutores y empleados
- **Sistema de Pedidos**: Gestión completa de pedidos de comida
- **Manejo de Créditos**: Control de créditos y pagos
- **Catálogo de Platillos**: Administración de menú e ingredientes
- **Sistema de Noticias**: Publicación de anuncios y noticias
- **Panel Administrativo**: Interfaz de administración completa
- **Soporte Multi-base de datos**: SQLite para desarrollo, PostgreSQL para producción

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 4.2.23
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: HTML, CSS, JavaScript
- **Contenedores**: Docker & Docker Compose
- **Variables de Entorno**: python-dotenv

## 📋 Requisitos Previos

- Python 3.11+
- pip (gestor de paquetes de Python)
- PostgreSQL 15+ (para producción)
- Docker & Docker Compose (opcional)

## 🔧 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Marco0425/DinnerSchool.git
cd DinnerSchool
```

### 2. Configurar Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Copia el archivo de ejemplo y configura tus variables:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus configuraciones:

```env
# Django Configuration
SECRET_KEY=tu-clave-secreta-super-segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration - PostgreSQL (Producción)
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/dinnerschool

# ReCAPTCHA Configuration
RECAPTCHA_SITE_KEY=tu-site-key
RECAPTCHA_SECRET_KEY=tu-secret-key
```

### 5. Configurar Base de Datos

#### Para Desarrollo (SQLite)
```bash
cd DinnerSchool
python manage.py migrate
python manage.py createsuperuser
```

#### Para Producción (PostgreSQL)
```bash
# Asegurate de tener PostgreSQL corriendo
cd DinnerSchool
python manage.py migrate
python manage.py createsuperuser
```

### 6. Ejecutar el Servidor

```bash
cd DinnerSchool
python manage.py runserver
```

El sistema estará disponible en: `http://localhost:8000`

## 🐳 Instalación con Docker

### 1. Usando Docker Compose

```bash
# Construir y ejecutar todos los servicios
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d

# Crear superusuario
docker-compose exec web python DinnerSchool/manage.py createsuperuser
```

### 2. Solo PostgreSQL

Si solo quieres ejecutar PostgreSQL con Docker:

```bash
docker-compose up postgres -d
```

## 📊 Migración de SQLite a PostgreSQL

El proyecto incluye un script automatizado para migrar datos de SQLite a PostgreSQL:

### 1. Preparar PostgreSQL

Asegúrate de que PostgreSQL esté corriendo y la base de datos esté creada.

### 2. Ejecutar Migración

```bash
python migrate_to_postgres.py postgresql://usuario:contraseña@localhost:5432/dinnerschool
```

### 3. Actualizar Configuración

Actualiza tu archivo `.env` con la nueva URL de PostgreSQL:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/dinnerschool
```

## 📱 Uso del Sistema

### Panel de Administración

Accede al panel de administración en: `http://localhost:8000/admin/`

### Funcionalidades Principales

1. **Gestión de Usuarios**
   - Registro de alumnos, tutores y empleados
   - Asignación de roles y permisos

2. **Sistema de Pedidos**
   - Creación de pedidos por turno (desayuno/comida)
   - Seguimiento de estados de pedidos
   - Gestión de ingredientes especiales

3. **Manejo de Créditos**
   - Recarga de créditos por tutor
   - Historial de transacciones
   - Control de gastos diarios

4. **Catálogo de Platillos**
   - Administración de menús
   - Control de precios e ingredientes
   - Disponibilidad por turno

## 🗂️ Estructura del Proyecto

```
DinnerSchool/
├── core/                    # App principal de usuarios
│   ├── models.py           # Modelos de usuarios, alumnos, tutores
│   ├── views.py            # Vistas principales
│   └── templates/          # Plantillas HTML
├── comedor/                # App del sistema de comedor
│   ├── models.py           # Modelos de pedidos, platillos, créditos
│   ├── views.py            # Lógica de negocio del comedor
│   └── admin.py            # Configuración del admin
├── mysite/                 # Configuración del proyecto Django
│   ├── settings.py         # Configuración principal
│   ├── urls.py             # URLs principales
│   └── wsgi.py             # Configuración WSGI
├── static/                 # Archivos estáticos (CSS, JS, imágenes)
├── migrate_to_postgres.py  # Script de migración
├── docker-compose.yml      # Configuración Docker
├── requirements.txt        # Dependencias Python
└── .env.example           # Ejemplo de variables de entorno
```

## 🔒 Seguridad

### Variables de Entorno

- **SECRET_KEY**: Clave secreta de Django (¡NUNCA la compartas!)
- **DEBUG**: Siempre `False` en producción
- **ALLOWED_HOSTS**: Lista de hosts permitidos en producción

### Buenas Prácticas

- Usa HTTPS en producción
- Configura un firewall adecuado
- Realiza backups regulares de la base de datos
- Mantén las dependencias actualizadas

## 🧪 Pruebas

```bash
# Ejecutar todas las pruebas
python manage.py test

# Ejecutar pruebas específicas
python manage.py test core
python manage.py test comedor
```

## 📈 Deployment

### Preparación para Producción

1. **Configurar Variables de Entorno**
   ```env
   SECRET_KEY=tu-clave-super-secreta-de-producción
   DEBUG=False
   ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
   DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/dinnerschool
   ```

2. **Configurar Archivos Estáticos**
   ```bash
   python manage.py collectstatic
   ```

3. **Aplicar Migraciones**
   ```bash
   python manage.py migrate
   ```

### Opciones de Deployment

- **Heroku**: Compatible con configuración de variables de entorno
- **DigitalOcean**: Usando App Platform o Droplets
- **AWS**: EC2 con RDS para PostgreSQL
- **Docker**: Usando la configuración incluida

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa los [Issues existentes](https://github.com/Marco0425/DinnerSchool/issues)
2. Crea un nuevo Issue si tu problema no está reportado
3. Proporciona información detallada sobre el error

## 🔄 Changelog

### v1.0.0
- ✅ Configuración inicial del proyecto
- ✅ Sistema de gestión de usuarios
- ✅ Sistema de pedidos y platillos
- ✅ Manejo de créditos
- ✅ Sistema de noticias
- ✅ Soporte para PostgreSQL
- ✅ Script de migración automática
- ✅ Configuración Docker

---

Desarrollado con ❤️ para instituciones educativas