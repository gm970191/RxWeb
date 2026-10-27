module.exports = {
  publicPath: './',
  assetsDir: 'uploads/img',
  chainWebpack: config => {
    config.module
      .rule('images')
      .use('url-loader')
      .loader('url-loader')
      .tap(options => {
        options.name = '[name].[ext]';
        options.outputPath = 'uploads/img/';
        options.publicPath = '/uploads/img/';
        return options;
      });
  }
};