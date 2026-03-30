import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  devIndicators: false,
  output: 'standalone',
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_DEFAULT_ENDPOINT || 'http://localhost:8000';
    return [
      {
        source: '/media/:path*',
        destination: `${apiUrl}/media/:path*`,
      },
      {
        source: '/videos-media/:path*',
        destination: `${apiUrl}/videos-media/:path*`,
      },
    ]
  },
}

export default nextConfig
