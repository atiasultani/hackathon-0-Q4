/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
  },
  env: {
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000',
  },
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: `${process.env.BACKEND_URL || 'http://localhost:8000'}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;