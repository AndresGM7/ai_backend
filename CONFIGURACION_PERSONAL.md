# 📝 Guía de Configuración Personal

## 🎯 Lugares donde debes actualizar tus datos

### 1. README.md - Sección de Autor (Línea ~152)

```markdown
## 👨‍💻 Autor

**Andrés Giraldo**
- Portfolio: https://andresgiraldo.dev (← CAMBIA ESTO)
- LinkedIn: https://www.linkedin.com/in/andgm/(← CAMBIA ESTO)
- GitHub: https://github.com/AndresGM7
- Email: andresgiraldo1988@gmail.com
```

### 2. README.md - Badge de GitHub Actions (Línea ~3)

```markdown
[![CI Pipeline](https://github.com/TU_USUARIO/ai_backend/workflows/CI%20Pipeline/badge.svg)]
```

Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub.

### 3. Git Config (Ya configurado localmente)

Tu Git local ya tiene:
```bash
git config user.name "Andres Giraldo"
git config user.email "andresgiraldo1988@gmail.com"
```

Para cambiar globalmente:
```bash
git config --global user.name "Andres Giraldo"
git config --global user.email "andresgiraldo1988@gmail.com"
```

### 4. pyproject.toml - Metadatos del proyecto

```toml
[tool.poetry]
name = "aibackend"
version = "0.1.0"
description = "Sistema de Optimización de Precios con IA"  # Agregar descripción
authors = [
    "Andrés Giraldo <andresgiraldo1988@gmail.com>"  # Actualizar email
]
```

### 5. Cuando subas a GitHub

Necesitarás crear el repositorio y conectarlo:

```bash
# En GitHub, crea un nuevo repositorio llamado "ai_backend"
# Luego ejecuta:

git remote add origin https://github.com/AndresGM7/ai_backend.git
git branch -M main
git push -u origin main
```

---

## ✅ Datos a Actualizar (Checklist)

- [ ] **README.md** - Sección de Autor
- [ ] **README.md** - Badge de GitHub Actions
- [ ] **README.md** - URL de git clone
- [ ] **Git config** - Email real
- [ ] **pyproject.toml** - Author email
- [ ] **GitHub** - Crear repositorio remoto
- [ ] **GitHub** - Configurar secretos (OPENAI_API_KEY para CI/CD)

---

## 🔑 Secretos de GitHub (Para CI/CD)

Cuando subas a GitHub, configura estos secretos:

1. Ve a tu repo en GitHub
2. Settings > Secrets and variables > Actions
3. Agrega estos secretos:
   - `OPENAI_API_KEY`: Tu clave de OpenAI

Esto permitirá que el pipeline CI/CD funcione correctamente.

---

## 📧 Emails Sugeridos

Si no tienes un email profesional, usa:
- Gmail profesional: nombre.apellido@gmail.com
- ProtonMail: nombre.apellido@proton.me
- Outlook: nombre.apellido@outlook.com

---

## 🌐 URLs Sugeridas

### Portfolio:
- GitHub Pages: https://tu-usuario.github.io
- Vercel: https://tu-nombre.vercel.app
- Netlify: https://tu-nombre.netlify.app

### LinkedIn:
- Formato: https://linkedin.com/in/nombre-apellido
- Personaliza tu URL desde LinkedIn Settings

### GitHub:
- Tu perfil: https://github.com/tu-usuario
- Este proyecto: https://github.com/tu-usuario/ai_backend

---

## 💡 Recomendaciones

1. **Usa el mismo nombre de usuario** en GitHub, LinkedIn y portfolio para consistencia
2. **Email profesional** - Evita emails poco profesionales
3. **Portfolio actualizado** - Agrega este proyecto con screenshots
4. **LinkedIn optimizado** - Menciona las tecnologías: FastAPI, Python, OpenAI

---

## 🚀 Siguiente Paso

Después de actualizar tus datos:

```bash
# Hacer commit de los cambios
git add README.md pyproject.toml
git commit -m "docs: actualizar información personal"

# Crear repositorio en GitHub y subir
git remote add origin https://github.com/TU_USUARIO/ai_backend.git
git push -u origin main
```

