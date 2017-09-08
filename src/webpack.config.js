// webpack.config.js
var htmlWebpackPlugin = require('html-webpack-plugin');
var webpack = require("webpack");

//var lang = require('highlight.js-async-webpack/src/file.lang.hljs.js');
//var _entry= {
//    back_end: './editor.js', // Original entrance
//    vue: ['vue']
//};
//for (var i = 0; i < lang.length; i++) {
//    _entry[lang[i]] = ['mavon-editor/dist/js/' + lang[i] + '.js']
//}

module.exports = {
  // entry point of our application
  entry: './fileuploader.js',
  // where to place the compiled bundle
  output: {
    path: '../js/',
    publicPath: '/static/js/',
    filename: 'fileuploader.min.js'
  },
  module: {
    // `loaders` is an array of loaders to use.
    // here we are only configuring vue-loader
    loaders: [
      {
        test: /\.vue$/, // a regex for matching all files that end in `.vue`
        loader: 'vue-loader'   // loader to use for matched files
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/
      },
      {
      test: /\.css$/,
      loader: "style-loader!css-loader!sass"
      }, {
        test: /\.(png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot)$/,
        loader: 'file-loader?outputPath=../img/search/&publicPath=../img/search/'
      }
    ],

  },
vue: {
  loaders: {
    scss: 'style!css!sass'
  }
},
  resolve: {
    alias: {
      'vue$': 'vue/dist/vue.common.js'
    }
  },
  plugins: [
    new htmlWebpackPlugin({
      inject: false,
      hash: true,
      filename: '../templates/index.html',
      template: '../templates/index.webpack'
    }),
    //new webpack.optimize.DedupePlugin(),
    //new webpack.optimize.UglifyJsPlugin({minimize: true})
  ]

}
