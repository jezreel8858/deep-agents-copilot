import nextConfig from "eslint-config-next";

// eslint-config-next@16+ ja exporta configuracao Flat Config nativa (array);
// FlatCompat/next/core-web-vitals (padrao legado pre-16) causava
// "Converting circular structure to JSON" ao combinar eslint-plugin-react
// via ponte de compatibilidade com ESLint 9 flat config.
const eslintConfig = [...nextConfig];

export default eslintConfig;

