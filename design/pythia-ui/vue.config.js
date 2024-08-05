const webpack = require("webpack");

module.exports = {
  runtimeCompiler: true,

  devServer: {
    port: process.env.DEV_SERVER_PORT || 8082,
    proxy: {
      "/api": {
        target: "http://localhost:8018/",
        changeOrigin: true,
        ws: true,
      },
      "/static/": {
        target: "http://localhost:8018/",
        changeOrigin: true,
        ws: true,
      },
    },
  },

  filenameHashing: true,
  outputDir: "../../apps/core/static/",
  assetsDir: "",
  publicPath: "/",
  lintOnSave: false, // this also fixes build crashing in gitlab CI because of compile errors

  pluginOptions: {
    i18n: {
      locale: "cs",
      fallbackLocale: "en",
      localeDir: "locales",
      enableInSFC: true,
    },
  },

  chainWebpack: (config) => {
    config.module
      .rule("i18n")
      .resourceQuery(/blockType=i18n/)
      .type("javascript/auto")
      .use("i18n")
      .loader("@kazupon/vue-i18n-loader")
      .end()
      .use("yaml")
      .loader("yaml-loader")
      .end();
  },
};
