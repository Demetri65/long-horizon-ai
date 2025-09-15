/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  trailingSlash: true,
  transpilePackages: ["geist"],
};

module.exports = nextConfig;
