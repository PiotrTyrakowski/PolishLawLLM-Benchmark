import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  reactCompiler: true,
  // cacheComponents disabled due to known issues with dynamic routes
  // See: https://github.com/vercel/next.js/issues/85240
  // Re-enable when fixed in a future Next.js release
  cacheComponents: false,
};

export default nextConfig;
