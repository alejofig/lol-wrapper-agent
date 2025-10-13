# 🎮 LoL Wrapped - Landing Page

Modern, minimalist landing page for LoL Wrapped, inspired by [Spotify Wrapped](https://www.spotify.com/us/wrapped/), built with Astro.

## 📋 Requisitos

- Node.js >= 18.20.8 (o superior)
- npm >= 9.6.5

> **Nota:** Si tienes Node.js v18.20.7, actualiza a v18.20.8+ o usa Node v20/v22 para evitar advertencias de compatibilidad.

## 🚀 Inicio Rápido

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# Construir para producción
npm run build

# Vista previa de producción
npm run preview
```

## 📁 Estructura

```
landing/
├── src/
│   └── pages/
│       └── index.astro      # Landing page principal
├── public/                  # Assets estáticos
├── astro.config.mjs        # Configuración de Astro
└── package.json
```

## 🎨 Características

- ✨ Diseño moderno y responsivo
- 🎯 Optimizado para SEO
- ⚡ Ultra rápido (Astro + CSS vanilla)
- 🌈 Gradientes y animaciones suaves
- 📱 Mobile-first design
- 🎮 Temática de League of Legends

## 🔗 Integración con Backend

Para conectar con tu servidor MCP, actualiza el script de envío del formulario en `index.astro`:

```javascript
// En la sección <script>
const response = await fetch('http://localhost:8000/api/wrapped', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ gameName, tagLine, region })
});
```

## 🎨 Personalización

Los colores principales están definidos en variables CSS en `index.astro`:

```css
:root {
  --primary: #0bc5ea;        /* Cyan */
  --secondary: #c084fc;      /* Purple */
  --accent: #fbbf24;         /* Amber */
  --bg-dark: #0a0e1a;        /* Dark blue */
}
```

## 📦 Scripts Disponibles

- `npm run dev` - Inicia el servidor de desarrollo (puerto 4321)
- `npm run build` - Construye para producción
- `npm run preview` - Vista previa de la build de producción

## 🌐 Deploy

### AWS Amplify (Recomendado)

Para desplegar en AWS Amplify, consulta la [Guía de Despliegue](./DEPLOYMENT.md) detallada.

**Resumen rápido:**
1. Configura variables de entorno (AppSync credentials)
2. Conecta tu repositorio Git a Amplify Console
3. Configura `landing` como root directory
4. Deploy automático ✨

### Otras plataformas

También puedes desplegar en:
- Vercel
- Netlify
- Cloudflare Pages
- GitHub Pages
- Cualquier hosting estático

```bash
npm run build
# Los archivos estarán en /dist
```

## 📝 Licencia

MIT
