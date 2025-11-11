/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: [
      'api.mapbox.com',
      // Add your Cloudflare R2 domain when you set it up in Stage 4
      // Example: 'pub-abc123.r2.dev'
    ],
  },
  experimental: {
    serverActions: {
      allowedOrigins: ['localhost:3000'],
    },
  },
  async headers() {
    return [
      {
        // Apply CORS headers to API routes
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: process.env.ASTRO_SERVICE_URL || 'http://localhost:8000' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,DELETE,PATCH,POST,PUT,OPTIONS' },
          { 
            key: 'Access-Control-Allow-Headers', 
            value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization' 
          },
        ],
      },
    ];
  },
  webpack: (config, { isServer }) => {
    // Fix for mapbox-gl on client side
    if (!isServer) {
      config.resolve.alias = {
        ...config.resolve.alias,
        'mapbox-gl': 'mapbox-gl/dist/mapbox-gl.js',
      };
    }
    return config;
  },
};

module.exports = nextConfig;
