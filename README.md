# INSICA - Sistema Inteligente de Gestión Inmobiliaria

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![MVC](https://img.shields.io/badge/Architecture-MVC-purple.svg)

**INSICA** es un Sistema Inteligente de Gestión y Optimización de Operaciones diseñado para el Sector Inmobiliario. Esta plataforma web automatiza los flujos administrativos, moderniza el catálogo de inmuebles y centraliza la gestión comercial, sustituyendo la obsolescencia de los métodos manuales por un entorno seguro y escalable.

## 🏗️ Arquitectura y Módulos Principales

El sistema está construido bajo el patrón de arquitectura **Modelo-Vista-Controlador (MVC)** y la metodología de desarrollo de sistemas de información de Llorens (1991). Se divide en 4 grandes almacenes de datos:

*   **Módulo 1: Gestión de Inmuebles (D1)**: Permite a los Agentes Inmobiliarios registrar nuevas propiedades (fotos, precio, ubicación). Genera fichas técnicas detalladas y mantiene el catálogo actualizado.
*   **Módulo 2: Interacciones y CRM (D2)**: Centraliza las consultas de los clientes (Leads), disparando alertas al equipo comercial para su rápida gestión.
*   **Módulo 3: Gestión de Citas (D3)**: Sistema de agendamiento donde el Cliente solicita fechas para visitar inmuebles, y el Agente confirma o reprograma la visita.
*   **Módulo 4: Gestión de Ventas (D4)**: Automatiza el cierre comercial, procesando el monto final y calculando los honorarios (comisiones) generados.

## 🔐 Control de Acceso Basado en Roles (RBAC)

La plataforma garantiza el Aislamiento de Datos (Data Isolation) categorizando a los usuarios en tres perfiles:

1.  **Administrador**: Gerencia global. Supervisa el inventario histórico, aprueba la creación de nuevos Agentes y monitorea las métricas financieras (volumen transaccionado y comisiones) de toda la agencia.
2.  **Agente Inmobiliario**: Equipo comercial. Publica propiedades en el catálogo, atiende sus Leads asignados, administra su propia agenda de citas y procesa sus cierres de ventas.
3.  **Cliente**: Usuario público registrado. Explora el catálogo de propiedades disponibles, visualiza detalles, envía consultas y agenda citas.

## 💻 Tecnologías Utilizadas

*   **Backend**: Python 3.9+, Flask, Flask-Login, Flask-SQLAlchemy.
*   **Base de Datos**: Base de datos relacional (MySQL/SQLite).
*   **Frontend**: HTML5, CSS3, Bootstrap 5, Jinja2.
*   **Control de versiones**: Git, GitHub

## ⚙️ Instalación y Configuración Local


Sigue estos pasos para ejecutar el proyecto en tu entorno de desarrollo:

1. **Clonar el repositorio**
    ```bash
    git clone [https://github.com/tu-usuario/insica-sistema-inmobiliario.git](https://github.com/tu-usuario/insica-sistema-inmobiliario.git)
    cd insica-sistema-inmobiliario
    ```

2. **Crear y activar un entorno virtual**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3. **Instalar dependencias**
    ```bash
    pip install -r requirements.txt
    ```

4. **Inicializar la Base de Datos (Seeding)**
    > **Nota**: El sistema incluye un script que purga esquemas antiguos y genera un usuario Administrador por defecto para pruebas.
    ```bash
    python setup_db.py
    ```

5. **Ejecutar la aplicación**
    ```bash
    python run.py
    ```

   *La plataforma estará disponible en `http://localhost:5000`.*

## 🎓 Créditos Académicos

Este proyecto ha sido desarrollado como Trabajo de Investigación para optar al título de **Licenciatura en Computación** en la **Facultad Experimental de Ciencias** de **La Universidad del Zulia (LUZ)**[cite: 11].

*   **Autor**: Yainder Jesús Muñoz Piña[cite: 11]
*   **Tutora**: Prof. Yaskelly Yedra[cite: 11]